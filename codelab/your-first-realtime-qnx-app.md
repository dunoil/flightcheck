# Your First Real-Time QNX App in QEMU

Author: FlightCheck team
Summary: Go from an empty laptop to a real-time QNX 8.0 message passing server running in QEMU, using FlightCheck to check your setup, scaffold the app, and lint it.
id: your-first-realtime-qnx-app
categories: qnx, embedded, realtime
environments: Web
status: Draft
feedback link: https://qnx.devpost.com/

## Overview
Duration: 5

In this codelab you will:
1. Install QNX SDP 8.0 for free through QNX Everywhere.
2. Verify your host with `flightcheck doctor` and fix anything it flags.
3. Scaffold a real-time QNX server with `flightcheck init`.
4. Read the code and see the two patterns every QNX app is built on: message passing and priority scheduling.
5. Build with qcc and boot the app in QEMU.
6. Break the code on purpose, catch it with `flightcheck check`, and fix it.

You need: a Linux, macOS, or Windows host, Python 3.10 or newer, about 50 minutes, and no target hardware. QEMU is the target.

Verified end to end on 25 Nov 2026: QNX SDP 8.0 baseline 8.0.0.00141T202311271501L, qcc GCC 12.2.0, `flightcheck doctor` 7 PASS with 0 failures, and the scaffolded server booted live in QEMU.

## Get QNX SDP 8.0
Duration: 10

1. Create a free account at QNX Everywhere (qnx.software), accept the non-commercial Development License Agreement, and deploy the license to your own myQNX email in the myQNX License Manager.
2. Download QNX Software Center, install it, and use it to install QNX SDP 8.0, then activate the license key shown in your myQNX account.
3. In a terminal, source the environment script from your install directory. It sets QNX_HOST and QNX_TARGET, which every QNX tool depends on.

Positive: If `echo $QNX_HOST` prints your install path, the foundation is in place. The next step proves the rest automatically.

## Run flightcheck doctor
Duration: 5

Install FlightCheck and run the doctor:

```
pip install .
flightcheck doctor
```

Doctor checks the environment variables, the qcc toolchain, QEMU, make, Python, and your license file. Fix every FAIL using the fix instruction printed under it, then run doctor again until the summary shows zero failures.

Negative: Do not skip a FAIL and hope the build works anyway. A missing QNX_TARGET is the single most common cause of confusing qcc errors for new QNX developers, and doctor exists to catch it in seconds.

## Scaffold the app
Duration: 5

```
flightcheck init heartbeat_server
cd heartbeat_server
```

You now have `main.c`, a qcc `Makefile`, a `run-qemu.sh` script, and a README. This is a complete QNX program, not a stub.

## Read the two core patterns
Duration: 10

Open `main.c` and find:

1. Message passing: `ChannelCreate` opens a channel, and the server blocks in `MsgReceive`. Clients send, the server receives, does the work, and replies with `MsgReply`. This synchronous pattern is the heartbeat of QNX: drivers, servers, and applications all talk this way.
2. Priority scheduling: `sched_setscheduler` with SCHED_FIFO pins the server at priority 21. On QNX, when this thread is ready to run, it runs. That determinism is why QNX ships in vehicles and medical devices.

Notice that every QNX call is checked for failure. The codelab lint step shows why.

## Build and boot in QEMU
Duration: 10

Build for the x86_64 QNX target:

```
make
```

Then build a QEMU system image with mkqnximage, the image builder that ships with QNX SDP 8.0. In a working directory, run:

```
mkqnximage --type=qemu --noprompt --clean
```

Add the binary to the data partition by appending one line to `local/snippets/data_files.custom`:

```
[uid=0 gid=0 perms=755] heartbeat_server=/path/to/heartbeat_server/heartbeat_server
```

Start it at boot by appending to `local/snippets/post_start.custom`:

```
echo FLIGHTCHECK-DEMO-LAUNCH: starting /data/heartbeat_server
/data/heartbeat_server &
```

Rebuild the image, then boot it with the mkqnximage run recipe, which passes the IFS file as the QEMU kernel and attaches the disk image:

```
qemu-system-x86_64 -cpu max -smp 2 -m 1024 -drive file=output/disk-qemu.vmdk,if=ide,id=drv0 -nographic -kernel output/ifs.bin -object rng-random,filename=/dev/urandom,id=rng0 -device virtio-rng-pci,rng=rng0
```

You should see the server start during boot. This is the output from a verified run on QNX SDP 8.0 with qcc GCC 12.2.0 (your channel number and build date may differ, the shape of the output is the proof):

```
FLIGHTCHECK-DEMO-LAUNCH: starting /data/heartbeat_server
heartbeat_server ready on channel 1 at priority 21
Startup complete
QNX noname 8.0.0 2026/10/30-09:10:05EDT x86pc x86_64
```

The server created its channel, set FIFO priority 21, and is blocked in MsgReceive waiting for a client.

## Lint it, break it, fix it
Duration: 5

Run the linter on the clean scaffold:

```
flightcheck check main.c
```

It reports no findings. Now break it on purpose: replace the MsgReceive loop with a busy wait, and delete the `if (chid == -1)` error check after ChannelCreate:

```
    while (1) {
        sleep(1);
    }
```

Run check again. FlightCheck flags three problems: the busy wait loop with no blocking call (FC002), the sleep in a real-time path (FC003), and the channel with no MsgReceive loop (FC006). Note that FC001, the unchecked ChannelCreate rule, fires only when no error handling remains in the file at all, so if your file still checks errno anywhere, FC001 stays quiet. Restore the original code and confirm a clean report.

You now know the full loop: doctor, scaffold, build, boot, lint. Every QNX project you start from here reuses it.
