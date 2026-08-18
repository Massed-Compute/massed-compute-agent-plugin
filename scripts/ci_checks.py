#!/usr/bin/env python3
"""CI-safe structural, JSON, secret, and home-path checks. No MCP calls."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "massed-compute"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CURSOR_MARKETPLACE = ROOT / ".cursor-plugin" / "marketplace.json"
PLUGIN_JSON = PLUGIN / ".claude-plugin" / "plugin.json"
CURSOR_PLUGIN_JSON = PLUGIN / ".cursor-plugin" / "plugin.json"
MCP_JSON = PLUGIN / ".mcp.json"
CURSOR_MCP_JSON = PLUGIN / "mcp.json"

JSON_FILES = (
    MCP_JSON,
    CURSOR_MCP_JSON,
    PLUGIN_JSON,
    CURSOR_PLUGIN_JSON,
    MARKETPLACE,
    CURSOR_MARKETPLACE,
)

SCAN_ROOTS = (
    PLUGIN,
    ROOT / ".claude-plugin",
    ROOT / ".cursor-plugin",
    ROOT / ".github",
    ROOT / "listing",
    ROOT / "scripts",
    ROOT / "tests",
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "PASS_LOG.md",
    ROOT / "SECURITY.md",
    ROOT / "LICENSE",
)

SECRET_RES = [
    re.compile(r"(?i)authorization\s*[:=]\s*['\"]?\s*bearer\s+[A-Za-z0-9._\-+/=]{12,}"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\."),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
]

PLACEHOLDER_OK = (
    "<your-api-key>",
    "YOUR_API_KEY",
    "Bearer <your-api-key>",
)

HOME_RE = re.compile(r"(?:/Users|/home)/[A-Za-z0-9._-]+")
HOME_ALLOW = {"you", "username", "name", "user", "<name>"}

TEXT_SUFFIX = {".md", ".json", ".yml", ".yaml", ".txt", ".sh", ".py", ".toml"}


def iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in TEXT_SUFFIX or path.name in {
                "SKILL.md",
                "plugin.json",
                "marketplace.json",
            }:
                files.append(path)
    return files


def check_json() -> list[str]:
    errors: list[str] = []
    for path in JSON_FILES:
        if not path.is_file():
            errors.append(f"missing JSON: {path.relative_to(ROOT)}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
    return errors


def check_structure() -> list[str]:
    errors: list[str] = []
    for path in JSON_FILES:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return errors

    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    cursor_plugin = json.loads(CURSOR_PLUGIN_JSON.read_text(encoding="utf-8"))
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    cursor_market = json.loads(CURSOR_MARKETPLACE.read_text(encoding="utf-8"))
    mcp = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    cursor_mcp = json.loads(CURSOR_MCP_JSON.read_text(encoding="utf-8"))

    if plugin.get("name") != "massed-compute":
        errors.append(".claude-plugin/plugin.json name must be massed-compute")
    if plugin.get("defaultEnabled") is not False:
        errors.append(".claude-plugin/plugin.json defaultEnabled must be false")
    if cursor_plugin.get("name") != "massed-compute":
        errors.append(".cursor-plugin/plugin.json name must be massed-compute")
    if cursor_plugin.get("displayName") != "Massed Compute":
        errors.append(".cursor-plugin/plugin.json displayName must be Massed Compute")

    plugins = market.get("plugins") or []
    if not plugins:
        errors.append(".claude-plugin/marketplace.json has no plugins")
    for entry in plugins:
        source = entry.get("source")
        if not source:
            errors.append(".claude-plugin marketplace plugin missing source")
            continue
        src_path = (ROOT / source).resolve()
        if not src_path.is_dir():
            errors.append(f".claude-plugin marketplace source missing: {source}")

    cursor_plugins = cursor_market.get("plugins") or []
    if not cursor_plugins:
        errors.append(".cursor-plugin/marketplace.json has no plugins")
    for entry in cursor_plugins:
        source = entry.get("source")
        if not source:
            errors.append(".cursor-plugin marketplace plugin missing source")
            continue
        src_path = (ROOT / source).resolve()
        if not src_path.is_dir():
            errors.append(f".cursor-plugin marketplace source missing: {source}")
        if not (src_path / ".cursor-plugin" / "plugin.json").is_file():
            errors.append(f"Cursor source missing manifest: {source}/.cursor-plugin/plugin.json")
        if not (src_path / "mcp.json").is_file():
            errors.append(f"Cursor source missing MCP config: {source}/mcp.json")

    for label, payload in ((".mcp.json", mcp), ("mcp.json", cursor_mcp)):
        servers = (payload.get("mcpServers") or {})
        server = servers.get("massed-compute") or {}
        if server.get("type") != "http":
            errors.append(f"{label} massed-compute.type must be http")
        url = server.get("url") or ""
        if not str(url).startswith("https://"):
            errors.append(f"{label} url must be https")
        headers = server.get("headers") or {}
        auth = headers.get("Authorization") or headers.get("authorization")
        if auth:
            errors.append(f"{label} must not ship an Authorization header")

    skills_dir = PLUGIN / "skills"
    if not skills_dir.is_dir():
        errors.append("missing plugins/massed-compute/skills")
        return errors
    skill_dirs = [p for p in skills_dir.iterdir() if p.is_dir()]
    if not skill_dirs:
        errors.append("no skill directories found")
    for skill in skill_dirs:
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"missing {skill_md.relative_to(ROOT)}")
    return errors


def check_secrets() -> list[str]:
    errors: list[str] = []
    for path in iter_scan_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if any(tok in line for tok in PLACEHOLDER_OK):
                continue
            for rx in SECRET_RES:
                if rx.search(line):
                    errors.append(f"{path.relative_to(ROOT)}: secret-shaped match")
                    break
    return errors


def check_home_paths() -> list[str]:
    errors: list[str] = []
    for path in iter_scan_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in HOME_RE.finditer(text):
            name = match.group(0).rsplit("/", 1)[-1]
            if name.lower() in HOME_ALLOW:
                continue
            errors.append(f"{path.relative_to(ROOT)}: machine-specific path {match.group(0)}")
    return errors


CHECKS = {
    "json": check_json,
    "structure": check_structure,
    "secrets": check_secrets,
    "home-paths": check_home_paths,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        choices=list(CHECKS),
        action="append",
        help="Run a subset of checks (repeatable). Default: all.",
    )
    args = parser.parse_args()
    selected = args.only or list(CHECKS)
    failed = 0
    for name in selected:
        errors = CHECKS[name]()
        if errors:
            failed = 1
            print(f"FAIL {name}")
            for err in errors:
                print(f"  {err}")
        else:
            print(f"PASS {name}")
    return failed


if __name__ == "__main__":
    sys.exit(main())
