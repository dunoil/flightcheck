"""Environment checks for a QNX SDP 8.0 development host."""
import os
import shutil
from dataclasses import dataclass


@dataclass
class Check:
    name: str
    status: str  # PASS, WARN, or FAIL
    detail: str
    fix: str = ""


def check_env_var(name):
    value = os.environ.get(name)
    if value and os.path.isdir(value):
        return Check(name, "PASS", f"{name}={value}")
    if value:
        return Check(name, "WARN", f"{name} is set to {value} but that path does not exist",
                     f"Re-run the QNX SDP 8.0 setup script (qnxsdp-env.sh) from your install.")
    return Check(name, "FAIL", f"{name} is not set",
                 "Install QNX SDP 8.0 via QNX Everywhere, then source qnxsdp-env.sh.")


def check_tool(name, fix):
    path = shutil.which(name)
    if path:
        return Check(name, "PASS", f"found at {path}")
    return Check(name, "FAIL", f"{name} not found on PATH", fix)


def run_doctor():
    checks = [
        check_env_var("QNX_HOST"),
        check_env_var("QNX_TARGET"),
        check_tool("qcc", "qcc ships with QNX SDP 8.0. Source qnxsdp-env.sh so QNX_HOST is on PATH."),
        check_tool("qemu-system-x86_64", "Install QEMU, or use the QNX Developer Desktop which bundles it."),
        check_tool("make", "Install GNU make from your OS package manager."),
        check_tool("python3", "Install Python 3.10 or newer."),
    ]
    home = os.path.expanduser("~")
    license_paths = [os.path.join(home, ".qnx", "license", "licenses"),
                     os.path.join(home, ".qnx", "licenses")]
    if any(os.path.exists(p) for p in license_paths):
        checks.append(Check("qnx-license", "PASS", "license file found under ~/.qnx"))
    else:
        checks.append(Check("qnx-license", "WARN", "no license file found under ~/.qnx",
                            "Activate your free QNX Everywhere license, then re-run doctor."))
    return checks


def format_report(checks):
    lines = ["FlightCheck doctor: QNX SDP 8.0 host report", ""]
    for c in checks:
        lines.append(f"[{c.status}] {c.name}: {c.detail}")
        if c.fix and c.status != "PASS":
            lines.append(f"       fix: {c.fix}")
    fails = sum(1 for c in checks if c.status == "FAIL")
    warns = sum(1 for c in checks if c.status == "WARN")
    lines.append("")
    lines.append(f"Summary: {fails} fail, {warns} warn, {len(checks) - fails - warns} pass.")
    lines.append("You are ready to build for QNX 8.0 in QEMU." if fails == 0
                 else "Fix the FAIL items above before building. WARN items will not block a QEMU build.")
    return "\n".join(lines)
