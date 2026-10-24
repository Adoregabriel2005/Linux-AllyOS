#!/bin/sh
set -eu
cd "$(dirname "$0")"
packages=$(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' packages-default.txt)
sudo apt-get update
# A lista é controlada pelo projeto e contém somente nomes de pacotes.
sudo apt-get install -y $packages
sh install-tuxmanager.sh
echo 'Base RoseShell instalada, incluindo SuperTux.'
