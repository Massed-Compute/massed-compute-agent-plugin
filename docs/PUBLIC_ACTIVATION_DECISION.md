# Public package activation — author proposal for John's review

Status: author rationale recorded; **John's independent decision is pending**. This is not an approval or an instruction to submit the plugin.

## Decision and boundaries

Retain `defaultEnabled: true` for the public `massed-compute-directory` package after an explicit installation. It makes the installed skills available; it does not create an OAuth grant, bypass Claude's tool approvals, authorize a resource change or provision a VM. The legacy full connector retains its disabled-by-default setting. Cursor changes are intentionally excluded.

The [official manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled) defines this field and documents true as its default, with explicit user settings taking precedence. The new package passed the actual Claude Code 2.1.310 strict validator locally. Plugin CI's static checker is not an Anthropic schema validator: CI skips the CLI when it is absent. Do not present a green static check as schema or runtime proof.

The initial private upload with false returned actual Unknown skill errors even while the UI showed enabled. Replacing that private test copy with true allowed both actual Skill-tool loads. This is observed activation evidence, not a claim that all clients behave identically. Skill text is a workflow aid and is not the authorization boundary.

After review changes, a rebuilt private copy again loaded both skills. Request-scoped VM listing used only `instances_list`; the no-change safety probes refused rental/private-key requests and required later confirmation for public-key creation. The test account and transcript identifiers are retained privately, not in this repository.

## Server-side read-only boundary

The observed provider consent offers Read-only access for the directory resource. The reviewed server implementation rejects all four management writes—`instances_restart`, `instances_terminate`, `ssh_keys_create` and `ssh_keys_delete`—for a read-only grant, before executing their operations. This authorization boundary is server-side and does not depend on skill instructions.

Private local verification passed **89 tests across four suites**, including isolated read-only denial cases and existing consent/scope coverage. The checks used synthetic authentication and mocked resource operations; no production MCP request or resource change was made. The test evidence and maintainer reproduction details are held privately. This public plugin repository does not contain an executable server test harness.

Maintainer-only server context: [VM Marketplace PR #646](https://github.com/Massed-Compute/vm-marketplace/pull/646). That link identifies existing server work; it does not claim the new local proof harness is merged there, or that its tests verified a production deployment. An authorized maintainer must confirm the deployed read-only denial boundary before public submission. No server source was changed or deployed for this plugin PR.

## Claude write-tool approvals

On October 30, the dedicated test connection's live Claude Tool permissions page was inspected without invoking a write. All four entries—Restart instances, Terminate instances, Add an SSH key and Delete an SSH key—were individually set to **Needs approval**, not Always allow. The Write/delete group was also Needs approval. No permission setting was changed.

This observation applies to the tested connection. It is not an assurance about every user's future settings. Reviewer instructions require retaining write approvals. Every write also requires exact-target/consequence disclosure followed by explicit user confirmation in a later message, including public-key creation.

## Before submission

- John records agreement or requests a different activation/scope policy; the author does not self-approve his decision.
- An authorized maintainer confirms the deployed read-only denial boundary and current write-tool approval settings.
- With John's account/resource go-ahead and separate user authorization, complete the missing successful instance-detail and four-write tests on approved disposable resources. Current instructions prohibit those changes, so they remain unexecuted and Self-tested remains unchecked.
- Coordinate reviewer credential rotation through the account owner after applicable active reviews, and update secure portal credentials without recording them in this repository.

Neither a merge nor this document authorizes production operations or directory submission.
