"""FlightCheck command line interface: doctor, init, check."""
import argparse
import os
import sys

from . import __version__
from .doctor import run_doctor, format_report
from .lint import lint_source, format_findings
from .scaffold import scaffold


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flightcheck",
                                     description="FlightCheck for QNX: doctor, scaffold, and lint QNX 8.0 projects.")
    parser.add_argument("--version", action="version", version=f"flightcheck {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check this host for a working QNX SDP 8.0 setup.")

    p_init = sub.add_parser("init", help="Scaffold a real-time QNX C application.")
    p_init.add_argument("name", help="Project name (also the binary name).")
    p_init.add_argument("--dir", default=".", help="Parent directory for the new project.")

    p_check = sub.add_parser("check", help="Lint QNX C sources for common mistakes.")
    p_check.add_argument("paths", nargs="+", help="C source files to check.")

    args = parser.parse_args(argv)

    if args.command == "doctor":
        checks = run_doctor()
        print(format_report(checks))
        return 1 if any(c.status == "FAIL" for c in checks) else 0

    if args.command == "init":
        target = scaffold(args.dir, args.name)
        print(f"Scaffolded QNX 8.0 project at {target}")
        print("Next: source qnxsdp-env.sh, cd into the project, run make.")
        return 0

    if args.command == "check":
        total = 0
        for path in args.paths:
            with open(path) as fh:
                findings = lint_source(fh.read())
            total += len(findings)
            print(format_findings(findings, path))
        return 1 if total else 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
