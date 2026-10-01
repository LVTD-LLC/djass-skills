# djass CLI reference

The `djass` binary wraps every Projects API v1 operation and prints JSON on stdout so agents can parse it. Source: https://github.com/LVTD-LLC/djass (directory `cli/`).

## Install

Homebrew, macOS or Linux (preferred; `brew upgrade djass` updates it):

```bash
brew install LVTD-LLC/tap/djass
```

Official installer, any Unix with curl:

```bash
curl -fsSL https://djass.dev/downloads/cli/install.sh | sh
```

- The installer puts a checksum-verified release into `~/.local/bin`; set `DJASS_INSTALL_DIR` to change that.
- Windows archives and manual downloads: https://djass.dev/downloads/cli/latest/
- `djass version` prints the installed version.

## Environment

| Variable | Purpose |
|---|---|
| `DJASS_API_KEY` | Required for `generate` and `projects *`. Never printed by the CLI. |
| `DJASS_BASE_URL` | API base, default `https://djass.dev/api/v1`. Only for staging or local Djass. Plain `http://` is accepted only for `localhost` and `127.0.0.1`. |
| `DJASS_INSTALL_DIR` | Installer destination, default `~/.local/bin`. |

Global flag: `--base-url URL` overrides `DJASS_BASE_URL`.

## Commands

```text
djass generate           Create, wait for, download, and safely extract a repository
djass options            Print the live generator option catalog (no key needed)
djass projects create    Queue a project generation job
djass projects list      List projects
djass projects get       Get a project
djass projects status    Get project generation status
djass projects download  Download a generated ZIP
djass version            Print the CLI version
```

Run any subcommand with `-h` for its flags.

### generate

```bash
djass generate --name NAME --slug SLUG [--set key=value]... [--payload FILE] \
  [--output DIR] [--poll-interval 2s] [--timeout 10m]
```

- `--set key=value` is repeatable; any key from `djass options` works, flags take `y` or `n`.
- `--payload FILE` is a JSON file in the exact shape `POST /projects` accepts. `--name`, `--slug`, and `--set` override fields from it.
- `--output DIR` defaults to the slug. It must not exist or must be empty. The CLI never overwrites a repository.
- Downloaded ZIPs are checked for path traversal, symlinks, and other unsafe entries before extraction.
- Progress goes to stderr; the final JSON goes to stdout:

```json
{"output": "/workspace/acme_crm", "project_id": 123, "size_bytes": 48291, "status": "ready"}
```

### projects

```bash
djass projects create --name NAME --slug SLUG [--set key=value]... [--payload FILE]
djass projects list [--limit 20] [--offset 0] [--status queued|generating|ready|failed]
djass projects get <id>
djass projects status <id>
djass projects download <id> [--output project.zip] [--force]
```

`download` refuses to overwrite an existing file unless `--force` is passed.

## Exit codes

| Code | Meaning | `error.code` on stderr |
|---|---|---|
| 0 | Success | |
| 2 | Usage error (bad flags, missing name/slug, bad `--set`) | `usage_error` |
| 3 | Configuration error (missing `DJASS_API_KEY`, invalid base URL) | `configuration_error` |
| 4 | API error; the body is the API's own error object | as returned by the API |
| 5 | Local operation error (destination not empty, unsafe ZIP, write failure) | `operation_error` |

Errors are one JSON line on stderr in the same shape as the API:

```json
{"error": {"code": "operation_error", "category": "operation", "message": "...", "retryable": false, "details": {"exit_code": 5}}}
```
