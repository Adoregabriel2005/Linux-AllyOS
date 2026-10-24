#!/bin/sh
set -eu
PATH="$PATH:/usr/sbin:/sbin"
export PATH
cd "$(dirname "$0")"
ROSESHELL_LANGUAGE=pt_BR .venv/bin/python verify_i18n.py
ROSESHELL_LANGUAGE=en .venv/bin/python verify_i18n.py
ROSESHELL_LANGUAGE=pt_BR .venv/bin/python verify.py
ROSESHELL_LANGUAGE=pt_BR sh resolution_checks.sh
ROSESHELL_LANGUAGE=en sh resolution_checks.sh
for program in fastfetch hardinfo2 sensors nvtop smartctl nvme gsmartcontrol inxi lshw dmidecode glxinfo vulkaninfo lsusb tux-manager; do
    command -v "$program"
done
fastfetch --version
dpkg-query -W tux-manager fastfetch hardinfo2 lm-sensors nvtop smartmontools gsmartcontrol
printf '\nRELEASE CHECKS OK\n'
