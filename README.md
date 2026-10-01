# djass-skills

Plugin and skill for using [Djass](https://djass.dev) from coding-agent harnesses: Claude Code, OpenAI Codex, Cursor, OpenClaw, OpenCode, and anything else that reads Agent Skills.

Djass generates production-ready Django SaaS repositories from [`django-saas-starter`](https://github.com/LVTD-LLC/django-saas-starter). This plugin teaches your agent to pick generator options with you, queue a generation, and land the finished repo in your workspace. It bundles:

- the `djass` skill (`plugins/djass/skills/djass/SKILL.md`) with CLI, API, and option references;
- the hosted Djass MCP connection (`https://djass.dev/mcp`, authenticated with your `DJASS_API_KEY`);
- instructions for installing the `djass` CLI, which the skill prefers because it downloads and safely extracts the repo in one command.

| Format | Manifest | Read by |
|---|---|---|
| Claude Code plugin + marketplace | `plugins/djass/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | Claude Code |
| Codex plugin + marketplace | `plugins/djass/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | Codex CLI and app |
| Cursor plugin + marketplace | `plugins/djass/.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json` | Cursor |
| [Agent Plugins 1.0](https://agent-plugins.org) bundle | `integrations/openclaw/djass/plugin.json` + `mcp.json` | OpenClaw and other portable-plugin clients |
| [Agent Skills](https://agentskills.io) | `plugins/djass/skills/djass/SKILL.md` | every harness above, plus OpenCode and any skills-aware agent |

## Before you start: the API key

Every path needs a Djass API key. Copy your Agent API key from [Account settings](https://djass.dev/settings) (a scoped project key needs `projects:create` and `projects:read`), then export it in the environment that launches your agent:

```bash
export DJASS_API_KEY="replace-with-your-key"
```

The CLI, the MCP connection, and the API all read this one variable. GUI clients and gateways may not inherit your shell; use their private environment or secret settings and restart them. Never paste the key into chat, a command argument, or a committed file.

## If you are an AI agent

1. Install this plugin into your harness using the matching section below, or run `./install.sh` from a clone of this repo, which installs the `djass` CLI and links the skill into `~/.agents/skills/` and `~/.claude/skills/`.
2. Make sure `DJASS_API_KEY` is set. Check with `[ -n "$DJASS_API_KEY" ]`; never print it. Ask the user if it is missing.
3. Read [`plugins/djass/skills/djass/SKILL.md`](plugins/djass/skills/djass/SKILL.md) and follow it.

## Install per harness

### Claude Code

```bash
claude plugin marketplace add LVTD-LLC/djass-skills
claude plugin install djass@djass-skills
```

Or for one session without installing: `claude --plugin-dir /path/to/djass-skills/plugins/djass`. The skill is available as `/djass:djass` and Claude also uses it on its own when you ask for a new Django project. Run `/mcp` to confirm the `djass` server connected; a `401` means `DJASS_API_KEY` was not in Claude's environment when it started.

### OpenAI Codex

```bash
codex plugin marketplace add LVTD-LLC/djass-skills
codex plugin add djass@djass-skills
```

Or open `/plugins` in a Codex session and install **Djass**. The bundled MCP connection reads `DJASS_API_KEY` through `bearer_token_env_var`. Codex also reads skills from `~/.agents/skills/`, so `./install.sh` works as an alternative; if you go that way and want MCP too, merge [`examples/codex.toml`](examples/codex.toml) into `~/.codex/config.toml`.

### Cursor

Open **Customize**, choose **From GitHub Repository**, and enter `LVTD-LLC/djass-skills`; the repo carries the `.cursor-plugin/marketplace.json` Cursor expects, and the plugin declares a `DJASS_API_KEY` variable for you to fill in privately. Or copy `plugins/djass` to `~/.cursor/plugins/local/djass` and run **Developer: Reload Window**.

Without the plugin system: `./install.sh` links the skill (Cursor reads `~/.agents/skills/`), and [`examples/cursor-mcp.json`](examples/cursor-mcp.json) is the entry to merge into `.cursor/mcp.json`.

### OpenClaw

From a clone of this repo:

```bash
openclaw plugins install ./integrations/openclaw/djass
openclaw plugins inspect djass --runtime
```

The bundle is an Agent Plugins 1.0 package with an explicit Streamable HTTP MCP entry. Provide `DJASS_API_KEY` to the gateway or agent runtime, not only the install shell. If your OpenClaw build supports installing marketplaces from git, `openclaw plugins install git:github.com/LVTD-LLC/djass-skills@main` should find the same plugin; the local path form is the one we validate.

### OpenCode

OpenCode has no plugin manifest for skills; it reads `~/.agents/skills/` and `.agents/skills/` in the project. Either:

```bash
git clone https://github.com/LVTD-LLC/djass-skills ~/.local/share/djass-skills
~/.local/share/djass-skills/install.sh
```

or, for one project only, copy `plugins/djass/skills/djass` to `<project>/.agents/skills/djass`. For MCP, merge [`examples/opencode.json`](examples/opencode.json) into `opencode.json` (it uses `{env:DJASS_API_KEY}` and turns OAuth discovery off), then run `opencode mcp list`.

### VS Code and other MCP clients

[`examples/vscode-mcp.json`](examples/vscode-mcp.json) prompts for the key with a masked input; merge it into `.vscode/mcp.json`. Any other client: endpoint `https://djass.dev/mcp`, transport Streamable HTTP, header `Authorization: Bearer <your key>` set through private client configuration, plus the skill directory copied to wherever that client looks for skills.

### Any other agent

Anything that implements [Agent Skills](https://agentskills.io) can use `plugins/djass/skills/djass/`. Copy or symlink that directory to wherever the agent looks for skills; `~/.agents/skills/djass` is the emerging convention. The skill works without MCP: it installs and drives the `djass` CLI.

## Try it

> Use Djass to generate a new Django SaaS project for an invoicing tool for freelancers. Walk me through the generator options before you create anything.

> Show me the Djass generator options and recommend a conservative set for an MVP.

> Check the status of Djass project 123 and download it into ./invoicer when it is ready.

The agent will stop and ask before enabling optional integrations such as payments, analytics, storage, support chat, AI, CI, or deployment targets. Saying "use the defaults" is a complete answer.

## Bundled MCP tools

| Tool | Purpose |
|---|---|
| `get_generator_options` | Current fields, defaults, and feature flags grouped by category. |
| `create_project` | Queue one generation for the authenticated account. |
| `get_project_status` | Poll `queued`, `generating`, `ready`, or `failed`; includes download metadata when ready. |
| `get_project_download` | Authenticated ZIP URL, filename, size, and SHA-256 for a ready project. |
| `list_projects` | The account's projects, filterable by status. |

The hosted server cannot write to your filesystem; the agent fetches the ZIP URL with the same bearer token and unzips it client-side, or uses the `djass` CLI which does all of that in one step. The generator option `use_mcp` is unrelated: it decides whether the *generated* project includes its own MCP scaffolding.

## Troubleshooting

- **`401 invalid_token` on MCP initialize**: `DJASS_API_KEY` was not visible to the client process. Export it where the client starts, then restart the client.
- **Tools missing**: the skill alone does not configure MCP. Install the plugin for your harness or merge the matching example file, then restart.
- **`403 insufficient_scope`**: a scoped project key is missing `projects:create` or `projects:read`. Use an Agent API key or regrant scopes.
- **`429 quota_exceeded`**: the account hit its project limit; the error's `retry_guidance` says what to do.
- **CLI says the output directory already exists**: pick a new or empty directory; `djass` never overwrites a repo.

## Layout

```
.claude-plugin/marketplace.json              Claude Code marketplace
.agents/plugins/marketplace.json             Codex marketplace
.cursor-plugin/marketplace.json              Cursor marketplace
plugins/djass/.claude-plugin/plugin.json     Claude Code manifest
plugins/djass/.codex-plugin/plugin.json      Codex manifest (+ store metadata, logo)
plugins/djass/.cursor-plugin/plugin.json     Cursor manifest (+ DJASS_API_KEY variable)
plugins/djass/.mcp.json                      MCP connection for Claude Code and Cursor
plugins/djass/.codex-mcp.json                MCP connection for Codex (bearer_token_env_var)
plugins/djass/skills/djass/SKILL.md          the skill
plugins/djass/skills/djass/references/       CLI, API, and generator-option references
plugins/djass/skills/djass/agents/           Codex UI metadata for the skill
integrations/openclaw/djass/                 Agent Plugins 1.0 bundle (plugin.json, mcp.json, synced skill copy)
examples/                                    MCP config snippets for Codex, Cursor, OpenCode, VS Code
install.sh                                   installs the CLI and links the skill
scripts/validate.py, scripts/sync.py         packaging checks and OpenClaw sync
```

## Maintaining

See [`AGENTS.md`](AGENTS.md). After any change:

```bash
make validate
make sync && git diff --exit-code
claude plugin validate .
claude plugin validate ./plugins/djass
```

The Djass server, CLI, and docs live in [LVTD-LLC/djass](https://github.com/LVTD-LLC/djass); this repo ships packaging and instructions, not a second server. Djass docs: https://djass.dev/docs/api/mcp-server/ and https://djass.dev/docs/api/cli/.

## License

MIT, for this repository's packaging and instructions.
