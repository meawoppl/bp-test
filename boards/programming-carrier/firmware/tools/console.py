#!/usr/bin/env python3
"""Send fixture console commands over USB CDC and print the output.

  console.py PORT [--listen SECONDS] [COMMAND ...]

Each COMMAND is sent as a line; output is printed until it has been quiet
for a moment (or for --listen seconds after the last command).
"""
import argparse
import sys
import time

import serial


def drain(port, quiet_s, max_s):
    end = time.time() + max_s
    last = time.time()
    while time.time() < end:
        data = port.read(4096)
        if data:
            sys.stdout.write(data.decode(errors="replace"))
            sys.stdout.flush()
            last = time.time()
        elif time.time() - last > quiet_s:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port")
    ap.add_argument("--listen", type=float, default=0.0)
    ap.add_argument("commands", nargs="*")
    args = ap.parse_args()

    # Leave DTR/RTS deasserted: the ESP32-S2 USB console treats line-state
    # changes as reset/download requests, and toggling them wedged the console.
    port = serial.Serial()
    port.port, port.baudrate, port.timeout = args.port, 115200, 0.1
    port.dtr = port.rts = False
    with port:
        drain(port, 0.5, 2)
        for cmd in args.commands:
            port.write((cmd + "\r\n").encode())
            drain(port, 0.8, 10)
        if args.listen:
            drain(port, args.listen, args.listen)


if __name__ == "__main__":
    main()
