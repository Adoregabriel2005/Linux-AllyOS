#!/bin/sh
# Builder isolado no disco novo da VM descartável. Não usa o disco de sistema.
set -eu
test "$(id -u)" = 0
test "$(hostname)" = allyos-test
test "$(lsblk -dnbo SIZE /dev/sdb)" = 85899345920
test "$(lsblk -dno MODEL /dev/sdb | xargs)" = 'VBOX HARDDISK'
test "$(findmnt -n -o SOURCE /)" = /dev/sda1
if blkid /dev/sdb >/dev/null 2>&1; then
    test "$(blkid -s LABEL -o value /dev/sdb)" = ALLYBUILD
    test "$(blkid -s TYPE -o value /dev/sdb)" = ext4
else
    test -z "$(wipefs --noheadings /dev/sdb)"
    mkfs.ext4 -L ALLYBUILD /dev/sdb
fi
install -d /srv/allyos-builder
mountpoint -q /srv/allyos-builder || mount /dev/sdb /srv/allyos-builder
test "$(findmnt -n -o SOURCE /srv/allyos-builder)" = /dev/sdb
# Não mudar pacotes enquanto a auditoria lê os arquivos instalados.
while pgrep -fx 'dpkg --root=/ --verify' >/dev/null; do sleep 5; done
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso isolinux syslinux-common \
    grub-pc-bin grub-efi-amd64-bin mtools dosfstools dpkg-dev apt-utils \
    python3-yaml calamares calamares-settings-debian xserver-xephyr
printf 'BUILDER_READY\n'
