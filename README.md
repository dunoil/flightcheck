# FlightCheck for QNX

FlightCheck takes a developer from zero to a running real-time QNX 8.0 application in QEMU, and keeps them out of the common traps along the way.

It is a host tool: it runs on Linux, macOS, or Windows with Python 3.10 or newer and zero dependencies. Everything it produces targets QNX 8.0: the scaffold is a QNX C server built with qcc, and the linter checks QNX specific API usage.

## Commands

### flightcheck doctor
Checks the host for a working QNX SDP 8.0 setup: the QNX_HOST and QNX_TARGET environment variables, the qcc toolchain, QEMU, make, Python, and the QNX license file. Every check reports PASS, WARN, or FAIL with a concrete fix instruction.

### flightcheck init <name>
Scaffolds a real-time QNX C application: a message passing server using ChannelCreate and MsgReceive, fixed priority FIFO scheduling, a qcc Makefile for the x86_64 target, a QEMU run script, and a README with build and run instructions.

### flightcheck check <files>
Lints QNX C sources for common mistakes: unchecked ChannelCreate results, busy wait loops, sleep calls in real-time paths, missing priority inheritance consideration, printf in real-time context, and channels with no MsgReceive loop.

## Quick start
```
pip install .
flightcheck doctor
flightcheck init heartbeat_server
flightcheck check heartbeat_server/main.c
```

Then follow the codelab in `codelab/` to build the scaffolded app with qcc and boot it in QEMU.

## Build and run details for the scaffolded app
- QNX version: QNX SDP 8.0 (QNX Everywhere, free for non-commercial use)
- Target: QEMU x86_64 (also runs on any QNX 8.0 x86_64 target)
- Toolchain: qcc with the gcc_ntox86_64 variant, GNU make

## License
MIT. See LICENSE.
