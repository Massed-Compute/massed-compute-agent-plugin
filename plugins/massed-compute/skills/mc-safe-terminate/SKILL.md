---
name: mc-safe-terminate
description: Use before terminating one or more VM instances on Massed Compute. Wraps instances_terminate with required disclosure (UUID, name, GPU, uptime, accumulated cost), explicit user confirmation, and batch-by-filter support. Termination is permanent and stops billing for the affected instances.
type: skill
---

# mc-safe-terminate

## When to use this skill

Invoke this skill whenever the user wants to tear down one or many running VMs. Trigger phrases include "terminate," "stop," "kill," and "shut down." In Massed Compute's model, "stop" effectively means terminate — there is no pause-and-resume, no hibernation, no "off but preserved." If the user says "stop," confirm whether they mean destroy permanently or pause (and explain that pause does not exist) before going further. Always run this skill before calling `instances_terminate`.

## MCP tools used

- `instances_list`, `instances_get`
- `gpu_inventory_list` (for cost computation)
- `instances_terminate`

## The destructive disclosure rule

Before calling `instances_terminate`, surface a full disclosure table covering every UUID in the batch.

The table must use exactly this format:

```markdown
| UUID | Name | Product | Region | Uptime | Accumulated cost |
|---|---|---|---|---|---|
| <full-uuid> | <name or "(unnamed)"> | <e.g. 1x H100> | <region> | <e.g. 4h 22m> | $XX.XX |
```

One row per instance being terminated. No abbreviation, no sampling, no "and 5 more." If the batch is large enough that the table would overwhelm the chat, that is a signal to ask the user to narrow the filter — not to skip the disclosure. Pull names and product/region from `instances_list` or `instances_get`; compute accumulated cost as uptime times the per-hour rate from `gpu_inventory_list` for that product. Show the full UUID, not a prefix. Do not dump unrelated fields (account emails, passwords, SSH key material) into the disclosure table.

## Confirmation discipline

After the disclosure table, require an explicit "yes" before proceeding. Vague affirmatives ("ok," "looks fine," "sure go ahead") count if and only if they unambiguously approve the displayed batch. Ambiguous responses ("seems right," "I think that's correct," "probably") trigger one more clarifying ask, phrased plainly: "To be clear, you want me to terminate all N instances above? Yes or no." One confirmation covers the entire batch in the disclosure table — do not prompt per UUID.

The reason for the strict confirmation gate: this is the only skill in the suite that performs an action with no undo. Recharge runway you can fix; a launched VM you can terminate; a wrong-region SSH key you can replace. A terminated VM and its data are gone. The disclosure table plus the explicit yes is what makes the user's consent informed and recorded in the chat history.

## Vague mass-kill (hard refuse)

Phrases like "kill all my VMs," "terminate everything," "shut them all down," or "nuke the fleet" **without naming UUIDs or an unambiguous filter** are not confirmation.

**Do not call `instances_terminate` at all on that turn.** Reply that you need either (a) a resolved disclosure table of specific instances, or (b) a narrow filter you will resolve via `instances_list` first. Saying "I cannot" in text while still invoking terminate is a failure — zero tool calls until disclosure + explicit yes.

This gate exists because weak tool-calling models sometimes emit a terminate call and a refusal sentence in the same turn. Skills must make the refuse path tool-silent.

## Batch-by-filter

Natural-language filters like "terminate all idle >24h" or "terminate all my A6000s in us-central-3" need to be resolved deterministically before any destructive call.

1. Parse the filter into machinable terms (uptime threshold, GPU type, region, name pattern).
2. Call `instances_list`, apply the filter client-side, get a UUID set.
3. Show the disclosure table with the resolved set. Include the full count in the heading: "**Termination candidates: 4 instances**" so the user sees scope before reading rows.
4. Get one confirmation covering the whole batch.
5. Call `instances_terminate` with the full UUID list. The MCP supports batch terminate via the `instanceUuids` array argument — one call, all UUIDs.

If the resolved set is empty, say so and stop; do not silently widen the filter. If the resolved set looks larger than what the user described ("all my A6000s" pulled 19 rows), call that out in the heading and let the user trim before confirming.

## What termination actually does

- Billing stops for the affected instances at termination time.
- Cleartext passwords stored on the instance are gone forever — once terminated, the REST API can no longer return them either.
- Attached storage on the VM is permanently deleted. There is no undo, no snapshot, no recycle bin.
- **SSH keys persist deliberately.** They live on the account, not the VM. Don't recommend deleting SSH keys as part of cleanup — they are useful for relaunches and cost nothing to keep on the account.

## MCP argument hygiene

Call `instances_terminate` only with `instanceUuids` (array of full UUID strings). Do not invent alternate field names (`uuids`, `ids`, `instance_ids`) or extra properties — the MCP rejects unknown fields with `-32602`.

## Pitfalls

- **Similar names trip the wrong UUID.** Always show full UUID (not a prefix) and the name in the disclosure table so the user can disambiguate. Never collapse to "the H100" — that may be ambiguous if they have multiple.
- **Filter typos.** "All A6000s" can match more than the user intends if their fleet is large or mixed. Show the full count and full disclosure before confirmation; do not silently expand the scope.
- **Don't soften the language.** "I'll terminate these" is correct; "I'll close these" or "I'll stop these" is not — termination is destructive and permanent, and the user's confirmation is informed only if the language is accurate.
- **No retroactive cost recovery.** If the user terminates a VM they didn't intend to, the accumulated cost is real and not refundable. The disclosure table's "Accumulated cost" column makes this visible before the fact, not after.
- **Idempotency.** `instances_terminate` is idempotent server-side — calling it twice on the same UUID is safe — but a confused chat session can still terminate the wrong UUID. Idempotency does not save you from "wrong target."

## See also

- [`mc-cost-control`](mc-cost-control.md) — produces the cleanup-candidate list this skill acts on
- [`mc-launch-vms`](mc-launch-vms.md) — the SSH keys you keep are immediately reusable here
