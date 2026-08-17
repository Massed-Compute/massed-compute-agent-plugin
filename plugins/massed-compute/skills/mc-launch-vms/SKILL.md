---
name: mc-launch-vms
description: Use when the user wants to launch one or more VM instances on Massed Compute via the MCP. Orchestrates pre-flight checks (billing, token, SSH key), multi-instance naming and launch loops, coupon application, and post-launch SSH connection.
type: skill
---

# mc-launch-vms

## When to use this skill

Use this skill when the user has decided what to launch and wants the VMs running. That includes single-VM launches ("spin up one H100 in NV1"), batched launches ("give me four A100x4 boxes named worker-1 through worker-4"), and coupon-backed launches ("apply coupon SUMMER25"). The skill assumes the user already knows the SKU, image, and region — or is willing to accept `region: "any"`.

Do not use this skill while the user is still researching what to launch. If the conversation is in "which GPU should I pick?" or "what's cheapest for inference at 70B?" territory, defer to `mc-pick-gpu` and let it return a concrete `productName` first. Coming back here once the SKU is known.

## MCP tools used

- `account_token_validation`
- `account_billing`
- `gpu_inventory_list`
- `images_list`
- `ssh_keys_list`, `ssh_keys_create`
- `instances_launch`
- `instances_list`, `instances_get`
- `coupon_accepted_products` (only when a coupon is mentioned)

## Pre-flight checklist

Run all three checks before any `instances_launch` call. None of them are skippable; each one corresponds to a launch failure mode that the API will not catch in advance.

1. **Auth valid** — call `account_token_validation`. If the call fails or returns invalid, surface the error verbatim and stop. There is no point continuing if the plugin OAuth grant (or fallback Bearer) cannot authenticate; every downstream call will return 401 and the user will be staring at a launch loop that never starts.

2. **Billing configured** — call `account_billing`. Both `recharge_amount` and `recharge_threshold` must be set to non-null, non-zero values. If either is missing, tell the user the launch will return 402 (payment required), point them at the billing UI in their account dashboard, and stop. Do not attempt the launch "to see what happens" — the 402 is deterministic and burns a request.

3. **SSH key present** — call `ssh_keys_list`. If the list is empty, offer to create one via `ssh_keys_create` and pause for the user's public key. Without a key attached at launch time (and without a startup `command` that opens its own access path), the VM will boot but the user has no way in. The MCP redacts the cleartext password by design, so SSH key auth is the practical entry route.

## Picking the GPU

If the user has not specified a SKU yet, defer to `mc-pick-gpu`. Once a `productName` is selected, validate it against `gpu_inventory_list` and confirm the requested region has available capacity. If the user asked for a region that is currently empty, list the regions that do have capacity for that SKU and let them choose between switching region, accepting `"any"`, or waiting. Do not paper over a capacity miss by silently routing them elsewhere.

## Picking the image

Call `images_list` and resolve the user's image by name. The MCP returns an array of image records with both name and ID; match on the user's string and grab the corresponding ID for the launch call. If the user mentioned an image that is not in the list (an old one, a typo, or wishful thinking), suggest the closest match by name. There is a contract divergence to be aware of internally: the MCP `images_list` returns image IDs and `instances_launch` takes `imageId` (integer), while the underlying REST API uses `os_image_name` (string) on its launch endpoint. The MCP and REST contracts diverge here. Do not surface the field-name mismatch to the user — just resolve their image name to its `imageId` before calling launch and move on.

## Single-launch flow

1. Gather the launch parameters: `imageId` (resolved from name via `images_list`), `productName` (the SKU), `regionName` (`"any"` is acceptable if the user has no preference), `instanceName` (optional — if omitted and only one VM is being launched, let the backend assign one), `sshKeys` (default to all keys returned by `ssh_keys_list` unless the user specified a subset), `command` (optional startup command), and `coupon` (optional). Avoid asking for these fields one at a time; pull what you can from context and only prompt for the gaps.

2. Present a single batched summary to the user before doing anything destructive. Include: GPU SKU and count, region, image name, instance name (if specified), SSH keys to be attached (by label, not full key material), and the coupon code if any. Ask one yes/no confirmation. Avoid drip-feeding confirmations across multiple turns.

3. Call `instances_launch` once with the gathered arguments. Capture the returned instance UUID.

