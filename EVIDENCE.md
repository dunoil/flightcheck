# FlightCheck: verified evidence

All results below were produced on 25 Nov 2026 on a Linux host, using the free QNX Everywhere non-commercial license for QNX SDP 8.0. No claim here is aspirational: every line was run and captured.

## Environment
- QNX SDP 8.0 baseline 8.0.0.00141T202311271501L, installed with QNX Software Center 2.0.4
- Toolchain: qcc, GCC 12.2.0, targets gcc_ntox86_64 (default) and gcc_ntoaarch64le
- QEMU: qemu-system-x86_64, installed on the host

## Unit tests
`python3 -m unittest` in this directory: 4 tests, all pass.

## flightcheck doctor
Run against the real SDP install:

```
FlightCheck doctor: QNX SDP 8.0 host report

[PASS] QNX_HOST
[PASS] QNX_TARGET
[PASS] qcc
[PASS] qemu-system-x86_64
[PASS] make
[PASS] python3
[PASS] qnx-license

Summary: 0 fail, 0 warn, 7 pass.
You are ready to build for QNX 8.0 in QEMU.
```

## qcc build
The scaffold from `flightcheck init heartbeat_server` compiled clean with the real qcc into an ELF 64-bit QNX binary (interpreter /usr/lib/ldqnx-64.so.2, 13,736 bytes).

## flightcheck check
`flightcheck check heartbeat_server/main.c` reports no findings. Breaking the scaffold on purpose (busy wait with sleep, deleted error check) is flagged with FC002, FC003, and FC006, as the codelab shows.

## QEMU boot
A mkqnximage QEMU image carrying heartbeat_server on its data partition was booted with qemu-system-x86_64, using the IFS file as the QEMU kernel. Console output:

```
FLIGHTCHECK-DEMO-LAUNCH: starting /data/heartbeat_server
heartbeat_server ready on channel 1 at priority 21
Startup complete
QNX noname 8.0.0 2026/10/30-09:10:05EDT x86pc x86_64
```

The server created its channel, set FIFO priority 21, and blocked in MsgReceive on a live QNX 8.0 system.
