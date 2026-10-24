#!/bin/sh
set -eu
cd "$(dirname "$0")"
for spec in '640x480 1' '640x480 1.25' '1280x1024 1' '1920x1080 1' '3840x2160 1'; do
    set -- $spec
    Xephyr :2 -screen "$1" -nolisten tcp > /tmp/roseshell-resolution-x.log 2>&1 &
    rose_xpid=$!
    sleep 1
    if ! DISPLAY=:2 QT_SCALE_FACTOR="$2" .venv/bin/python verify_resolution.py; then
        kill "$rose_xpid" || true
        exit 1
    fi
    kill "$rose_xpid"
    wait "$rose_xpid" 2>/dev/null || true
done
