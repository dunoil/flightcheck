"""Scaffold a real-time QNX 8.0 C application that builds with qcc and runs in QEMU."""
import os

MAIN_C = r"""/*
 * {name}: a minimal real-time QNX 8.0 server.
 * Demonstrates channel based message passing and priority scheduling.
 */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/neutrino.h>
#include <sys/iofunc.h>
#include <sched.h>

int main(int argc, char *argv[]) {{
    /* Default channel flags keep QNX priority inheritance: a client that
       blocks this server lends it its priority, which bounds inversion. */
    int chid = ChannelCreate(0);
    if (chid == -1) {{
        fprintf(stderr, "ChannelCreate failed: %s\n", strerror(errno));
        return EXIT_FAILURE;
    }}

    struct sched_param params;
    params.sched_priority = 21;
    if (sched_setscheduler(0, SCHED_FIFO, &params) == -1) {{
        fprintf(stderr, "sched_setscheduler failed: %s\n", strerror(errno));
        return EXIT_FAILURE;
    }}

    printf("{name} ready on channel %d at priority %d\n", chid, params.sched_priority);
    fflush(stdout);

    char buffer[256];
    int rcvid;
    while (1) {{
        rcvid = MsgReceive(chid, buffer, sizeof(buffer), NULL);
        if (rcvid == -1) {{
            if (errno == EINTR) continue;
            fprintf(stderr, "MsgReceive failed: %s\n", strerror(errno));
            break;
        }}
        if (rcvid == 0) {{
            /* A pulse arrived. Handle _PULSE_CODE_DISCONNECT etc. here. */
            continue;
        }}
        /* TODO: parse the message in buffer, do the work, then MsgReply. */
        if (MsgReply(rcvid, EOK, "ok", 3) == -1) {{
            fprintf(stderr, "MsgReply failed: %s\n", strerror(errno));
        }}
    }}
    ChannelDestroy(chid);
    return EXIT_SUCCESS;
}}
"""

MAKEFILE = """# QNX 8.0 build. Requires QNX_HOST and QNX_TARGET from qnxsdp-env.sh.
CC = qcc
CFLAGS = -Vgcc_ntox86_64 -Wall -O2
TARGET = {name}

all: $(TARGET)

$(TARGET): main.c
\t$(CC) $(CFLAGS) -o $@ main.c

clean:
\trm -f $(TARGET)

.PHONY: all clean
"""

RUN_QEMU = """#!/bin/sh
# Boot the scaffolded app with mkqnximage, the image builder in QNX SDP 8.0.
# Add {name} to the data partition in local/snippets/data_files.custom,
# launch it from local/snippets/post_start.custom, then boot with
# qemu-system-x86_64 -kernel output/ifs.bin. Full commands: codelab step 5.
echo "Build first:  make"
echo "Then follow codelab step 5 to build the QEMU image and run {name}."
"""

README = """# {name}

A real-time QNX 8.0 server scaffolded by FlightCheck.

## Build
1. Install QNX SDP 8.0 via QNX Everywhere (free for non-commercial use).
2. Source the environment: `. $HOME/qnx800/qnxsdp-env.sh` (adjust to your install path).
3. Run `make`. This invokes qcc for the x86_64 QNX target.

## Run
Follow the FlightCheck codelab to build a QEMU system image with mkqnximage
and boot this binary, or copy it to any QNX 8.0 target and run it directly.

## What it shows
- ChannelCreate and MsgReceive message passing, the core QNX IPC pattern
- Fixed priority FIFO scheduling with sched_setscheduler
- Error handling on every QNX API call, checked by `flightcheck check`
"""


def scaffold(base_dir, name):
    target = os.path.join(base_dir, name)
    os.makedirs(target, exist_ok=True)
    # The Makefile TARGET must be a bare binary name, never a path. A reader
    # passing a path such as "apps/heartbeat" used to get TARGET = apps/heartbeat
    # and a failing make. The project directory keeps the full path; the
    # generated files use only the last component.
    app_name = os.path.basename(name.rstrip("/")) or name
    files = {
        "main.c": MAIN_C.format(name=app_name),
        "Makefile": MAKEFILE.format(name=app_name),
        "run-qemu.sh": RUN_QEMU.format(name=app_name),
        "README.md": README.format(name=app_name),
    }
    for fname, content in files.items():
        with open(os.path.join(target, fname), "w") as fh:
            fh.write(content)
    os.chmod(os.path.join(target, "run-qemu.sh"), 0o755)
    return target
