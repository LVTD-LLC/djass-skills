# Changelog

## 0.2.0 (2026-10-01)

- The skill now interviews the user about the tech stack (payments, analytics, email, storage, AI, deploy target, and the rest) and states what is fixed in every Djass project before it discovers options or calls any tool. It never infers optional integrations from the app idea.
- Homebrew is the preferred CLI install: `brew install LVTD-LLC/tap/djass`. `install.sh` uses it when available.

## 0.1.0 (2026-10-01)

- Initial release: Djass plugin and `djass` skill for Claude Code, Codex, Cursor, OpenClaw, OpenCode and any Agent Skills client.
- Bundles the hosted Djass MCP connection (`https://djass.dev/mcp`, bearer auth from `DJASS_API_KEY`).
- Skill covers the `djass` CLI, the MCP tools, the Projects API fallback, generator option selection, and post-generation steps.
