#!/bin/sh
set -eu
sudo mkdir -p /mnt/allyos-src
mountpoint -q /mnt/allyos-src || sudo mount -t vboxsf -o ro allyos-src /mnt/allyos-src
sudo apt-get update
sudo apt-get install -y live-build python3-pyside6.qtwidgets qml6-module-qtquick qml6-module-qtquick-controls qml6-module-qtquick-layouts qml6-module-qtquick-window qml6-module-qtquick-templates qml6-module-qtqml-workerscript xorriso squashfs-tools
target="$HOME/allyos-source"
mkdir -p "$target"
tar -C /mnt/allyos-src --exclude=iso/build-preview --exclude=shell/__pycache__ --exclude=shell/.venv -cf - iso shell docs LICENSE COPYRIGHT.md README.md | tar -C "$target" -xf -
python3 "$target/iso/prepare.py" --output "$HOME/allyos-build"
echo 'ALLYOS BUILDER READY'
