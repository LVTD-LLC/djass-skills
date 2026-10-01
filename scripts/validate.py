#!/usr/bin/env python3
"""Offline packaging checks for djass-skills. Standard library only (Python 3.11+)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11: minimal parse of the one flat table we ship.
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
NAME = "djass"
MARKETPLACE = "djass-skills"
MCP_URL = "https://djass.dev/mcp"
REPO_URL = "https://github.com/LVTD-LLC/djass-skills"
AUTHOR = "LVTD LLC"
ENV_VAR = "DJASS_API_KEY"
MCP_TOOLS = [
    "get_generator_options",
    "create_project",
    "get_project_status",
    "get_project_download",
    "list_projects",
]
# A real Djass key never belongs in this repo; catch anything that looks like one.
SECRET_PATTERNS = [
    re.compile(r"Bearer\s+(?!\$\{|\{env:|\$\{input:|<)[A-Za-z0-9_\-]{20,}"),
    re.compile(r"X-API-Key:\s+(?!\$|<)[A-Za-z0-9_\-]{20,}"),
    re.compile(r"DJASS_API_KEY\s*=\s*[\"']?(?!replace|<|\$)[A-Za-z0-9_\-]{20,}"),
]

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def tree(directory: Path) -> dict[str, bytes]:
    return {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def load_codex_toml(text: str) -> dict:
    if tomllib is not None:
        return tomllib.loads(text)["mcp_servers"][NAME]
    assert f"[mcp_servers.{NAME}]" in text, "examples/codex.toml: missing mcp_servers table"
    return {key: value for key, value in re.findall(r'^(\w+)\s*=\s*"([^"]*)"', text, flags=re.M)}


def safe_relative_path(value: str) -> bool:
    return value.startswith("./") and ".." not in Path(value).parts


def main() -> int:
    # Every JSON file in the repo must parse.
    for path in ROOT.rglob("*.json"):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
    if failures:
        return report()

    # Plugin manifests: same name, version, author, repository; referenced paths exist.
    manifests = {
        "plugins/djass/.claude-plugin/plugin.json": "plugins/djass",
        "plugins/djass/.codex-plugin/plugin.json": "plugins/djass",
        "plugins/djass/.cursor-plugin/plugin.json": "plugins/djass",
        "integrations/openclaw/djass/plugin.json": "integrations/openclaw/djass",
    }
    versions = set()
    for relative, base in manifests.items():
        manifest = read_json(relative)
        check(manifest.get("name") == NAME, f"{relative}: name must be {NAME!r}")
        check(bool(manifest.get("version")), f"{relative}: version missing")
        versions.add(manifest.get("version"))
        check(manifest.get("author", {}).get("name") == AUTHOR, f"{relative}: author.name must be {AUTHOR!r}")
        check(manifest.get("repository") == REPO_URL, f"{relative}: repository must be {REPO_URL}")
        check(manifest.get("homepage") == "https://djass.dev", f"{relative}: homepage must be https://djass.dev")
        check(manifest.get("license") == "MIT", f"{relative}: license must be MIT")
        for field in ("skills", "mcpServers"):
            value = manifest.get(field)
            if isinstance(value, str):
                check(safe_relative_path(value), f"{relative}: {field} must be a ./ path without ..")
                check((ROOT / base / value).exists(), f"{relative}: {field} path {value} does not exist")
        interface = manifest.get("interface")
        if interface:
            for field in ("composerIcon", "logo"):
                icon = interface.get(field)
                if icon:
                    check(safe_relative_path(icon) and (ROOT / base / icon).is_file(), f"{relative}: {field} {icon} missing")
    check(len(versions) == 1, f"plugin manifests disagree on version: {sorted(v or '' for v in versions)}")
    version = next(iter(versions))

    # Marketplace catalogs.
    claude = read_json(".claude-plugin/marketplace.json")
    check(claude["name"] == MARKETPLACE, ".claude-plugin/marketplace.json: wrong marketplace name")
    entry = claude["plugins"][0]
    check(entry["name"] == NAME and entry["source"] == "./plugins/djass", ".claude-plugin/marketplace.json: bad plugin entry")
    check(entry.get("version") == version, ".claude-plugin/marketplace.json: version differs from plugin manifests")

    codex = read_json(".agents/plugins/marketplace.json")
    check(codex["name"] == MARKETPLACE, ".agents/plugins/marketplace.json: wrong marketplace name")
    source = codex["plugins"][0]["source"]
    check(source == {"source": "local", "path": "./plugins/djass"}, ".agents/plugins/marketplace.json: bad source")
    check(codex["plugins"][0]["policy"]["installation"] == "AVAILABLE", ".agents/plugins/marketplace.json: bad policy")

    cursor = read_json(".cursor-plugin/marketplace.json")
    check(cursor["name"] == MARKETPLACE, ".cursor-plugin/marketplace.json: wrong marketplace name")
    check(cursor["plugins"][0]["source"] == "./plugins/djass", ".cursor-plugin/marketplace.json: bad source")

    # MCP connection files.
    claude_mcp = read_json("plugins/djass/.mcp.json")["mcpServers"][NAME]
    check(claude_mcp == {"type": "http", "url": MCP_URL, "headers": {"Authorization": f"Bearer ${{{ENV_VAR}}}"}},
          "plugins/djass/.mcp.json: unexpected djass server config")
    codex_mcp = read_json("plugins/djass/.codex-mcp.json")["mcpServers"][NAME]
    check(codex_mcp == {"type": "http", "url": MCP_URL, "bearer_token_env_var": ENV_VAR},
          "plugins/djass/.codex-mcp.json: unexpected djass server config")
    openclaw_mcp = read_json("integrations/openclaw/djass/mcp.json")
    check(openclaw_mcp.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
          "integrations/openclaw/djass/mcp.json: missing Agent Plugins schema")
    check(openclaw_mcp["mcpServers"][NAME] == {"type": "streamable-http", "url": MCP_URL,
                                                "headers": {"Authorization": f"Bearer ${{{ENV_VAR}}}"}},
          "integrations/openclaw/djass/mcp.json: unexpected djass server config")
    cursor_manifest = read_json("plugins/djass/.cursor-plugin/plugin.json")
    check(cursor_manifest["variables"]["required"] == [ENV_VAR], "cursor plugin.json: variables.required must list DJASS_API_KEY")

    # Examples for clients without a plugin format.
    opencode = read_json("examples/opencode.json")["mcp"][NAME]
    check(opencode["url"] == MCP_URL and opencode["type"] == "remote" and opencode["oauth"] is False,
          "examples/opencode.json: unexpected config")
    check(opencode["headers"]["Authorization"] == f"Bearer {{env:{ENV_VAR}}}", "examples/opencode.json: bad env syntax")
    cursor_example = read_json("examples/cursor-mcp.json")["mcpServers"][NAME]
    check(cursor_example["url"] == MCP_URL and cursor_example["headers"]["Authorization"] == f"Bearer ${{env:{ENV_VAR}}}",
          "examples/cursor-mcp.json: unexpected config")
    vscode = read_json("examples/vscode-mcp.json")
    check(vscode["servers"][NAME]["url"] == MCP_URL and vscode["inputs"][0]["password"] is True,
          "examples/vscode-mcp.json: unexpected config")
    codex_toml = load_codex_toml((ROOT / "examples/codex.toml").read_text(encoding="utf-8"))
    check(codex_toml == {"url": MCP_URL, "bearer_token_env_var": ENV_VAR}, "examples/codex.toml: unexpected config")

    # The skill itself.
    skill_dir = ROOT / "plugins/djass/skills/djass"
    skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    check(skill.startswith(f"---\nname: {NAME}\ndescription: "), "SKILL.md: frontmatter must start with name then description")
    check(f'version: "{version}"' in skill, "SKILL.md: metadata.version differs from plugin manifests")
    check("TODO" not in skill, "SKILL.md: contains TODO")
    check(len(skill.splitlines()) <= 200, "SKILL.md: keep it under 200 lines")
    for tool in MCP_TOOLS:
        check(f"`{tool}`" in skill, f"SKILL.md: must mention MCP tool {tool}")
    for phrase in ("djass generate", "djass options", "/project-options", "use_mcp", "Never infer optional flags"):
        check(phrase in skill, f"SKILL.md: must mention {phrase!r}")
    check((skill_dir / "agents/openai.yaml").is_file(), "skill: agents/openai.yaml missing")
    for reference in ("cli.md", "api.md", "generator-options.md"):
        check((skill_dir / "references" / reference).is_file(), f"skill: references/{reference} missing")
        check(f"references/{reference}" in skill, f"SKILL.md: must link references/{reference}")

    # OpenClaw bundle carries an identical copy of the skill.
    check(tree(ROOT / "plugins/djass/skills") == tree(ROOT / "integrations/openclaw/djass/skills"),
          "integrations/openclaw/djass/skills differs from plugins/djass/skills; run scripts/sync.py")

    # Local Markdown links resolve; no secrets anywhere.
    markdown = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]
    for path in markdown:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            check((path.parent / target.split("#")[0]).exists(), f"{path.relative_to(ROOT)}: broken link {target}")
    for path in [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and p.suffix in {".md", ".json", ".toml", ".yaml", ".yml", ".sh", ".py"}]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            check(not pattern.search(text), f"{path.relative_to(ROOT)}: looks like it contains a credential")

    check(version in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "CHANGELOG.md: current version not mentioned")
    return report()


def report() -> int:
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASS: manifests, marketplaces, MCP configs, examples, skill contract, OpenClaw sync, links, no secrets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
