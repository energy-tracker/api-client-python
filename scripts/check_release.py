"""Validate the release tag against package metadata and report prerelease status."""

import argparse
import tomllib
from pathlib import Path

from packaging.version import Version


def validate_release(tag: str, project_file: Path) -> Version:
    with project_file.open("rb") as file:
        package_version = tomllib.load(file)["project"]["version"]
    version = Version(package_version)
    expected_tag = f"v{package_version}"
    if tag != expected_tag:
        raise ValueError(
            f"Release tag {tag!r} does not match package version: expected {expected_tag!r}"
        )
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Release tag, e.g. v2.0.0")
    args = parser.parse_args()
    project_file = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        version = validate_release(args.tag, project_file)
    except ValueError as error:
        parser.error(str(error))
    print(f"prerelease={str(version.is_prerelease).lower()}")


if __name__ == "__main__":
    main()
