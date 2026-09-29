"""Validate distribution contents and import the installed wheel outside the checkout."""

import subprocess
import tarfile
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    wheels = list((root / "dist").glob("*.whl"))
    sdists = list((root / "dist").glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit("Expected exactly one wheel and one sdist; run make build first")

    with ZipFile(wheels[0]) as wheel:
        names = wheel.namelist()
        if "energy_tracker_api/py.typed" not in names:
            raise SystemExit("Wheel is missing py.typed")
        if any(
            not (name.startswith("energy_tracker_api/") or ".dist-info/" in name) for name in names
        ):
            raise SystemExit("Wheel contains files outside the package and its metadata")
    with tarfile.open(sdists[0]) as sdist:
        source_files = {name.partition("/")[2] for name in sdist.getnames()}
        if "energy_tracker_api/py.typed" not in source_files:
            raise SystemExit("Source distribution is missing py.typed")
        contract_files = {
            str(path.relative_to(root))
            for path in (root / "contracts").rglob("*")
            if path.is_file()
        }
        if "contracts/schema.json" not in contract_files or not contract_files <= source_files:
            raise SystemExit("Source distribution is missing shared API contracts")
        if not {"tests/test_contracts.py", "tests/conftest.py"} <= source_files:
            raise SystemExit("Source distribution is missing the API contract test runner")

    with tempfile.TemporaryDirectory(prefix="energy-tracker-wheel-") as directory:
        environment = venv.EnvBuilder(with_pip=True)
        environment.create(directory)
        python = Path(directory) / "bin" / "python"
        subprocess.run(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", str(wheels[0])],
            cwd=directory,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "from importlib.metadata import version; "
                "from importlib.resources import files; "
                "import energy_tracker_api as api; "
                "assert api.__version__ == version('energy-tracker-api'); "
                "assert files(api).joinpath('py.typed').is_file(); "
                "assert all(hasattr(api, name) for name in api.__all__); "
                "print('Installed wheel imports successfully:', api.__version__)",
            ],
            cwd=directory,
            check=True,
        )


if __name__ == "__main__":
    main()
