"""Mutation tests for the public plugin's release and credential boundaries.

Each case operates on an isolated repository copy. No MCP connection is made.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class PublicPackageChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        spec = importlib.util.spec_from_file_location("checks_under_test", self.root / "scripts" / "ci_checks.py")
        self.checks = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.checks)
        self.package = self.root / "plugins" / "massed-compute-directory"

    def read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict) -> None:
        (self.root / relative).write_text(json.dumps(value), encoding="utf-8")

    def test_release_package_passes(self) -> None:
        self.assertEqual([], self.checks.check_structure())

    def test_marketplace_release_must_match_manifest(self) -> None:
        original = self.read_json(".claude-plugin/marketplace.json")
        for field, value in (("name", "other-package"), ("version", "9.9.9"), ("source", "./plugins/massed-compute")):
            with self.subTest(field=field):
                market = json.loads(json.dumps(original))
                entry = next(p for p in market["plugins"] if p["name"] == "massed-compute-directory")
                entry[field] = value
                self.write_json(".claude-plugin/marketplace.json", market)
                self.assertTrue(self.checks.check_structure(), f"accepted mismatched {field}")

    def test_duplicate_public_marketplace_entry_is_rejected(self) -> None:
        market = self.read_json(".claude-plugin/marketplace.json")
        entry = next(p for p in market["plugins"] if p["name"] == "massed-compute-directory")
        market["plugins"].append(entry.copy())
        self.write_json(".claude-plugin/marketplace.json", market)
        self.assertTrue(self.checks.check_structure())

    def test_malformed_marketplace_entries_are_reported(self) -> None:
        relative = ".claude-plugin/marketplace.json"
        original = self.read_json(relative)
        for entries in (["not-an-entry"], {"massed-compute-directory": {}}):
            with self.subTest(entries=entries):
                market = json.loads(json.dumps(original))
                market["plugins"] = entries
                self.write_json(relative, market)
                self.assertTrue(self.checks.check_structure())

    def test_release_version_must_exist_in_manifest(self) -> None:
        manifest = self.read_json("plugins/massed-compute-directory/.claude-plugin/plugin.json")
        del manifest["version"]
        self.write_json("plugins/massed-compute-directory/.claude-plugin/plugin.json", manifest)
        self.assertTrue(self.checks.check_structure())

    def test_authentication_and_launcher_overrides_are_rejected(self) -> None:
        relative = "plugins/massed-compute-directory/.mcp.json"
        original = self.read_json(relative)
        for field, value in (
            ("headers", {"Authorization": "fixture-only"}),
            ("headersHelper", "fixture-helper"),
            ("env", {"API_KEY": "fixture-only"}),
            ("command", "fixture-launcher"),
            ("args", ["fixture-argument"]),
        ):
            with self.subTest(field=field):
                config = json.loads(json.dumps(original))
                config["mcpServers"]["massed-compute-directory"][field] = value
                self.write_json(relative, config)
                self.assertTrue(self.checks.check_structure(), f"accepted {field}")

    def test_root_configuration_override_is_rejected(self) -> None:
        relative = "plugins/massed-compute-directory/.mcp.json"
        config = self.read_json(relative)
        config["env"] = {"API_KEY": "fixture-only"}
        self.write_json(relative, config)
        self.assertTrue(self.checks.check_structure())

    def test_server_collection_must_be_an_object(self) -> None:
        relative = "plugins/massed-compute-directory/.mcp.json"
        self.write_json(relative, {"mcpServers": ["unexpected"]})
        self.assertTrue(self.checks.check_structure())

    def test_frontmatter_rejects_non_text_or_malformed_descriptions(self) -> None:
        skill = self.package / "skills" / "mc-existing-vms" / "SKILL.md"
        for description in ("[]", "{enabled: true}", "false", "42", "1e3", "''", '"unterminated', "|", "!custom value", "Inspect: VMs", "Inspect:"):
            with self.subTest(description=description):
                skill.write_text(f"---\nname: mc-existing-vms\ndescription: {description}\n---\nBody\n", encoding="utf-8")
                self.assertTrue(self.checks.check_structure(), f"accepted {description}")

    def test_frontmatter_rejects_missing_delimiters_and_fields(self) -> None:
        skill = self.package / "skills" / "mc-existing-vms" / "SKILL.md"
        for text in (
            "name: mc-existing-vms\ndescription: Read VMs\n",
            "---\nname: mc-existing-vms\ndescription: Read VMs\n",
            "---\nname: mc-existing-vms\n---\nBody\n",
            "---\nname: mc-existing-vms\ndescription: Read VMs\ndescription: Other text\n---\n",
            "---\nname: different-skill\ndescription: Read VMs\n---\n",
        ):
            with self.subTest(text=text):
                skill.write_text(text, encoding="utf-8")
                self.assertTrue(self.checks.check_structure())

    def test_frontmatter_supports_quoted_text_and_colons(self) -> None:
        skill = self.package / "skills" / "mc-existing-vms" / "SKILL.md"
        for description in ('"Inspect VMs: read-only behavior"', "'Inspect a user''s VMs safely'", "Inspect existing VMs"):
            with self.subTest(description=description):
                skill.write_text(f"---\nname: mc-existing-vms\ndescription: {description}\n---\nBody\n", encoding="utf-8")
                self.assertEqual([], self.checks.check_structure())

    def test_invalid_json_is_reported_without_a_traceback(self) -> None:
        (self.package / ".mcp.json").write_text("{", encoding="utf-8")
        self.assertTrue(self.checks.check_structure())


if __name__ == "__main__":
    unittest.main()
