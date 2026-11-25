"""Static checks for common QNX programming mistakes in C sources."""
import re
from dataclasses import dataclass


@dataclass
class Finding:
    rule: str
    line: int
    message: str


BLOCKING_CALLS = ("MsgReceive", "MsgReceivePulse", "TimerWait", "MsgSend", "pause(", "sigsuspend", "select(", "poll(")


def _loop_body(lines, start, span=20):
    return "\n".join(lines[start:start + span])


def lint_source(text):
    findings = []
    lines = text.splitlines()
    has_channel_create = "ChannelCreate" in text
    has_error_check = ("== -1" in text) or ("< 0" in text) or ("errno" in text)
    mentions_priority_flags = ("_NTO_CHF" in text) or ("priority inheritance" in text.lower())

    for i, line in enumerate(lines, start=1):
        if re.search(r"=\s*ChannelCreate\s*\(", line) and not has_error_check:
            findings.append(Finding("FC001-channelcreate-unchecked", i,
                                    "ChannelCreate result has no error check in this file: test it against -1 and handle errno before use."))
        if "ChannelCreate" in line and not mentions_priority_flags:
            findings.append(Finding("FC004-no-priority-inheritance", i,
                                    "ChannelCreate with default flags: confirm priority behavior for your clients, or pass _NTO_CHF flags explicitly and document the choice."))
        if re.search(r"\b(sleep|usleep)\s*\(", line):
            findings.append(Finding("FC003-sleep-in-rt-path", i,
                                    "Sleep call found: in a real-time path prefer timer based waits (TimerCreate, ClockPeriod) so latency stays bounded."))
        if re.search(r"while\s*\(\s*1\s*\)|for\s*\(\s*;\s*;", line):
            body = _loop_body(lines, i - 1)
            if not any(call in body for call in BLOCKING_CALLS):
                findings.append(Finding("FC002-busy-wait", i,
                                        "Infinite loop with no blocking call in its body: a QNX server loop should block on MsgReceive or a timer instead of busy waiting."))
            if "printf" in body and "MsgReceive" not in body:
                findings.append(Finding("FC005-printf-in-rt-loop", i,
                                        "printf inside a non blocking loop: route logging through a low priority logger thread so it cannot stall real-time work."))

    if has_channel_create and "MsgReceive" not in text:
        findings.append(Finding("FC006-no-msgreceive", 1,
                                "ChannelCreate without MsgReceive: a QNX server channel should block on MsgReceive to receive client pulses and messages."))
    return findings


def format_findings(findings, path):
    if not findings:
        return f"{path}: no FlightCheck findings. Nice work."
    out = [f"{path}: {len(findings)} finding(s)"]
    for f in findings:
        out.append(f"  line {f.line} [{f.rule}] {f.message}")
    return "\n".join(out)
