"""Overlay AllyOS sobre as configurações oficiais Debian do Calamares 3.3."""
import hashlib
from pathlib import Path
import tarfile
from profiles import recommended_extras

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'iso/vendor/calamares-settings-debian_13.0.13.orig.tar.bz2'
SHA256 = '0a6f9e243c3ea5fdaa702deaeac67ffb59692ca95b16b402f6b2e7ea08f05020'


def prepare_installer(output, version):
    from prepare import put, copy
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == SHA256
    overlay = output / 'config/includes.chroot'
    prefix = 'calamares-settings-debian-13.0.13/'
    with tarfile.open(ARCHIVE) as archive:
        for member in archive.getmembers():
            # Ler apenas arquivos conhecidos; nunca extrair links ou caminhos arbitrários.
            if member.isfile() and member.name.startswith(prefix + 'calamares/'):
                relative = member.name[len(prefix + 'calamares/'):]
                if '..' in Path(relative).parts:
                    raise ValueError(relative)
                data = archive.extractfile(member).read()
                target = overlay / 'etc/calamares' / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        license_text = archive.extractfile(prefix + 'COPYING').read().decode()
        media_helper = archive.extractfile(prefix + 'helpers/calamares-sources-media').read().decode()
        final_helper = archive.extractfile(prefix + 'helpers/calamares-sources-final').read().decode()
    put(overlay, 'usr/share/doc/allyos-installer/Debian-COPYING', license_text)
    # Fontes temporárias do live-build não devem sobreviver no sistema alvo.
    # O repositório da mídia contém os dois conjuntos de GRUB e suas dependências.
    media_helper = media_helper.replace('rm -f $CHROOT/etc/apt/sources.list.d/base.list', '''for file in base.list zz-sources.list packages.list; do
    rm -f "$CHROOT/etc/apt/sources.list.d/$file"
done
rm -f "$CHROOT/etc/apt/sources.list"''')
    final_helper = final_helper.replace('main non-free-firmware', 'main contrib non-free non-free-firmware')
    put(overlay, 'usr/share/calamares/helpers/calamares-sources-media', media_helper, True)
    put(overlay, 'usr/share/calamares/helpers/calamares-sources-final', final_helper, True)
    package_config = overlay / 'etc/calamares/modules/packages.conf'
    # Our image does not install Debian Live task metapackages. With only the
    # offline bootloader repository active, APT cannot resolve absent names.
    put(overlay, 'etc/calamares/modules/packages.conf', '''backend: apt
operations:
  - remove:
      - live-boot
      - live-config
      - live-config-systemd
      - live-tools
      - calamares-settings-debian
      - calamares
''')
    settings = overlay / 'etc/calamares/settings.conf'
    text = settings.read_text(encoding='utf-8').replace('branding: debian', 'branding: allyos')
    text = text.replace('  - users\n  - summary', '  - users\n  - packagechooser\n  - summary')
    text = text.replace('  - packages\n', '  - contextualprocess@allyos-profile\n  - packages\n')
    text = text.replace('prompt-install: false', 'prompt-install: true')
    text += '\ninstances:\n  - id: allyos-profile\n    module: contextualprocess\n    config: allyos-profile.conf\n'
    text += 'hide-back-and-next-during-exec: false\n'
    settings.write_text(text, encoding='utf-8', newline='\n')
    put(overlay, 'etc/calamares/modules/locale.conf', '---\nregion: America\nzone: Sao_Paulo\nuseSystemTimezone: false\ngeoip:\n  style: none\n')
    welcome = overlay / 'etc/calamares/modules/welcome.conf'
    welcome.write_text(welcome.read_text(encoding='utf-8').replace('showSupportUrl:         true', 'showSupportUrl:         false').replace('showKnownIssuesUrl:     true', 'showKnownIssuesUrl:     false').replace('showReleaseNotesUrl:    true', 'showReleaseNotesUrl:    false'), encoding='utf-8', newline='\n')
    put(overlay, 'etc/calamares/modules/packagechooser.conf', '''---
mode: required
method: legacy
default: full
labels:
  step: Applications
  step[pt_BR]: Aplicativos
items:
  - id: full
    name: Recommended applications
    name[pt_BR]: Pacote recomendado
    description: Firefox ESR, Wine, hardware diagnostics, TuxManager and Fastfetch. SuperTux is included in both profiles.
    description[pt_BR]: Firefox ESR, Wine, diagnóstico de hardware, TuxManager e Fastfetch. SuperTux está nos dois perfis.
    screenshot: welcome.png
  - id: minimal
    name: Essential desktop
    name[pt_BR]: Área de trabalho essencial
    description: RoseShell, files, text editor, terminal, task manager, network, audio and SuperTux.
    description[pt_BR]: RoseShell, arquivos, editor de texto, terminal, tarefas, rede, áudio e SuperTux.
    screenshot: welcome.png
''')
    put(overlay, 'etc/calamares/modules/allyos-profile.conf', '''---
dontChroot: false
timeout: 600
packagechooser_packagechooser:
  full: /usr/lib/allyos-installer/select-profile full
  minimal: /usr/lib/allyos-installer/select-profile minimal
  "*": /bin/false
''')
    put(overlay, 'etc/calamares/modules/partition.conf', '''---
efi:
  mountPoint: /boot/efi
  recommendedSize: 512MiB
  minimumSize: 300MiB
allowManualPartitioning: true
initialPartitioningChoice: none
defaultFileSystemType: ext4
userSwapChoices: [small, none, suspend]
initialSwapChoice: small
drawNestedPartitions: true
alwaysShowPartitionLabels: true
''')
    put(overlay, 'etc/calamares/modules/displaymanager.conf', '''---
displaymanagers: [sddm]
defaultDesktopEnvironment:
  executable: roseshell-session
  desktopFile: roseshell
basicSetup: false
sysconfigSetup: false
''')
    # Preserva todas as tarefas Debian de boot, initramfs, fontes APT e limpeza Live.
    branding = (overlay / 'etc/calamares/branding/debian/branding.desc').read_text(encoding='utf-8')
    branding = branding.replace('componentName:   debian', 'componentName:   allyos')
    branding = branding.replace('welcomeStyleCalamares: true', 'welcomeStyleCalamares: false')
    branding = branding.replace('Debian GNU/Linux', 'AllyOS · Debian GNU/Linux')
    branding = branding.replace('shortProductName:    Debian', 'shortProductName:    AllyOS')
    branding = branding.replace('version:             13', 'version:             "' + version + '"')
    branding = branding.replace('shortVersion:        13', 'shortVersion:        "' + version + '"')
    branding = branding.replace('Debian 13', 'AllyOS ' + version + ' (Debian 13)')
    branding = branding.replace('bootloaderEntryName: Debian', 'bootloaderEntryName: AllyOS')
    branding = branding.replace('debian-logo.png', 'allyos.svg').replace('welcome.png', 'welcome.png')
    branding = branding.replace('"#26475b"', '"#191c1e"').replace('"#265370"', '"#64434e"')
    put(overlay, 'etc/calamares/branding/allyos/branding.desc', branding)
    put(overlay, 'etc/calamares/branding/allyos/stylesheet.qss', '''QWidget { background: #222629; color: #eee7dc; }
QPushButton { background: #343a3d; border: 1px solid #737a78; padding: 6px 12px; border-radius: 0; }
QPushButton:hover { background: #654650; }
QPushButton:disabled { color: #8a8c89; border-color: #444b4d; }
QLineEdit, QComboBox, QListView { background: #171c1e; border: 1px solid #717977; padding: 4px; selection-background-color: #835b69; }
QProgressBar { border: 1px solid #717977; text-align: center; }
QProgressBar::chunk { background: #bd8b9a; }
QToolTip { background: #eee7dc; color: #191c1e; border: 1px solid #737a78; }
''')
    put(overlay, 'etc/calamares/branding/allyos/show.qml', '''// Copyright 2026 gorigamia. GPL-3.0-or-later.
import QtQuick 2.15
import calamares.slideshow 1.0
Presentation {
    Slide {
        Rectangle { anchors.fill: parent; color: "#191c1e" }
        Column {
            anchors.centerIn: parent
            width: parent.width - 48
            spacing: 20
            Text { text: "AllyOS · RoseShell"; color: "#eee7dc"; font.pixelSize: 28; width: parent.width; wrapMode: Text.WordWrap }
            Rectangle { width: parent.width; height: 2; color: "#c58f9d" }
            Text {
                text: Qt.locale().name.indexOf("pt") === 0 ? "Criado por gorigamia. Base Debian GNU/Linux 13.\\nPreparando seu ambiente de trabalho." : "Created by gorigamia. Based on Debian GNU/Linux 13.\\nPreparing your desktop."
                color: "#b9c7bf"; font.pixelSize: 17; width: parent.width; wrapMode: Text.WordWrap
            }
        }
    }
}
''')
    put(overlay, 'etc/calamares/branding/allyos/allyos.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#191c1e"/><path d="M10 54 28 10h8l18 44H43L32 25 21 54z" fill="#c58f9d"/></svg>')
    # A recepção e os perfis usam somente a identidade gráfica, sem retrato.
    branding_path = overlay / 'etc/calamares/branding/allyos/branding.desc'
    branding_path.write_text(branding_path.read_text(encoding='utf-8').replace('welcome.png', 'allyos.svg'), encoding='utf-8', newline='\n')
    chooser = overlay / 'etc/calamares/modules/packagechooser.conf'
    chooser.write_text(chooser.read_text(encoding='utf-8').replace('screenshot: welcome.png', 'screenshot: allyos.svg'), encoding='utf-8', newline='\n')
    extras = recommended_extras() + ['wine32:i386']
    put(overlay, 'usr/lib/allyos-installer/select-profile', '''#!/bin/sh
set -eu
test "$(id -u)" = 0
grep -q '^ID=allyos$' /usr/lib/os-release
case "${1:-}" in
 full) ;;
 minimal)
  # Preservar explicitamente sessão, kernel, firmware e bootloader antes de
  # retirar aplicativos e bibliotecas que só pertenciam ao perfil completo.
  apt-mark manual allyos-desktop allyos-branding linux-image-amd64 sudo locales systemd-sysv
  firmware=$(dpkg-query -W -f='${db:Status-Status} ${binary:Package}\\n' 'firmware-*' | awk '$1 == "installed" {print $2}')
  if [ -n "$firmware" ]; then apt-mark manual $firmware; fi
  for package in grub-pc grub-efi grub-efi-amd64 grub-efi-amd64-signed shim-signed; do
    if dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q 'install ok installed'; then
      apt-mark manual "$package"
    fi
  done
  export DEBIAN_FRONTEND=noninteractive LC_ALL=C
  apt-get -s --autoremove remove allyos-apps ''' + ' '.join(extras) + ''' > /var/log/allyos-minimal-plan.log
  if grep -Eq '^Remv (allyos-desktop|allyos-branding|openbox|linux-image|linux-base|initramfs-|systemd|grub-|shim-|firmware-)' /var/log/allyos-minimal-plan.log; then
    echo 'Recusado: plano removeria um componente essencial.' >&2
    exit 1
  fi
  apt-get -y --autoremove remove allyos-apps ''' + ' '.join(extras) + '''
  ;;
 *) exit 2 ;;
esac
install -d /var/lib/allyos
printf '%s\\n' "$1" > /var/lib/allyos/install-profile
rm -f /usr/share/applications/allyos-install.desktop
''', True)
    put(overlay, 'usr/share/applications/allyos-install.desktop', '''[Desktop Entry]
Type=Application
Name=Install AllyOS
Name[pt_BR]=Instalar AllyOS
Exec=calamares-install-debian
TryExec=calamares
Icon=allyos
Categories=System;
''')
