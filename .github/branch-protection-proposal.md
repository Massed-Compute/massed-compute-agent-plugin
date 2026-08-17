# Branch protection proposal (not applied)

Inspected 2026-08-17: no classic branch protection rules (`nodes: []`), no repository rulesets (`[]`). REST protection endpoint returned 503.
Visibility: **private**. Do not change visibility in this PR.

Apply the same `main-change-control` ruleset described in the docs repo file of the same name, with required checks:

- `secrets`
- `validate`
- `json-validate`
- `secrets-scan`
- `home-path-scan`
- `plugin-validate`

UI: **Settings → Rules → Rulesets → New branch ruleset**.
Required PR + 1 non-author approval + dismiss stale reviews + require last push approval + conversations resolved + up-to-date branch + block force push + block deletion + empty bypass list + apply to administrators if policy allows.

Do not run the Rulesets API without explicit admin approval.
