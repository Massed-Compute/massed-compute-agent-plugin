---
name: mc-cost-control
description: Use when the user wants to review spend, compute hourly burn rate, or audit running instances on Massed Compute. Synthesizes instance list with product pricing and billing config to produce cost reports and runway estimates. Does not terminate; pair with mc-safe-terminate for cleanup.
type: skill
---

# mc-cost-control

## When to use this skill

Trigger this skill when the user asks any variant of "what am I spending right now," "list my running instances and their cost," "how long until my next recharge fires," "what's my hourly burn rate," or "find idle instances I might want to shut down." It's also appropriate when the user wants a fleet snapshot before making capacity decisions, or when they're investigating an unexpected charge and need to map current usage to dollars.

Do not use this skill when the user wants to actually terminate instances. The job here is read-only synthesis: instance state plus pricing plus billing config rolled into a report. Cleanup belongs in `mc-safe-terminate`, which handles the destructive path with its own confirmation flow. If the user transitions from "what's running" to "shut these down," hand off rather than acting.

## MCP tools used

- `instances_list`
- `gpu_inventory_list` (for per-SKU pricing lookup)
- `account_billing`

Call each with **empty arguments `{}`** unless the live tool schema lists required fields. Do not invent filters, flags, or optional properties — unknown fields return `-32602`.

## The burn-rate procedure

1. Call `instances_list` to retrieve all running instances with their `product_name`, `created`/`launched_at`, and `region`.
2. Call `gpu_inventory_list` to retrieve product pricing for each `product_name` referenced by an instance.
3. Join the two responses: for each instance, look up its product's `price_cents_per_hour` (or equivalent — verify the exact field name from the live response, since the inventory schema may use a different key). Convert to dollars by dividing cents by 100. The result is the per-instance hourly cost in dollars.
4. Sum the per-instance hourly costs to produce the fleet `$/hr` burn rate. This is the headline number for the report.

Keep the join keyed on `product_name`. If a running instance references a product that does not appear in the inventory response, surface that as a warning in the report rather than silently dropping it from the burn-rate sum — it usually means the SKU was retired but instances are still active, and the user should know. In that case, the instance still incurs charges at whatever rate it was launched at; the lack of a current inventory entry doesn't make it free. Note the unknown rate explicitly in the report row and continue.

Cache the `gpu_inventory_list` response for the duration of a single report — there's no point calling it once per instance when most fleets cluster on two or three SKUs. One call covers all of them.

## Long-running detection

After computing per-instance hourly rates, scan launch timestamps and flag two cohorts: instances launched more than 24 hours ago, and separately those launched more than 7 days ago. For each flagged instance, compute accumulated cost as `(now - launched_at) hours × hourly_rate`. Surface both cohorts in the report so the user can decide whether the long-running state is intentional. Many users have legitimate multi-day training jobs.

The 24-hour and 7-day thresholds are heuristics, not rules. Do not recommend termination — just flag. The user is in the best position to know whether a 5-day-old instance is a forgotten dev box or a checkpoint-laden training run that's two epochs from done. The skill's job is to make the cost of leaving it running visible, not to make the call. Phrase the long-running summary as a count plus accumulated cost ("2 instances >24h, $147 accumulated"), not as a recommendation.

## Recharge runway

Call `account_billing` to retrieve the recharge configuration. The response includes `recharge_amount` (the dollar amount added per recharge) and `recharge_threshold` (the balance level that triggers the next recharge). Combine these with the fleet burn rate to estimate hours until the next recharge fires:

```
runway_hours = (current_balance + recharge_amount - recharge_threshold) / fleet_burn_rate
```

Express this calculation explicitly in the report. It's a simplification: it assumes no other charges land between now and the next recharge, and it answers the specific question "how many hours of current burn until the next automatic top-up." If the user's balance is close to the threshold, runway can collapse to single-digit hours, which is usually the answer they're looking for when they ask the question in the first place.

Important caveat: `account_billing` returns recharge configuration, not the current account balance directly. The runway estimate is therefore best-effort. If the user wants an authoritative balance figure or a recharge history, point them at the billing UI rather than fabricating a number from incomplete data.

## Standard report format

When asked for a fleet snapshot, produce output shaped like the following:

```markdown
## Massed Compute fleet snapshot

**Burn rate**: $X.XX/hr · **Runway to next recharge**: Y hours

| UUID | Name | GPU | Region | Uptime | $/hr | Accumulated cost |
|---|---|---|---|---|---|---|
| … | … | 1x H100 | us-central-3 | 28h 14m | 2.72 | 76.83 |

**Long-running**: 2 instances >24h, 0 instances >7d.

**Cleanup candidates** (>24h with no detectable activity): see `mc-safe-terminate`.
```

The headline line is intentionally compact — burn rate and runway are the two numbers the user almost always wants first. The table holds the per-instance breakdown. The trailing notes flag long-running instances and point at the cleanup skill without taking action.

When the fleet is large (more than ~15 instances), sort the table by `$/hr` descending so the highest-cost instances appear at the top. Most users want to scan from most expensive to least when deciding what to investigate. For very large fleets, consider truncating to the top 20 rows and summarizing the tail ("...and 47 more instances at <$0.50/hr each, $X.XX/hr combined") rather than dumping a 200-row table into chat.

## What this skill does NOT do

This skill does not call `instances_terminate` under any circumstance. If the user pivots from "show me what's running" to "kill these," the model should hand off to `mc-safe-terminate` rather than acting from inside this skill. The reasoning is structural: separating "what's running and how much it costs" from "kill it" forces an explicit decision step between the two, and makes destructive action meaningfully harder to do by accident. A user who reads a fleet snapshot and decides to clean up is making a different choice than a user who said "spin down everything" in one breath, and the skill boundary preserves that distinction.

## Pitfalls

- **Pricing in `gpu_inventory_list` is dollars per hour, not per minute or per second.** Don't accidentally divide by 60 or 3600 when normalizing — the field already represents an hourly rate (after cents-to-dollars conversion).
- **`instances_list` may not include a `launched_at` field directly.** If only `created` is available in the response, use that as a proxy for uptime. Verify the exact field name from a live response before computing durations; the schema is the source of truth, not assumptions.
- **`account_billing` doesn't tell you the current balance directly.** It returns recharge config (`recharge_amount`, `recharge_threshold`). Estimating runway is best-effort. For an exact balance, point the user at the billing UI rather than guessing.
- **Cost rounding.** Hourly rates are denominated in dollars and cents. Don't quote four decimal places — one ($2.7/hr) or two ($2.72/hr) is enough. Over-precision suggests a confidence the underlying data doesn't support.
- **Time-zone math.** When converting "uptime" from `launched_at` (or `created`) to a human-readable duration, both timestamps must be in UTC. Mixing local time silently produces wrong durations, and the error compounds for instances that crossed a DST boundary.

## See also

- `mc-safe-terminate` — for actually cleaning up the candidates this skill flags
- Billing UI: https://vm.massedcompute.com/billing — authoritative balance and recharge history