4. Poll `instances_get` against that UUID until `status: running`, with a 5-minute upper bound. The MCP currently does not surface intermediate launch progress; the instance moves from `pending` to `running` when the host has provisioned it. If it stays `pending` past the 5-minute window, surface that fact and stop polling. Do not retry the launch — the original instance is still in flight, and a retry will create a duplicate.

5. Output the SSH connect string (`user@ip` or equivalent from the instance payload). Prefer SSH key auth. Do **not** fetch, display, or paste cleartext VM passwords into the chat — MCP redacts them on purpose. If the user needs console password access, tell them to use the Massed Compute dashboard or their own REST client outside the conversation; never pull passwords into this chat.

## Multi-launch flow (N>1)

The procedure depends on whether `instances_launch` accepts a `quantity` parameter on the live MCP server. Check the input schema before deciding which branch to take.

**Current state at writing**: `instances_launch` does not expose `quantity`. The skill loops N sequential `instances_launch` calls. Naming convention: `{base}-1` through `{base}-N`, where `{base}` is the user's chosen base name. If no base name was given, auto-generate one from the SKU (e.g., `h100x8-1`, `h100x8-2`, ...). Get a single up-front confirmation covering the entire batch — the GPU, the count, the region, the image, the SSH keys, and the naming scheme. Never ask per-instance "are you sure?" prompts; that turns a four-VM launch into eight conversational turns.

**Partial failure policy**: if any call in the loop fails, abort the loop immediately. Report which UUIDs succeeded (with their names) and which slot failed. Let the user decide whether to terminate the partial set or keep what landed. Do not retry the failed slot automatically — the failure could be a transient capacity miss, a billing limit being hit mid-batch, or an image incompatibility, and silent retry can mask all three. The user should make the next call.

**Future state**: if a future MCP build exposes `quantity` on `instances_launch` (the input schema will list it), use it. Set `quantity: N` and call once. Naming will be auto-generated by the backend; the user gets one confirmation, one MCP call, and one batch result. Drop the loop entirely in that case — the loop exists only as a workaround for a missing schema field.

## Coupon-aware launches

When the user provides a coupon code, validate it against the chosen SKU before launching. The launch call itself will accept any string in the coupon field; an unaccepted coupon does not error, it just gets ignored, and the user pays full price without realizing the discount did not apply.

1. Call `coupon_accepted_products` with the coupon code. The response lists the products the coupon applies to.
2. Confirm the chosen `productName` appears in the accepted list. If it does not, tell the user — they can switch to an accepted product, drop the coupon, or pick a different coupon. Surface this before calling `instances_launch`. Do not launch silently with an inapplicable coupon.

## Post-launch wiring

After `instances_launch` returns success:

- Poll `instances_get` until the instance reports `status: running`. Cap the wait at 5 minutes; if it exceeds that, surface the still-pending status and let the user decide whether to keep waiting or investigate.
- Surface the SSH connect string. The instance object includes a connect-string field (verify the exact field name from the live response shape — the MCP does not promise stability of every field). Format it as a single copy-pasteable line so the user can drop it straight into a terminal.
- Restate password hygiene: MCP hides cleartext VM passwords so they never enter the chat. Do not work around redaction. Point users to the Massed Compute dashboard for console credentials if SSH keys are not enough.

## Pitfalls

- **`region: "any"` lands you in whichever DC has capacity.** That may not be the user's geographically preferred region. If latency to the VM matters — interactive SSH from Europe, low-latency inference fronting a US-East user base — pick a specific region from `gpu_inventory_list`'s availability data instead of letting the scheduler decide.
- **No SSH key + no startup command = unreachable VM.** The launch will succeed, the user will be billed, and they will not be able to log in. The pre-flight rejects this case when no key exists in the account at all. The model should also reject it if the user explicitly asks to launch with `sshKeys: []` and provides no `command` to bootstrap an alternate access path. Confirm intent before proceeding.
- **Recharge threshold not set returns 402.** This is the most common launch failure for new accounts. The pre-flight catches it; do not skip the pre-flight to "save a step." A 402 response is not a friendly error — it does not auto-prompt the user to fix billing.
- **Image incompatibility.** Some images only run on specific GPU form factors (SXM-only images on PCIe SKUs will be rejected, for example). If the launch returns "Product does not support the VM Image," explain the constraint to the user and suggest a compatible image from `images_list`. Do not retry with the same image — the rejection is deterministic.

## See also

- `mc-pick-gpu` — SKU selection before this skill
- `mc-cost-control` — burn rate after launch
- `mc-safe-terminate` — teardown
- `setup` — plugin OAuth / MCP connect
