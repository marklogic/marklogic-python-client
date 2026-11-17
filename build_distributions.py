# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.

import argparse
import shutil
import subprocess
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=PROJECT_DIR / "dist")
    args = parser.parse_args()
    output_dir = args.output.resolve()

    version = subprocess.run(
        ["poetry", "version", "--short"],
        cwd=PROJECT_DIR,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ["poetry", "build", "--output", str(output_dir)],
        cwd=PROJECT_DIR,
        check=True,
    )
    sbom_name = f"marklogic_python_client-{version}.spdx.json"
    shutil.copyfile(PROJECT_DIR / "sbom.spdx.json", output_dir / sbom_name)
    print(f"Copy file {sbom_name}")


if __name__ == "__main__":
    main()
