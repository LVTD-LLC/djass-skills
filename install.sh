#!/usr/bin/env bash
# Installs the djass CLI and links the djass skill where AI coding agents look
# for skills. Safe to rerun. Flags: --no-cli, --no-skill.
set -euo pipefail

want_cli=1
want_skill=1
for arg in "$@"; do
  case "$arg" in
    --no-cli) want_cli=0 ;;
    --no-skill) want_skill=0 ;;
    -h|--help)
      sed -n '2,3p' "$0" | sed 's/^# //'; exit 0 ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_src="$here/plugins/djass/skills/djass"

if [ "$want_cli" = 1 ]; then
  if command -v djass >/dev/null 2>&1; then
    echo "djass already installed: $(djass version)"
  elif command -v brew >/dev/null 2>&1; then
    echo "installing the djass CLI with Homebrew..."
    brew install LVTD-LLC/tap/djass
  elif command -v curl >/dev/null 2>&1; then
    echo "installing the djass CLI from https://djass.dev/downloads/cli/install.sh ..."
    curl -fsSL https://djass.dev/downloads/cli/install.sh | sh
    install_dir="${DJASS_INSTALL_DIR:-$HOME/.local/bin}"
    case ":$PATH:" in
      *":$install_dir:"*) ;;
      *) echo "note: add $install_dir to PATH to run djass." ;;
    esac
  else
    echo "curl not found. Install curl, or download the CLI from https://djass.dev/downloads/cli/latest/ then rerun." >&2
    exit 1
  fi
fi

if [ "$want_skill" = 1 ]; then
  # ~/.agents/skills is read by Codex, Cursor and OpenCode; ~/.claude/skills by Claude Code.
  for dir in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    mkdir -p "$dir"
    target="$dir/djass"
    if [ -L "$target" ] || [ -e "$target" ]; then
      echo "skill already present at $target (left untouched)"
    else
      ln -s "$skill_src" "$target"
      echo "linked skill: $target -> $skill_src"
    fi
  done
fi

echo
if [ -z "${DJASS_API_KEY:-}" ]; then
  echo "next: copy your Agent API key from https://djass.dev/settings and export DJASS_API_KEY in the environment that launches your agent."
else
  echo "DJASS_API_KEY is set. Ask your agent to generate a Django SaaS project with Djass."
fi
echo "MCP: the plugin bundles https://djass.dev/mcp for Claude Code, Codex, Cursor and OpenClaw; other clients can merge a file from examples/."
