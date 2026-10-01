# AGENTS.md

This repository packages the Djass skill and MCP connection so every major coding-agent harness can install it. There is no server code here, only manifests, Markdown, and small validation scripts.

## Rules

- `plugins/djass/skills/djass/SKILL.md` is the product. Keep it under 200 lines, concrete, and in sync with the real Djass contracts in `LVTD-LLC/djass`: hosted MCP tools in `apps/mcp/hosted.py`, the CLI in `cli/`, the API in `apps/api/`, and the generator catalog in `apps/core/generator_options.py`. When Djass changes an interface, update `SKILL.md` and the matching file under `references/` in the same change.
- Every manifest carries the same `name` (`djass`) and the same `version`. Bump the version everywhere at once: the three manifests under `plugins/djass/`, `integrations/openclaw/djass/plugin.json`, the entry in `.claude-plugin/marketplace.json`, `metadata.version` in `SKILL.md`, and `CHANGELOG.md`. `scripts/validate.py` fails on drift.
- The OpenClaw bundle holds a copy of the skill, not a symlink; symlinks and paths escaping the plugin break when clients archive or cache a subdirectory. Run `python3 scripts/sync.py` after editing the skill. CI rejects copy drift.
- One secret, one name: `DJASS_API_KEY`. Claude Code and Cursor expand `${DJASS_API_KEY}` in `.mcp.json`; Codex uses `bearer_token_env_var`; OpenCode uses `{env:DJASS_API_KEY}`; VS Code uses a masked input. Never commit a real key, and never add a config that puts the key in a URL.
- Keep the plugin directory valid in all formats. Do not add components only one harness understands unless they are harmless to the others (a `hooks/` directory, for example, means different things to Claude Code and Codex).
- Djass is a managed hosted product. Do not add self-hosting or local-stdio MCP instructions here; the only local-stdio path is for developing Djass itself and is documented in that repo.

## Checks

Run before committing:

```bash
make validate                                   # manifests, MCP configs, examples, skill contract, sync, links, secrets
make sync && git diff --exit-code               # OpenClaw copy is current
bash -n install.sh                              # and shellcheck install.sh if installed
claude plugin validate .                        # marketplace
claude plugin validate ./plugins/djass          # plugin manifest, skill frontmatter, MCP entries
codex plugin marketplace add . && codex plugin list | grep djass && codex plugin marketplace remove djass-skills
```

To try the plugin live in Claude Code without installing: `claude --plugin-dir ./plugins/djass`, then `/djass:djass`. For Codex: `codex plugin marketplace add .` from the repo root, then `/plugins` in a session.

A live smoke test needs a real key in the environment: `djass options` (public) then `djass projects list --limit 1`. Never paste the key into a transcript.

## Git

Commit to `main`. Push to `LVTD-LLC/djass-skills`. Tag releases `v<version>` when the skill or manifests change materially.
