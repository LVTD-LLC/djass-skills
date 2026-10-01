# Djass Projects API v1

Base URL: `https://djass.dev/api/v1`. OpenAPI: https://djass.dev/api/docs. Full doc: https://djass.dev/docs/api/projects-api-v1/

Use this only when the `djass` CLI and the Djass MCP tools are both unavailable.

## Authentication

Send one of, in lookup order:

1. `X-API-Key: <key>`
2. `Authorization: Bearer <key>`

Scopes: `POST /projects` needs `projects:create`; every `GET /projects*` endpoint needs `projects:read`. `GET /project-options` is public. Agent API keys have both scopes; scoped project keys have only what was granted.

## Endpoints

| Method and path | Purpose | Notes |
|---|---|---|
| `GET /project-options` | Current generator catalog | Public. Returns `defaults` and `groups`. |
| `POST /projects` | Queue a generation | Body: flat JSON of fields and flags. Returns `201` with `project`. |
| `GET /projects?limit=&offset=&status=` | List caller's projects | `limit` 1..100, default 20. |
| `GET /projects/{id}` | Full project object | |
| `GET /projects/{id}/status` | Lightweight polling | `status`, `error_message`, `artifact_ready`, timestamps. |
| `GET /projects/{id}/download` | ZIP stream | `409 artifact_not_ready` until `artifact_ready` is true. |

Project `status` is one of `queued`, `generating`, `ready`, `failed`.

## Create payload

Every flag is the string `"y"` or `"n"`. Unknown keys and other values fail validation. Discover the current keys from `/project-options` instead of copying this example.

```json
{
  "project_name": "Acme CRM",
  "project_slug": "acme_crm",
  "caprover_app_name": "acme-crm",
  "project_description": "Internal CRM for support and sales",
  "repo_url": "https://github.com/acme/acme-crm",
  "author_name": "Acme",
  "author_email": "team@acme.test",
  "author_url": "https://acme.test",
  "project_main_color": "green",
  "use_posthog": "y",
  "use_chatwoot": "n",
  "use_s3": "y",
  "use_qdrant": "n",
  "use_stripe": "y",
  "use_sentry": "y",
  "generate_blog": "y",
  "generate_docs": "y",
  "use_mjml": "y",
  "use_keyboard_shortcuts": "y",
  "use_ai": "y",
  "use_healthchecks": "y",
  "use_apprise": "n",
  "use_mcp": "n",
  "use_ci": "y",
  "use_digitalocean": "n"
}
```

`project_slug` is normalized server-side (slugify, then `-` becomes `_`). An empty `author_email` is filled from the account email.

## Errors

Every non-2xx response:

```json
{
  "error": {
    "code": "machine_readable_code",
    "category": "validation|auth|quota|retryable|internal",
    "message": "Human readable summary",
    "retryable": false,
    "details": {}
  }
}
```

| Status | `code` | Action |
|---|---|---|
| 400 | `invalid_project_slug` | Fix the slug. |
| 401 | `auth_required` | Key missing or invalid. Ask the user. |
| 403 | `insufficient_scope` | `details.required_scope` names the scope. Ask the user for a key with it. |
| 404 | `project_not_found` | Wrong id or not owned by this key. |
| 409 | `artifact_not_ready` | Keep polling `/status`. |
| 429 | `quota_exceeded` | Account limit hit; `details.retry_guidance` explains. Stop. |
| 503 | `retryable_error` | Retry with exponential backoff. |
| 500 | `internal_error` | Report it; retry once at most. |

Retry only when `retryable` is true or the failure is a transient network error.

## Polling

Start at 2 seconds, back off to at most 15 seconds, stop when `status` is `ready` or `failed`. There is no webhook.

## curl flow

```bash
export DJASS_BASE_URL="https://djass.dev/api/v1"
# DJASS_API_KEY must already be exported; do not echo it.

curl -sS "$DJASS_BASE_URL/project-options"

curl -sS -X POST "$DJASS_BASE_URL/projects" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $DJASS_API_KEY" \
  --data @project.json

PROJECT_ID=123
curl -sS "$DJASS_BASE_URL/projects/$PROJECT_ID/status" -H "X-API-Key: $DJASS_API_KEY"

curl -fL "$DJASS_BASE_URL/projects/$PROJECT_ID/download" \
  -H "X-API-Key: $DJASS_API_KEY" -o acme_crm.zip
unzip -q acme_crm.zip -d ./acme_crm
```

Known limits: no idempotency key on create (duplicates are possible), no completion webhook, no server request id in the body.
