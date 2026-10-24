#!/bin/sh
set -eu
test "$(id -u)" = 0 || { echo 'Execute com sudo no terminal da VM.'; exit 1; }
build=/home/goriga/allyos-trixie-build
test -f "$build/allyos-build.json"
test -f "$build/config/bootstrap"
test "$(python3 -c 'import json; print(json.load(open("/home/goriga/allyos-trixie-build/allyos-build.json"))["codename"])')" = trixie
cd "$build"
test "$(pwd -P)" = /home/goriga/allyos-trixie-build
# An interrupted bootstrap restore leaves stale chroot stage markers.
# Clean generated stages only in this verified build; retain config and cache.
lb clean --all
version=$(python3 -c 'import json; print(json.load(open("allyos-build.json"))["version"])')
lb config --mode debian --distribution trixie --architecture amd64 \
    --binary-image iso-hybrid --bootloaders 'syslinux grub-efi' \
    --debian-installer live --archive-areas 'main contrib non-free non-free-firmware' \
    --security true --updates true --firmware-chroot true --firmware-binary true \
    --iso-application "AllyOS $version - Debian 13 / RoseShell" \
    --iso-volume "ALLYOS_$(printf '%s' "$version" | tr . _)" \
    --chroot-squashfs-compression-type zstd --chroot-squashfs-compression-level 15 \
    --bootappend-live 'boot=live components hostname=allyos username=ally locales=pt_BR.UTF-8 keyboard-layouts=br'
lb build
test -f live-image-amd64.hybrid.iso
version=$(python3 -c 'import json; print(json.load(open("allyos-build.json"))["version"])')
image="AllyOS-$version-dev-amd64.iso"
mv live-image-amd64.hybrid.iso "$image"
sha256sum "$image" > "$image.sha256"
cp "$image" "$image.sha256" /mnt/allyos-output/
echo "ISO gerada e exportada: $image"
