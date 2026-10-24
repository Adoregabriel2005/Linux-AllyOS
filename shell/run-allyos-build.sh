#!/bin/sh
set -eu
target="$HOME/allyos-source"
mkdir -p "$target"
tar -C /mnt/allyos-src --exclude=iso/build-preview --exclude=iso/output --exclude=shell/__pycache__ --exclude=shell/.venv -cf - iso shell docs LICENSE COPYRIGHT.md README.md | tar -C "$target" -xf -
cd "$target"
nohup sh iso/build.sh > "$HOME/allyos-build.log" 2>&1 < /dev/null &
printf 'ALLYOS BUILD PID=%s LOG=%s/allyos-build.log\n' "$!" "$HOME"
