"""Release version checks used before publishing distribution artifacts."""

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_release import validate_release


@pytest.mark.parametrize(
    "version,prerelease",
    [
        ("2.0.0", False),
        ("2.0.1.post1", False),
        ("2.1.0a1", True),
        ("2.1.0b2", True),
        ("2.1.0rc1", True),
        ("2.1.0.dev1", True),
    ],
)
def test_release_classifies_pep440_versions(tmp_path, version, prerelease):
    project = tmp_path / "pyproject.toml"
    project.write_text(f'[project]\nversion = "{version}"\n')

    result = validate_release(f"v{version}", project)

    assert result.is_prerelease is prerelease


@pytest.mark.parametrize("tag", ["v2.0.1", "v2.0.0rc1", "2.0.0", "v", ""])
def test_release_rejects_tags_that_do_not_match_package(tmp_path, tag):
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nversion = "2.0.0"\n')

    with pytest.raises(ValueError, match="does not match package version"):
        validate_release(tag, project)


def test_release_rejects_invalid_package_version(tmp_path):
    project = tmp_path / "pyproject.toml"
    project.write_text('[project]\nversion = "invalid"\n')

    with pytest.raises(ValueError, match="Invalid version"):
        validate_release("vinvalid", project)


@pytest.mark.parametrize("version,prerelease", [("2.0.0", "false"), ("2.1.0rc1", "true")])
def test_release_command_outputs_github_metadata_outside_checkout(tmp_path, version, prerelease):
    root = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    script = scripts / "check_release.py"
    script.write_text((root / "scripts/check_release.py").read_text())
    (project / "pyproject.toml").write_text(f'[project]\nversion = "{version}"\n')

    result = subprocess.run(
        [sys.executable, str(script), f"v{version}"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == f"prerelease={prerelease}\n"


def test_release_command_fails_without_outputs_for_wrong_tag(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_release.py"), "v-not-the-package-version"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "does not match package version" in result.stderr
