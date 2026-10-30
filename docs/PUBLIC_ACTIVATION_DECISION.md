# Public package activation — author proposal for John's review

Status: author rationale recorded; **John's independent decision is pending**. This is not an approval or an instruction to submit the plugin.

## Decision and boundaries

Retain `defaultEnabled: true` for the public `massed-compute-directory` package after an explicit installation. It makes the installed skills available; it does not create an OAuth grant, bypass Claude's tool approvals, authorize a resource change or provision a VM. The legacy full connector retains its disabled-by-default setting. Cursor changes are intentionally excluded.

The [official manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference#defaultenabled) defines this field and documents true as its default, with explicit user settings taking precedence. The new package passed the actual Claude Code 2.1.310 strict validator locally. Plugin CI's static checker is not an Anthropic schema validator: CI skips the CLI when it is absent. Do not present a green static check as schema or runtime proof.

The initial private upload with false returned actual Unknown skill errors even while the UI showed enabled. Replacing that private test copy with true allowed both actual Skill-tool loads. This is observed activation evidence, not a claim that all clients behave identically. Skill text is a workflow aid and is not the authorization boundary.

After review changes, a rebuilt private copy again loaded both skills. Request-scoped VM listing used only `instances_list`; the no-change safety probes refused rental/private-key requests and required later confirmation for public-key creation. The test account and transcript identifiers are retained privately, not in this repository.

## Server-side read-only boundary

The provider consent observed during dedicated-account testing offered a Read-only access option for the directory resource. The server stores a read-only consent as a read-only grant and resolves it into the authenticated context. The directory dispatcher checks the authenticated scope before argument validation or tool-handler execution.

All four management writes require full access: `instances_restart`, `instances_terminate`, `ssh_keys_create` and `ssh_keys_delete`. With a read-only grant, the server implementation returns JSON-RPC Forbidden (40300) and does not call the handler. Read-only access is therefore enforced by server code, independently of either skill's prompt text.

Evidence inspected in the VM Marketplace repository at main commit `d1a8b7280f7e87763096a3823615efc262412494`:

- `app/api/oauth/authorize/decision/route.ts`: stores read-only unless write scope was requested and full access explicitly selected; reconciles the persisted grant with consent.
- `app/api/mcp/_lib/resolveAuth.ts`: carries the grant's read-only value into the authenticated context.
- `app/api/mcp/_lib/registry.ts`: marks all four write tools as requiring full access.
- `app/api/mcp/_lib/dispatcher.ts`: rejects insufficient scope before argument processing and handler execution.
- `app/api/mcp/directory/route.ts`: uses the directory surface of this shared handler.

Those authorization files and existing consent/scope tests were compared with the locally tested checkout and matched that main revision. No server source was changed or deployed for this PR.

### Reproducible local proof

`tests/public_directory_readonly.test.ts` adds twelve isolated tests: all four writes are denied before their handlers in both dispatcher protocol modes and at the directory HTTP boundary. Database access is prohibited by mocks, all write adapters are mocked, and only synthetic authentication data is used. It makes no production MCP requests and creates no resources.

An authorized maintainer with the VM Marketplace checkout and its dependencies can reproduce the proof. From that checkout, set `MC_PLUGIN_CHECKOUT` to this plugin repository's absolute path, then run:

```sh
node node_modules/jest/bin/jest.js --runInBand \
  --roots "$PWD" "$MC_PLUGIN_CHECKOUT/tests" \
  --runTestsByPath "$MC_PLUGIN_CHECKOUT/tests/public_directory_readonly.test.ts" \
  "$PWD/__tests__/api/mcp/mcpDirectorySurface.test.ts" \
  "$PWD/__tests__/api/mcp/resolveAuth.test.ts" \
  "$PWD/__tests__/api/oauth/decision.test.ts"
```

The twelve proof cases plus 77 existing consent/scope/directory cases passed locally: **89 tests, four suites**. The proof uses the server checkout's Jest configuration; it is intentionally not part of this plugin's dependency-free CI and does not test a deployed production build. Deployment identity and production denial behavior must be confirmed by an authorized maintainer before public submission. No mutation call was sent to production to manufacture that evidence.

## Claude write-tool approvals

On October 30, the dedicated test connection's live Claude Tool permissions page was inspected without invoking a write. All four entries—Restart instances, Terminate instances, Add an SSH key and Delete an SSH key—were individually set to **Needs approval**, not Always allow. The Write/delete group was also Needs approval. No permission setting was changed.

This observation applies to the tested connection. It is not an assurance about every user's future settings. Reviewer instructions require retaining write approvals. Every write also requires exact-target/consequence disclosure followed by explicit user confirmation in a later message, including public-key creation.

## Before submission

- John records agreement or requests a different activation/scope policy; the author does not self-approve his decision.
- An authorized maintainer confirms the deployed read-only denial boundary and current write-tool approval settings.
- With John's account/resource go-ahead and separate user authorization, complete the missing successful instance-detail and four-write tests on approved disposable resources. Current instructions prohibit those changes, so they remain unexecuted and Self-tested remains unchecked.
- Coordinate reviewer credential rotation through the account owner after applicable active reviews, and update secure portal credentials without recording them in this repository.

Neither a merge nor this document authorizes production operations or directory submission.
