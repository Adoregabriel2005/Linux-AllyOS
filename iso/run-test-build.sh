#!/bin/sh
set -eu
test "$(id -u)" = 0
test "$(hostname)" = allyos-test
test "$(findmnt -n -o SOURCE /srv/allyos-builder)" = /dev/sdb
test -f /mnt/allyos-src/iso/release.json
version=$(python3 -c 'import json; print(json.load(open("/mnt/allyos-src/iso/release.json"))["version"])')
sources="/srv/allyos-builder/source-$version"
archive="/mnt/allyos-src/iso/build-preview-$version/config/includes.binary/sources/allyos-source-$version.tar.gz"
test -f "$archive"
if [ ! -d "$sources" ]; then
    temporary=$(mktemp -d "/srv/allyos-builder/source-$version.XXXXXX")
    tar -xzf "$archive" -C "$temporary"
    mv "$temporary" "$sources"
fi
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$sources/iso/release.json")" = "$version"
if [ "${ALLYOS_PUBLIC_BUILD:-0}" != 1 ] && [ -f /mnt/allyos-src/iso/local-assets/startup-local.wav ]; then
    mkdir -p "$sources/iso/local-assets"
    cp /mnt/allyos-src/iso/local-assets/startup-local.wav "$sources/iso/local-assets/startup-local.wav"
fi
export ALLYOS_BUILD_DIR="/srv/allyos-builder/build-$version"
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
if sh "$sources/iso/build.sh" >"/mnt/allyos-output/build-$version.log" 2>&1; then
    cp "$ALLYOS_BUILD_DIR/AllyOS-$version-dev-amd64.iso" /mnt/allyos-output/
    cp "$ALLYOS_BUILD_DIR/AllyOS-$version-dev-amd64.iso.sha256" /mnt/allyos-output/
    printf '0\n' >"/mnt/allyos-output/build-$version.exit"
else
    result=$?
    printf '%s\n' "$result" >"/mnt/allyos-output/build-$version.exit"
    exit "$result"
fi
