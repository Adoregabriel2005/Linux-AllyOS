#!/bin/sh
set -eu
cd "$(dirname "$0")"
# Pacote oficial Debian 13 amd64, fixado e conferido pelo digest da release.
file='vendor/tux-manager_1.0.8-1.deb13_amd64.deb'
digest='77f14af3305cb8cf09faf027812e906a845ea281a2fb95795360b9db01b2b4d7'
test "$(dpkg --print-architecture)" = amd64 || { echo 'Pacote TuxManager requer amd64.'; exit 1; }
printf '%s  %s\n' "$digest" "$file" | sha256sum -c -
staged=$(mktemp /tmp/roseshell-tuxmanager-XXXXXX.deb)
trap 'rm -f "$staged"' EXIT
cp "$file" "$staged"
chmod 644 "$staged"
sudo apt-get install -y "$staged"
