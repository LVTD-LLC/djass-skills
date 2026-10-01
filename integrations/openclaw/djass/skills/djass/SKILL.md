---
name: djass
description: Generate a production-ready Django SaaS repository with Djass (built on django-saas-starter) and put it in the current workspace. Use when the user wants to start a new Django project, SaaS, or web app, scaffold a Django codebase, says "use Djass", mentions django-saas-starter, wants a generated project ZIP, or asks about a queued Djass project. Covers the djass CLI, the hosted Djass MCP tools, the Projects API fallback, choosing generator options, and first steps in the generated repo.
license: MIT
compatibility: Needs a Djass account and API key exported as DJASS_API_KEY. The CLI path needs a shell with curl; the MCP path needs the hosted Djass MCP connection that this plugin bundles.
metadata:
  author: LVTD-LLC
  version: "0.1.0"
  homepage: https://djass.dev
---

# Djass: generate a Django SaaS repository

Djass renders `django-saas-starter` with the options the user picks, zips the result, and serves it. Your job: settle the options with the user, queue one generation, wait for it, and unpack the repo into an empty directory. Generation usually finishes within a few minutes; the CLI waits up to 10 minutes by default.

Three ways to reach Djass. Use the first that fits:

| Path | Use when | Lands the repo locally? |
|---|---|---|
| `djass` CLI | You have a shell (every coding agent does) | Yes, one command does create, poll, download, verify, extract |
| Djass MCP tools: `get_generator_options`, `create_project`, `get_project_status`, `get_project_download`, `list_projects` | No shell, or to inspect options and status | No, returns a download URL for you to fetch |
| Projects API at `https://djass.dev/api/v1` | Neither of the above works | No, returns a ZIP stream |

All three take the same API key and the same option names.

## 1. Credentials

Djass needs an API key from https://djass.dev/settings. An Agent API key has every scope; a scoped project key needs `projects:create` and `projects:read`.

- The CLI and the API read `DJASS_API_KEY` from the environment.
- The bundled MCP connection sends `Authorization: Bearer ${DJASS_API_KEY}` from the client's environment.

Check presence without printing the value:

```bash
[ -n "${DJASS_API_KEY:-}" ] && echo set || echo missing
```

If it is missing, ask the user to export it in the environment that launches their agent and restart the session. Never print the key, pass it as a command argument, put it in a URL, or write it into any file in the repo.

## 2. Install the CLI (shell path)

```bash
djass version >/dev/null 2>&1 || curl -fsSL https://djass.dev/downloads/cli/install.sh | sh
```

This installs a checksum-verified binary into `~/.local/bin` (`DJASS_INSTALL_DIR` overrides). Make sure that directory is on `PATH`. Windows archives are under https://djass.dev/downloads/cli/latest/.

## 3. Discover the current options

Never hard-code the option list; it changes when the template changes.

```bash
djass options
```

or call the `get_generator_options` MCP tool, or `GET https://djass.dev/api/v1/project-options` (public, no key).

The response has `defaults` (every field with its default) and `groups` (feature flags with labels and descriptions, by category). [references/generator-options.md](references/generator-options.md) explains what each flag adds to the generated repo.

## 4. Collect the project fields

Ask for whatever the user has not already given you:

- `project_name`: human name, for example `Acme CRM`.
- `project_slug`: the Python package name. Lowercase letters, digits, underscores, no leading digit. Djass slugifies and turns `-` into `_`, but propose the slug yourself and confirm it.
- `project_description`: one sentence.
- `repo_url`, `author_name`, `author_email`, `author_url`: use the user's values or leave them out. An empty `author_email` is filled from the account.
- `project_main_color`: a Tailwind color name; default `green`.
- `caprover_app_name`: defaults to the slug with hyphens; only matters for CapRover deploys.

## 5. Confirm every feature flag with the user

