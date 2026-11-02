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
DIRECTORY = ROOT / "plugins" / "massed-compute-directory"
DIRECTORY_MANIFEST = DIRECTORY / ".claude-plugin" / "plugin.json"
DIRECTORY_MCP = DIRECTORY / ".mcp.json"

# This public package is deliberately a fixed, reviewed set of skills plus one
# OAuth endpoint. New runtime components or files require an explicit review of
# this allowlist; legacy full-connector packages retain their existing rules.
DIRECTORY_MANIFEST_KEYS = {
    "name", "version", "description", "author", "homepage", "repository",
    "license", "privacyPolicyUrl", "icon", "keywords", "defaultEnabled",
}
DIRECTORY_FILES = {
    ".claude-plugin/plugin.json", ".mcp.json", "README.md", "LICENSE",
    "assets/icon.png", "skills/mc-existing-vms/SKILL.md",
    "skills/mc-safe-changes/SKILL.md",
}

JSON_FILES = (
    DIRECTORY_MANIFEST,
    DIRECTORY_MCP,
    MCP_JSON,
    CURSOR_MCP_JSON,
    PLUGIN_JSON,
    CURSOR_PLUGIN_JSON,
    MARKETPLACE,
    CURSOR_MARKETPLACE,
)

SCAN_ROOTS = (
    DIRECTORY,
    PLUGIN,
    ROOT / ".claude-plugin",
    ROOT / ".cursor-plugin",
    ROOT / ".github",
    ROOT / "listing",
    ROOT / "scripts",
    ROOT / "tests",
    ROOT / "docs",
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

TEXT_SUFFIX = {".md", ".json", ".yml", ".yaml", ".txt", ".sh", ".py", ".toml", ".ts"}


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
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                errors.append(f"JSON object required: {path.relative_to(ROOT)}")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
    return errors


def check_directory_skill(path: Path) -> list[str]:
    """Validate this package's scalar-only YAML frontmatter without a YAML dependency.

    Public skills use exactly name and description. Scalars may be plain text
    starting with a letter, JSON double-quoted strings, or YAML single-quoted
    strings. Other YAML forms
    are rejected explicitly rather than guessed at by a partial YAML parser.
    """
    label = str(path.relative_to(ROOT))
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return [f"{label}: missing frontmatter opening delimiter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return [f"{label}: missing frontmatter closing delimiter"]
    values: dict[str, str] = {}
    errors: list[str] = []
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):[ ]+(.*)", line)
        if not match:
            errors.append(f"{label}: frontmatter must use single-line text fields")
            continue
        key, raw = match.groups()
        raw = raw.strip()
        if key not in {"name", "description"}:
            errors.append(f"{label}: unexpected frontmatter field {key}")
            continue
        if key in values:
            errors.append(f"{label}: duplicate frontmatter field {key}")
            continue
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                errors.append(f"{label}: invalid quoted text for {key}")
                continue
        elif raw.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", raw):
                errors.append(f"{label}: invalid quoted text for {key}")
                continue
            value = raw[1:-1].replace("''", "'")
        else:
            value = re.sub(r"\s+#.*$", "", raw)
            if (
                not value
                or not re.match(r"[A-Za-z]", value)
                or re.search(r":(?:\s|$)", value)
                or value.lower() in {"null", "~", "true", "false", "yes", "no", "on", "off"}
            ):
                errors.append(f"{label}: {key} must be text, not another YAML value")
                continue
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}: {key} must be non-empty text")
            continue
        values[key] = value
    for key in ("name", "description"):
        if key not in values:
            errors.append(f"{label}: missing valid {key}")
    if "name" in values and (
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", values["name"])
        or values["name"] != path.parent.name
    ):
        errors.append(f"{label}: name must match its kebab-case skill directory")
    return errors


def check_directory_contents() -> list[str]:
    """Reject implicit components and symlinks before reading public config."""
    errors: list[str] = []
    if DIRECTORY.is_symlink() or not DIRECTORY.is_dir():
        return ["directory package must be a real directory, not a symlink"]
    allowed_dirs = {
        parent.as_posix()
        for rel in DIRECTORY_FILES
        for parent in Path(rel).parents
        if parent != Path(".")
    }

    def visit(folder: Path) -> None:
        for path in sorted(folder.iterdir()):
            rel = path.relative_to(DIRECTORY).as_posix()
            if path.is_symlink():
                errors.append(f"directory package must not contain symlinks: {rel}")
            elif path.is_dir():
                if rel not in allowed_dirs:
                    errors.append(f"directory package has unexpected directory: {rel}")
                else:
                    visit(path)
            elif not path.is_file() or rel not in DIRECTORY_FILES:
                errors.append(f"directory package has unexpected file: {rel}")

    visit(DIRECTORY)
    return errors


