#!/bin/sh
set -eu
cd "$(dirname "$0")"
command -v openbox >/dev/null || { echo 'Instale openbox antes de continuar.'; exit 1; }
test -x .venv/bin/python || { echo 'Crie o ambiente .venv antes de continuar.'; exit 1; }
root=$(pwd)
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/themes/RoseShell/openbox-3"
cp themerc "$HOME/.local/share/themes/RoseShell/openbox-3/themerc"
printf '#!/bin/sh\nexec "%s/.venv/bin/python" "%s/session.py"\n' "$root" "$root" > "$HOME/.local/bin/roseshell-session"
chmod +x "$HOME/.local/bin/roseshell-session"
printf '#!/bin/sh\nexec "%s/.venv/bin/python" "%s/capture.py"\n' "$root" "$root" > "$HOME/.local/bin/roseshell-capture"
chmod +x "$HOME/.local/bin/roseshell-capture"
cp task-manager.sh "$HOME/.local/bin/roseshell-task-manager"
chmod +x "$HOME/.local/bin/roseshell-task-manager"
mkdir -p "$HOME/.local/share/applications"
printf '[Desktop Entry]\nType=Application\nName=Fastfetch\nGenericName=System summary\nGenericName[pt_BR]=Resumo do sistema\nExec=sh "%s/diagnostic-terminal.sh" fastfetch\nTerminal=true\nIcon=utilities-system-monitor\nCategories=System;Monitor;\n' "$root" > "$HOME/.local/share/applications/roseshell-fastfetch.desktop"
if [ "${1:-}" = '--user-only' ]; then
    echo 'Lancadores RoseShell atualizados para o usuario.'
    exit 0
fi
missing=''
for package in $(sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' packages-default.txt); do
    if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q 'install ok installed'; then
        missing="$missing $package"
    fi
done
if [ -n "$missing" ]; then
    sudo apt-get install -y $missing
fi
if ! dpkg-query -W -f='${Version}' tux-manager 2>/dev/null | grep -qx '1.0.8-1~deb13'; then
    sh install-tuxmanager.sh
fi
entry=$(mktemp)
trap 'rm -f "$entry"' EXIT
printf '[Desktop Entry]\nName=RoseShell\nComment=Ambiente RoseShell sobre Debian\nExec=%s/.local/bin/roseshell-session\nTryExec=%s/.local/bin/roseshell-session\nType=Application\nDesktopNames=RoseShell;\n' "$HOME" "$HOME" > "$entry"
sudo install -m 644 "$entry" /usr/share/xsessions/roseshell.desktop
echo 'Sessao RoseShell instalada. Disponivel no seletor de sessoes do login.'
