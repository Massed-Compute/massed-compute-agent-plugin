# Public package activation — proposal and release requirements

This document records the proposed activation behavior and its supporting evidence. Independent activation and release review is required before submission; current review decisions belong in the PR record. This document is not an approval or an instruction to submit the plugin.

## Decision and boundaries

Retain `defaultEnabled: true` for the public `massed-compute-directory` package after an explicit installation. It makes the installed skills available; it does not create an OAuth grant, bypass Claude's tool approvals, authorize a resource change or provision a VM. The legacy full connector retains its disabled-by-default setting. Cursor changes are intentionally excluded.

The [official manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled) defines this field and documents true as its default, with explicit user settings taking precedence. The new package passed the actual Claude Code 2.1.310 strict validator locally. Plugin CI's static checker is not an Anthropic schema validator: CI skips the CLI when it is absent. Do not present a green static check as schema or runtime proof.

The initial private upload with false returned actual Unknown skill errors even while the UI showed enabled. Replacing that private test copy with true allowed both actual Skill-tool loads. This is observed activation evidence, not a claim that all clients behave identically. Skill text is a workflow aid and is not the authorization boundary.

An earlier post-review private rebuild again loaded both skills. Request-scoped VM listing used only `instances_list`; the no-change safety probes refused rental/private-key requests and required later confirmation for public-key creation. These results predate the latest multi-VM workflow changes. The test account and transcript identifiers are retained privately, not in this repository.

On November 2, the revised package was rebuilt and replaced in the private Claude test installation. The actual `mc-safe-changes` skill loaded. A no-change simulation with fictional duplicate-name VMs stopped for UUID selection, enumerated the multi-VM count and identifiers, and required operation-plus-count or exact-UUID confirmation. A separate bare "yes" was rejected without any account calls. These simulated workflow checks do not establish successful lifecycle operations or server enforcement.

The subsequent multi-key deletion revision was rebuilt and privately replaced too. The actual safety skill rejected ambiguous fictional key labels and a separate bare "yes" for a two-key deletion. It required exact key IDs/labels, a total count and later delete-plus-count or exact-ID confirmation. No account calls were made. The VM guard was unchanged by that revision; these remain no-change simulations rather than positive write tests.

## Server-side read-only boundary

The previously observed provider consent offers Read-only access for the directory resource. Current fetched server source shows that read-only is preselected only when the authorization request excludes `mcp:write`. If write access is requested, the Read-only access checkbox starts unchecked and the user may select it to narrow the grant. An absent or blank scope defaults to both read and write. This describes source behavior, not a fresh observation of the deployed consent UI or the scope requested by a particular client.

The reviewed server implementation rejects all four management writes—`instances_restart`, `instances_terminate`, `ssh_keys_create` and `ssh_keys_delete`—for a read-only grant, before executing their operations. This authorization boundary is server-side and does not depend on skill instructions. A maintainer must still verify the deployed boundary before submission.

Private local verification passed **89 tests across four suites**, including isolated read-only denial cases and existing consent/scope coverage. The checks used synthetic authentication and mocked resource operations; no production MCP request or resource change was made. The test evidence and maintainer reproduction details are held privately. This public plugin repository does not contain an executable server test harness.

Maintainer-only server context: [VM Marketplace PR #646](https://github.com/Massed-Compute/vm-marketplace/pull/646). That link identifies existing server work; it does not claim the new local proof harness is merged there, or that its tests verified a production deployment. An authorized maintainer must confirm the deployed read-only denial boundary before public submission. No server source was changed or deployed for this plugin PR.

## Claude write-tool approvals

On October 30, the dedicated test connection's live Claude Tool permissions page was inspected without invoking a write. All four entries—Restart instances, Terminate instances, Add an SSH key and Delete an SSH key—were individually set to **Needs approval**, not Always allow. The Write/delete group was also Needs approval. No permission setting was changed.

This observation applies to the tested connection. It is not an assurance about every user's future settings. Reviewer instructions require retaining write approvals. Every write also requires exact-target/consequence disclosure followed by explicit user confirmation in a later message, including public-key creation.

## Before submission

- Obtain independent review of the activation choice and release readiness; the author does not self-approve the proposal.
- An authorized maintainer confirms the deployed read-only denial boundary and current write-tool approval settings.
- With the account/resource owner's go-ahead and separate user authorization, complete the missing successful instance-detail and four-write tests on approved disposable resources. Current instructions prohibit those changes, so they remain unexecuted and Self-tested remains unchecked.
- Coordinate reviewer credential rotation through the account owner after applicable active reviews, and update secure portal credentials without recording them in this repository.
- While reviewer access is active, the account owner must verify the reviewer password is unique and the reviewer account has no card or credit. These account conditions have not been verified by this plugin's author.

Neither a merge nor this document authorizes production operations or directory submission.