def check_structure() -> list[str]:
    errors = check_directory_contents()
    if errors:
        return errors
    errors = check_json()
    if errors:
        return errors
    for path in JSON_FILES:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return errors

    directory_plugin = json.loads(DIRECTORY_MANIFEST.read_text(encoding="utf-8"))
    directory_mcp = json.loads(DIRECTORY_MCP.read_text(encoding="utf-8"))
    if not isinstance(directory_plugin, dict) or not isinstance(directory_mcp, dict):
        return ["directory manifest and MCP configuration must be JSON objects"]
    for key in sorted(set(directory_plugin) - DIRECTORY_MANIFEST_KEYS):
        errors.append(f"directory manifest must not configure {key}; only reviewed metadata is allowed")
    if directory_plugin.get("name") != "massed-compute-directory":
        errors.append("directory plugin name must be massed-compute-directory")
    version = directory_plugin.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", version):
        errors.append("directory plugin must have a release version")
    if directory_plugin.get("defaultEnabled") is not True:
        errors.append("public directory plugin must activate after explicit installation")
    if directory_plugin.get("privacyPolicyUrl") != "https://massedcompute.com/legal/privacy-policy/":
        errors.append("directory plugin must explicitly link the privacy policy")
    servers = directory_mcp.get("mcpServers") or {}
    if not isinstance(servers, dict):
        errors.append("directory mcpServers must be a JSON object")
        servers = {}
    server = servers.get("massed-compute-directory") or {}
    if not isinstance(server, dict):
        errors.append("directory server configuration must be a JSON object")
        server = {}
    if set(servers) != {"massed-compute-directory"}:
        errors.append("directory package must reference only the public management server")
    if server.get("url") != "https://vm.massedcompute.com/api/mcp/directory" or server.get("type") != "http":
        errors.append("directory server must use the HTTPS HTTP directory endpoint")
    if set(directory_mcp) != {"mcpServers"}:
        errors.append("directory MCP configuration must contain only mcpServers")
    # This package is pure provider OAuth: no headers, env, helper commands,
    # alternate launchers or other authentication/configuration escape paths.
    for key in sorted(set(server) - {"type", "url"}):
        errors.append(f"directory server must not configure {key}; only type and url are allowed")
    for rel in ("README.md", "LICENSE", "assets/icon.png", "skills/mc-existing-vms/SKILL.md", "skills/mc-safe-changes/SKILL.md"):
        if not (DIRECTORY / rel).is_file():
            errors.append(f"directory package missing {rel}")
    skills = DIRECTORY / "skills"
    if skills.is_dir():
        for skill_dir in sorted(p for p in skills.iterdir() if p.is_dir()):
            skill_path = skill_dir / "SKILL.md"
            if not skill_path.is_file():
                errors.append(f"directory skill missing {skill_path.relative_to(ROOT)}")
            else:
                errors.extend(check_directory_skill(skill_path))

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
    cursor_owner = cursor_market.get("owner") or {}
    if cursor_owner.get("email") != "techadmin@massedcompute.com":
        errors.append(".cursor-plugin/marketplace.json owner.email must be techadmin@massedcompute.com")
    cursor_author = cursor_plugin.get("author") or {}
    if cursor_author.get("email") != "techadmin@massedcompute.com":
        errors.append(".cursor-plugin/plugin.json author.email must be techadmin@massedcompute.com")
    logo = cursor_plugin.get("logo")
    if not logo:
        errors.append(".cursor-plugin/plugin.json must include logo")
    elif not (PLUGIN / logo).is_file():
        errors.append(f".cursor-plugin/plugin.json logo missing: {logo}")
    elif not logo.startswith("assets/"):
        errors.append(".cursor-plugin/plugin.json logo must use a dedicated plugin asset, not a skill icon")

    plugins = market.get("plugins") or []
    if not isinstance(plugins, list) or any(not isinstance(entry, dict) for entry in plugins):
        errors.append("marketplace plugins must be a list of JSON objects")
        plugins = []
    if not plugins:
        errors.append(".claude-plugin/marketplace.json has no plugins")
    directory_entries = [entry for entry in plugins if entry.get("name") == "massed-compute-directory"]
    if len(directory_entries) != 1:
        errors.append("marketplace must contain exactly one massed-compute-directory entry")
    else:
        entry = directory_entries[0]
        if entry.get("name") != directory_plugin.get("name") or entry.get("version") != directory_plugin.get("version"):
            errors.append("directory marketplace name/version must match the plugin manifest")
        expected_source = "./" + DIRECTORY.relative_to(ROOT).as_posix()
        if entry.get("source") != expected_source:
            errors.append(f"directory marketplace source must be {expected_source}")
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
        if source.startswith("./"):
            errors.append(".cursor-plugin marketplace source should not use a ./ prefix")
        src_path = (ROOT / source).resolve()
        if not src_path.is_dir():
            errors.append(f".cursor-plugin marketplace source missing: {source}")
        if not (src_path / ".cursor-plugin" / "plugin.json").is_file():
            errors.append(f"Cursor source missing manifest: {source}/.cursor-plugin/plugin.json")
        if not (src_path / "mcp.json").is_file():
            errors.append(f"Cursor source missing MCP config: {source}/mcp.json")

    claude_server = (mcp.get("mcpServers") or {}).get("massed-compute") or {}
    cursor_server = (cursor_mcp.get("mcpServers") or {}).get("massed-compute") or {}
    if claude_server.get("type") != "http":
        errors.append(".mcp.json massed-compute.type must be http")
    for label, server in ((".mcp.json", claude_server), ("mcp.json", cursor_server)):
        url = server.get("url") or ""
        if not str(url).startswith("https://"):
            errors.append(f"{label} url must be https")
        headers = server.get("headers") or {}
        auth = headers.get("Authorization") or headers.get("authorization")
        if auth:
            errors.append(f"{label} must not ship an Authorization header")
    if claude_server.get("url") != cursor_server.get("url"):
        errors.append(".mcp.json and mcp.json must point at the same Massed Compute MCP URL")

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
