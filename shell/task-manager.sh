#!/bin/sh
if command -v tux-manager >/dev/null; then
    exec tux-manager
fi
exec xfce4-taskmanager
