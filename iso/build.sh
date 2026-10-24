#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v lb >/dev/null || { echo 'Instale live-build no Debian 13 amd64.'; exit 1; }
test "$(dpkg --print-architecture)" = amd64 || { echo 'Builder requer Debian amd64.'; exit 1; }
output=${ALLYOS_BUILD_DIR:-"$HOME/allyos-build"}
if [ -f "$output/chroot/usr/lib/os-release" ] && ! grep -q '^VERSION_CODENAME=trixie$' "$output/chroot/usr/lib/os-release"; then
    echo 'Cache de outra distribuição detectado. Escolha uma pasta nova com ALLYOS_BUILD_DIR.'
    exit 1
fi
ally_version=$(python3 -c 'import json; print(json.load(open("iso/release.json"))["version"])')
ally_label="ALLYOS_$(printf '%s' "$ally_version" | tr . _)"
python3 iso/prepare.py --output "$output"
cd "$output"
# Hooks/config e os pacotes locais foram preparados antes de lb config.
sudo lb config --mode debian --distribution trixie --architecture amd64 \
    --binary-image iso-hybrid --bootloaders 'syslinux grub-efi' \
    --debian-installer false --archive-areas 'main contrib non-free non-free-firmware' \
    --security true --updates true --firmware-chroot true --firmware-binary true \
    --iso-application "AllyOS $ally_version - Debian 13 / RoseShell" \
    --iso-volume "$ally_label" \
    --chroot-squashfs-compression-type zstd --chroot-squashfs-compression-level 8 \
    --bootappend-live 'boot=live components nottyautologin hostname=allyos username=ally locales=pt_BR.UTF-8 keyboard-layouts=br timezone=America/Sao_Paulo'
sudo lb build
test -f live-image-amd64.hybrid.iso
mv live-image-amd64.hybrid.iso "AllyOS-$ally_version-dev-amd64.iso"
sha256sum "AllyOS-$ally_version-dev-amd64.iso" > "AllyOS-$ally_version-dev-amd64.iso.sha256"
echo "ISO gerada em $output/AllyOS-$ally_version-dev-amd64.iso"
