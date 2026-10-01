# Djass generator options

What each option changes in the generated repository. The live catalog (`djass options`, the `get_generator_options` MCP tool, or `GET https://djass.dev/api/v1/project-options`) is the source of truth; this page explains the entries and can lag behind it. Full doc: https://djass.dev/docs/features/generator-options/

These are build-time choices. They add or omit code; they are not runtime feature flags.

## Core fields

| Key | Default | What it does |
|---|---|---|
| `project_name` | `My Awesome Project` | Human name used in templates and package metadata. |
| `project_slug` | derived from the name | Python package and directory name: lowercase, underscores. |
| `caprover_app_name` | slug with hyphens | App name in the generated CapRover deployment config. |
| `project_description` | placeholder sentence | README and metadata. |
| `repo_url` | placeholder | Repository link in templates and docs. |
| `author_name`, `author_email`, `author_url` | placeholders / empty | Package metadata; empty email is filled from the account. |
| `project_main_color` | `green` | Primary Tailwind color referenced by templates. |

## Feature flags (`"y"` or `"n"`)

### Monitoring

| Key | Default | Adds |
|---|---|---|
| `use_posthog` | `y` | PostHog product analytics. Backend logs use standard Python logging so PostHog Logs can consume the same structured fields. |
| `use_sentry` | `y` | Sentry error monitoring wired to Python logging records (breadcrumbs, events, optional logs). |
| `use_healthchecks` | `y` | Health-check endpoints and monitoring configuration. |
| `use_apprise` | `n` | Apprise-backed admin notifications with email fallback. |

### CX

| Key | Default | Adds |
|---|---|---|
| `use_chatwoot` | `n` | Customer support chat scaffolding, off at runtime until configured. |
| `use_mjml` | `y` | MJML email template rendering for transactional mail. |

### Commerce

| Key | Default | Adds |
|---|---|---|
| `use_stripe` | `y` | Subscription, checkout, billing, webhook, and pricing-page pieces. |

### Storage

| Key | Default | Adds |
|---|---|---|
| `use_s3` | `y` | S3-compatible media storage settings and deployment guidance. No upload forms or validation. |
| `use_qdrant` | `n` | Authenticated Qdrant client configuration with lazy connection. Does not provision Qdrant, create collections, or define vector workflows. |

### UX

| Key | Default | Adds |
|---|---|---|
| `use_keyboard_shortcuts` | `y` | Keyboard shortcut helpers, data attributes, and visible hints for command-style controls. |

### Content

| Key | Default | Adds |
|---|---|---|
| `generate_blog` | `y` | Blog app, routes, templates, admin tooling, tests. |
| `generate_docs` | `y` | Markdown-driven docs pages, navigation, templates, tests. |

### AI

| Key | Default | Adds |
|---|---|---|
| `use_ai` | `y` | Pydantic AI service scaffolding, provider settings, example tests. |
| `use_mcp` | `n` | An MCP server scaffold inside the generated project. Unrelated to the Djass MCP connection used to run the generator. |

### Delivery

| Key | Default | Adds |
|---|---|---|
| `use_ci` | `y` | GitHub Actions checks for the generated project. |
| `use_digitalocean` | `n` | DigitalOcean App Platform configuration and deployment docs. |

## Guidance

- Enable only what the user will wire up in the next few weeks. Adding an integration later is easier than carrying unused ones.
- Never choose a flag from the app idea alone; ask. "Use the defaults" is an explicit answer.
- If the live catalog shows a key that is not on this page, describe it from its catalog `description` and ask the user about it like any other flag.
