#!/usr/bin/env python3
"""Print or execute a safe /userdata vision model install plan."""

import argparse
import subprocess
from pathlib import Path


ADB = r"C:\Users\MR\Downloads\tool\tool\RKDevTool_Release_v2.92\RKDevTool_Release_v2.92\bin\adb.exe"


def run(cmd, execute):
    print(" ".join(cmd))
    if execute:
        subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--adb", default=ADB)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    artifact = Path(args.artifact_dir)
    if not artifact.exists():
        raise SystemExit("artifact dir not found: %s" % artifact)
    dest = "/userdata/smart_retail/models/vision"
    print("SAFE_INSTALL_TARGET %s" % dest)
    print("No boot/rootfs/oem/uboot writes. No database overwrite.")
    run([args.adb, "shell", "mkdir -p %s" % dest], args.execute)
    run([args.adb, "push", str(artifact), dest + "/"], args.execute)
    run([args.adb, "shell", "ls -lh %s" % dest], args.execute)
    if not args.execute:
        print("DRY_RUN add --execute only after artifact review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