This is the step agents get wrong. Do not pick optional integrations from the app idea. Show the user the flags grouped the way the catalog groups them (monitoring, CX, commerce, storage, UX, content, AI, delivery) with their defaults, and ask which to enable. "Use the defaults" is a valid answer and counts as confirmation. Record the final `y` or `n` for every flag before you generate.

`use_mcp` means "put MCP server scaffolding inside the generated project". It has nothing to do with the Djass MCP connection you may be using right now.

Keep the first generation conservative: only what the user will wire up in the next few weeks.

## 6. Generate

### CLI (preferred when you have a shell)

```bash
djass generate \
  --name "Acme CRM" \
  --slug acme_crm \
  --set use_stripe=y --set use_posthog=y --set use_mcp=n \
  --output ./acme_crm
```

Pass every confirmed flag with `--set key=y` or `--set key=n`; unspecified flags take the catalog default. `--output` must be a new or empty directory; the CLI refuses to overwrite and rejects unsafe ZIP entries. It queues the job, polls (`--poll-interval`, default 2s; `--timeout`, default 10m), downloads, verifies, and extracts. Success prints JSON with `output`, `project_id`, `size_bytes`, and `status`. For a payload you already built, use `--payload project.json`. Flags and exit codes: [references/cli.md](references/cli.md).

### MCP tools

1. `create_project` with the explicit fields and every flag as the string `"y"` or `"n"`. Note the returned `id`.
2. `get_project_status` every 2 seconds, backing off to 15 seconds, until `status` is `ready` or `failed`. A `failed` project carries `error_message`; report it, do not retry blindly.
3. When `artifact_ready` is true, `get_project_download` returns a `download` object with `download_url`, `filename`, `size_bytes`, and `sha256`. Fetch the URL with `Authorization: Bearer <key>` from the client side, save the ZIP, check the SHA-256 if you can, and unzip into an empty directory. The hosted server cannot write to your filesystem.

### HTTP API

Only when neither the CLI nor MCP works. `POST /projects`, then `GET /projects/{id}/status`, then `GET /projects/{id}/download`, all with `X-API-Key`. Contract and error shapes: [references/api.md](references/api.md).

## 7. After generation

1. Read `djass-manifest.json` and `project-metadata.json` at the repo root. They record the options used, the template version, and checksums.
2. Read the generated `README.md` and `AGENTS.md`, then follow their setup steps (env file, local stack, migrations). Do not invent setup steps the generated repo does not document.
3. Tell the user what was generated, which flags were on, where it lives, and the project id for later downloads.

## Rules

- One generation per confirmed spec. Creating projects is not idempotent; calling `create_project` again makes a duplicate.
- Never overwrite an existing directory. Pick a new `--output` or ask.
- Never infer optional flags and never silently flip a default.
- Never expose the API key: no echo, no logs, no commits, no URL query strings.
- Flag values are the strings `"y"` and `"n"`, not booleans.
- Unknown option keys fail validation. Use only keys from the live catalog.

## Errors

The API and the CLI share one error shape: `{"error": {"code", "category", "message", "retryable", "details"}}`.

- `auth_required` (401) or `insufficient_scope` (403): the key is missing, wrong, or lacks a scope. Ask the user; do not retry.
- `invalid_project_slug` (400): fix the slug.
- `quota_exceeded` (429): the account hit its project limit. Tell the user.
- `artifact_not_ready` (409): keep polling status.
- `retryable_error` (503) or a network failure: retry with backoff a few times.
- CLI exit 5 with "already exists": choose another output directory.
- Djass MCP tools absent: the connection is not configured or `DJASS_API_KEY` is missing from the client environment. Point the user to the install section of this plugin's README. If you fall back to the CLI or API, say so.

## When to stop and ask

Ask the user, not the API, when `DJASS_API_KEY` is missing, the slug is ambiguous, any flag is unconfirmed, the destination directory is not empty, or a generation fails with a message you cannot act on.
