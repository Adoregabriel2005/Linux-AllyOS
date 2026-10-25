"""Prepara pacotes locais e configuração live-build; nunca copia a VM instalada."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tarfile
from profiles import package_names, recommended_extras

ROOT = Path(__file__).resolve().parents[1]
RELEASE = json.loads((ROOT / 'iso/release.json').read_text(encoding='utf-8'))
VERSION = RELEASE['version']
if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', VERSION):
    raise ValueError('Versão deve ter formato release.revisão.compilação')


def put(root, name, content, executable=False):
    path = root / name.lstrip('/')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')
    if executable:
        path.chmod(0o755)


def copy(source, root, name):
    target = root / name.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def control(root, name, depends, description):
    put(root, 'DEBIAN/control', f'Package: {name}\nVersion: {VERSION}-1\nArchitecture: all\nMaintainer: gorigamia\nSection: x11\nPriority: optional\nDepends: {depends}\nDescription: {description}\n')
    copy(ROOT / 'COPYRIGHT.md', root, f'usr/share/doc/{name}/copyright')
    copy(ROOT / 'LICENSE', root, f'usr/share/doc/{name}/LICENSE')


def stage_packages(staging):
    branding = staging / 'allyos-branding'
    control(branding, 'allyos-branding', 'base-files, init-system-helpers', 'AllyOS identity, Debian base and RoseShell login theme')
    with (branding / 'DEBIAN/control').open('a') as metadata:
        metadata.write('Provides: sddm-theme\n')
    release = (f'NAME="AllyOS"\nPRETTY_NAME="AllyOS {VERSION} (Debian 13)"\nID=allyos\nID_LIKE=debian\n'
               f'VERSION="{VERSION} (development; Debian 13 trixie)"\nVERSION_ID="{VERSION}"\n'
               'VERSION_CODENAME=trixie\nDEBIAN_CODENAME=trixie\nDEBIAN_VERSION_ID=13\n'
               'VARIANT="RoseShell"\nVARIANT_ID=roseshell\nLOGO=allyos\n')
    put(branding, 'usr/lib/os-release', release)
    put(branding, 'etc/lsb-release', f'DISTRIB_ID=AllyOS\nDISTRIB_RELEASE={VERSION}\nDISTRIB_CODENAME=trixie\nDISTRIB_DESCRIPTION="AllyOS {VERSION} (Debian 13)"\n')
    put(branding, 'usr/share/allyos/release.json', json.dumps(RELEASE, indent=2) + '\n')
    put(branding, 'DEBIAN/preinst', '''#!/bin/sh
set -e
case "$1" in install|upgrade)
 dpkg-divert --package allyos-branding --add --rename --divert /usr/lib/os-release.debian /usr/lib/os-release
esac
''', True)
    put(branding, 'DEBIAN/postrm', '''#!/bin/sh
set -e
case "$1" in remove|purge)
 dpkg-divert --package allyos-branding --remove --rename --divert /usr/lib/os-release.debian /usr/lib/os-release
esac
''', True)
    logo = '     /\\      AllyOS\n    /  \\     RoseShell\n   / /\\ \\    Debian inside\n  /_/  \\_\\\n'
    put(branding, 'usr/share/allyos/ascii.txt', logo)
    put(branding, 'usr/share/icons/hicolor/scalable/apps/allyos.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#191c1e"/><path d="M10 54 28 10h8l18 44H43L32 25 21 54z" fill="#c58f9d"/><path d="M22 42h20" stroke="#b7cbbc" stroke-width="5"/></svg>\n')
    fetch = {'logo': {'type': 'file', 'source': '/usr/share/allyos/ascii.txt'}, 'modules': [
        'title', 'separator', 'os', {'type': 'custom', 'key': 'Base', 'format': 'Debian GNU/Linux 13 (trixie)'},
        'host', 'kernel', 'uptime', 'packages', 'shell', 'display', 'de', 'wm', 'cpu', 'gpu', 'memory', 'disk']}
    put(branding, 'etc/xdg/fastfetch/config.jsonc', json.dumps(fetch, indent=2) + '\n')
    neoconfig = '''print_info() {
    info title
    info underline
    info "OS" distro
    prin "Base" "Debian GNU/Linux 13 (trixie)"
    info "Host" model
    info "Kernel" kernel
    info "Uptime" uptime
    info "Packages" packages
    info "Shell" shell
    info "Resolution" resolution
    info "DE" de
    info "WM" wm
    info "CPU" cpu
    info "GPU" gpu
    info "Memory" memory
}
distro_shorthand="off"
image_backend="ascii"
image_source="/usr/share/allyos/ascii.txt"
ascii_colors=(5 7)
'''
    put(branding, 'etc/skel/.config/neofetch/config.conf', neoconfig)
    for source in (ROOT / 'iso/sddm').iterdir():
        content = source.read_text(encoding='utf-8')
        if source.name == 'metadata.desktop':
            content = re.sub(r'^Version=.*$', 'Version=' + VERSION, content, flags=re.MULTILINE)
        put(branding, 'usr/share/sddm/themes/allyos/' + source.name, content)
    copy(ROOT / 'shell/assets/wallpapers/01-jardim-de-jade.png', branding, 'usr/share/sddm/themes/allyos/background.png')
    put(branding, 'usr/share/sddm/themes/allyos/theme.conf', f'[General]\nsystemName=AllyOS {VERSION}\nbaseLabel=RoseShell · Debian GNU/Linux 13\nLanguage=pt_BR\nPreviewMode=false\n')
    put(branding, 'etc/sddm.conf.d/10-allyos.conf', '[General]\nDisplayServer=x11\nInputMethod=\nGreeterEnvironment=QT_QUICK_BACKEND=software\n[Theme]\nCurrent=allyos\n')
    copy(ROOT / 'iso/virtualbox-display.sh', branding, 'usr/lib/allyos/virtualbox-display')
    (branding / 'usr/lib/allyos/virtualbox-display').chmod(0o755)
    put(branding, 'usr/lib/systemd/system/allyos-virtualbox-display.service', '''[Unit]
Description=AllyOS VirtualBox display compatibility
Before=sddm.service display-manager.service
ConditionPathExists=/sys/class/dmi/id/product_name

[Service]
Type=oneshot
ExecStart=/usr/lib/allyos/virtualbox-display
RemainAfterExit=yes

[Install]
WantedBy=graphical.target
''')
    put(branding, 'DEBIAN/postinst', '''#!/bin/sh
set -e
if [ "$1" = configure ]; then
 deb-systemd-helper enable allyos-virtualbox-display.service >/dev/null
fi
''', True)

    desktop = staging / 'allyos-desktop'
    packages = package_names('packages-minimal.txt')
    required = packages + ['python3-pyside6.qtwidgets', 'sddm', 'qml6-module-qtquick', 'qml6-module-qtquick-controls',
        'qml6-module-qtquick-layouts', 'qml6-module-qtquick-window', 'qml6-module-qtquick-templates',
        'qml6-module-qtqml-workerscript', 'xserver-xorg', 'qterminal', 'featherpad',
        'adwaita-icon-theme', 'xdg-utils', 'network-manager', 'allyos-branding',
        'qt6-image-formats-plugins', 'qt6-qpa-plugins', 'libqt6svg6', 'pipewire-audio', 'wireplumber', 'alsa-utils', 'dbus-user-session']
    control(desktop, 'allyos-desktop', ', '.join(dict.fromkeys(required)), 'RoseShell default desktop for AllyOS, based on Debian')
    for source in (ROOT / 'shell').iterdir():
        if source.is_file() and source.suffix in ('.py', '.sh', '.txt') and not source.name.startswith(('verify', 'demo_', 'install-', 'preview', 'resolution_', 'prepare-', 'vm-', 'test-', 'run-allyos-', 'export-allyos-')):
            copy(source, desktop, 'usr/lib/roseshell/' + source.name)
    copy(ROOT / 'shell/LICENSE', desktop, 'usr/lib/roseshell/LICENSE')
    copy(ROOT / 'shell/openbox.xml', desktop, 'usr/lib/roseshell/openbox.xml')
    copy(ROOT / 'shell/themerc', desktop, 'usr/share/themes/RoseShell/openbox-3/themerc')
    shutil.copytree(ROOT / 'shell/assets/wallpapers', desktop / 'usr/lib/roseshell/assets/wallpapers')
    shutil.copytree(ROOT / 'shell/assets/sounds', desktop / 'usr/lib/roseshell/assets/sounds')
    local_sound = ROOT / 'iso/local-assets/startup-local.wav'
    if local_sound.is_file() and os.environ.get('ALLYOS_PUBLIC_BUILD') != '1':
        copy(local_sound, desktop, 'usr/lib/roseshell/assets/sounds/startup-local.wav')
    copy(ROOT / 'shell/assets/icons/wine-hand.png', desktop, 'usr/share/pixmaps/allyos-wine.png')
    copy(ROOT / 'shell/assets/icons/wine-hand.png', desktop, 'usr/lib/roseshell/assets/icons/wine-hand.png')
    for command, module in [('roseshell-session', 'session.py'), ('roseshell-capture', 'capture.py'), ('roseshell-wine', 'wine_launcher.py')]:
        put(desktop, 'usr/bin/' + command, f'#!/bin/sh\nexec /usr/bin/python3 /usr/lib/roseshell/{module} "$@"\n', True)
    copy(ROOT / 'shell/task-manager.sh', desktop, 'usr/bin/roseshell-task-manager')
    (desktop / 'usr/bin/roseshell-task-manager').chmod(0o755)
    put(desktop, 'usr/share/xsessions/roseshell.desktop', '[Desktop Entry]\nName=RoseShell\nComment=AllyOS desktop on Debian\nExec=/usr/bin/roseshell-session\nTryExec=/usr/bin/roseshell-session\nType=Application\nDesktopNames=RoseShell;\n')
    put(desktop, 'usr/share/applications/allyos-fastfetch.desktop', '[Desktop Entry]\nName=Fastfetch\nType=Application\nTryExec=fastfetch\nExec=sh /usr/lib/roseshell/diagnostic-terminal.sh fastfetch\nTerminal=true\nIcon=utilities-system-monitor\nCategories=System;Monitor;\n')
    put(desktop, 'usr/share/applications/allyos-wine.desktop', '[Desktop Entry]\nName=Wine — Windows applications\nName[pt_BR]=Wine — Aplicativos Windows\nType=Application\nExec=roseshell-wine %f\nTryExec=wine\nIcon=/usr/share/pixmaps/allyos-wine.png\nMimeType=application/x-ms-dos-executable;application/x-msdownload;application/vnd.microsoft.portable-executable;application/x-msi;\nCategories=System;Emulator;\n')
    put(desktop, 'etc/skel/.dmrc', '[Desktop]\nSession=roseshell\n')
    put(desktop, 'etc/NetworkManager/conf.d/10-allyos.conf', '[ifupdown]\nmanaged=true\n')
    put(desktop, 'etc/skel/.config/RoseShell/Desktop.conf', '[General]\ntheme=dark\nside=left\nscale=1\nkeyboard=br\nlanguage=pt_BR\nperformance=economy\nwallpaper=/usr/lib/roseshell/assets/wallpapers/01-jardim-de-jade.png\nwallpaper_mode=fit\n')
    put(desktop, 'DEBIAN/postinst', '''#!/bin/sh
set -e
if [ "$1" = configure ] && [ ! -e /var/lib/sddm/state.conf ]; then
 install -d -m 755 /var/lib/sddm
 printf '[Last]\nSession=/usr/share/xsessions/roseshell.desktop\n' > /var/lib/sddm/state.conf
 chown sddm:sddm /var/lib/sddm/state.conf
fi
''', True)

    neo = staging / 'neofetch'
    control(neo, 'neofetch', 'bash', 'Original Neofetch 7.1.0 for AllyOS (upstream archived)')
    text = (neo / 'DEBIAN/control').read_text().replace(f'Version: {VERSION}-1', 'Version: 7.1.0+allyos1')
    put(neo, 'DEBIAN/control', text)
    source = ROOT / 'iso/vendor/neofetch'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == '3dc33493e54029fb1528251552093a9f9a2894fcf94f9c3a6f809136a42348c7'
    copy(source, neo, 'usr/bin/neofetch')
    (neo / 'usr/bin/neofetch').chmod(0o755)
    copy(ROOT / 'iso/vendor/neofetch-LICENSE.md', neo, 'usr/share/doc/neofetch/copyright')
    copy(ROOT / 'iso/vendor/neofetch-LICENSE.md', neo, 'usr/share/doc/neofetch/LICENSE')
    full = staging / 'allyos-apps'
    extras = recommended_extras()
    control(full, 'allyos-apps', ', '.join(['allyos-desktop', *dict.fromkeys(extras)]),
            'AllyOS recommended applications, diagnostics and Wine')
    return [branding, desktop, neo, full]


def bundle_sources(output):
    archive = output / 'config/includes.binary/sources' / f'allyos-source-{VERSION}.tar.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    def source_filter(info):
        excluded = {'vms', '.venv', '__pycache__', 'build-preview', 'output', '.git',
                    'sddm-THEMING-reference.md', '.vm-command.json', 'vm-command-bridge.py'}
        parts = Path(info.name).parts
        return None if excluded.intersection(parts) or 'local-assets' in parts or any(p.startswith(('build-preview-', '.vm-command')) for p in parts) else info
    with tarfile.open(archive, 'w:gz') as bundle:
        for name in ('iso', 'shell', 'docs', 'tools', 'README.md', 'LICENSE', 'COPYRIGHT.md'):
            bundle.add(ROOT / name, arcname=name, filter=source_filter)


def prepare(output, pack=True):
    output = output.resolve()
    if output.exists() and any(output.iterdir()) and not (output / 'allyos-build.json').exists():
        raise SystemExit('Pasta de destino não vazia e não pertence ao builder AllyOS.')
    output.mkdir(parents=True, exist_ok=True)
    put(output, 'allyos-build.json', json.dumps(RELEASE, indent=2) + '\n')
    put(output, 'config/bootloaders/splash.svg',
        (ROOT / 'iso/boot/splash.svg').read_text(encoding='utf-8').replace('@ALLY_VERSION@', VERSION))
    with tempfile.TemporaryDirectory(prefix='allyos-staging-', dir=output) as temporary:
        staging = Path(temporary)
        assert staging.resolve().is_relative_to(output)
        for package in stage_packages(staging):
            if pack:
                package_version = '7.1.0+allyos1' if package.name == 'neofetch' else VERSION + '-1'
                target = output / 'config/packages.chroot' / f'{package.name}_{package_version}_all.deb'
                target.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(package), str(target)], check=True)
            else:
                shutil.copytree(package, output / 'staging' / package.name, dirs_exist_ok=True)
    tux = ROOT / 'shell/vendor/tux-manager_1.0.8-1.deb13_amd64.deb'
    assert hashlib.sha256(tux.read_bytes()).hexdigest() == '77f14af3305cb8cf09faf027812e906a845ea281a2fb95795360b9db01b2b4d7'
    copy(tux, output, 'config/packages.chroot/' + tux.name)
    put(output, 'config/package-lists/allyos.list.chroot', 'allyos-desktop\nallyos-apps\nallyos-branding\nneofetch\nlinux-image-amd64\nlive-boot\nlive-config\nlive-config-systemd\nsystemd-sysv\nlocales\nsudo\ncalamares\ncalamares-settings-debian\n')
    # Listas separadas: APT resolve cada conjunto sem tentar instalar duas
    # variantes conflitantes do GRUB no mesmo sistema. As duas ficam na mídia.
    put(output, 'config/package-lists/allyos-bios.list.binary', 'grub-pc\n')
    put(output, 'config/package-lists/allyos-efi.list.binary', 'grub-efi\n')
    put(output, 'config/package-lists/allyos-wine32.list.chroot', 'wine32:i386\n')
    from installer import prepare_installer
    prepare_installer(output, VERSION)
    put(output, 'config/includes.installer/preseed.cfg', 'd-i debian-installer/locale string pt_BR.UTF-8\nd-i pkgsel/run_tasksel boolean false\n')
    # Overlay versionado do tema, também usado para testar ajustes de branding
    # antes da fase final de uma imagem de desenvolvimento.
    copy(ROOT / 'iso/sddm/Main.qml', output, 'config/includes.chroot/usr/share/sddm/themes/allyos/Main.qml')
    # live-config exports this setting before its SDDM component runs. Its
    # built-in session detection only handles Plasma and LXQt.
    put(output, 'config/includes.chroot/etc/live/config.conf.d/50-allyos.conf', 'LIVE_SESSION="roseshell.desktop"\n')
    copy(ROOT / 'iso/public-firmware-cleanup.sh', output, 'config/hooks/normal/0998-public-firmware.hook.chroot')
    (output / 'config/hooks/normal/0998-public-firmware.hook.chroot').chmod(0o755)
    put(output, 'config/hooks/normal/0999-allyos.hook.chroot', '''#!/bin/sh
set -eu
printf 'pt_BR.UTF-8 UTF-8\nen_US.UTF-8 UTF-8\n' > /etc/locale.gen
locale-gen
update-locale LANG=pt_BR.UTF-8
systemctl set-default graphical.target
systemctl enable allyos-virtualbox-display.service
install -d -m 755 /var/lib/openbox
python3 -c 'import PySide6.QtWidgets; import shiboken6'
test -x /usr/bin/roseshell-session
update-alternatives --install /usr/bin/x-session-manager x-session-manager /usr/bin/roseshell-session 100
update-alternatives --set x-session-manager /usr/bin/roseshell-session
test -f /usr/share/sddm/themes/allyos/Main.qml
# live-build materializes /etc/os-release from its Debian bootstrap before
# hooks. Restore the standard relative link to the branded, diverted file.
grep -q '^ID=allyos$' /usr/lib/os-release
ln -sfn ../usr/lib/os-release /etc/os-release
grep -q '^ID=allyos' /etc/os-release
dpkg-query -W > /usr/share/allyos/package-versions.txt
dpkg-query -W -f='${binary:Package}\\t${Version}\\t${source:Package}\\t${source:Version}\\n' > /usr/share/allyos/package-sources.tsv
''', True)
    copy(ROOT / 'shell/vendor/tuxmanager-source-v1.0.8.tar.gz', output, 'config/includes.binary/sources/tuxmanager-source-v1.0.8.tar.gz')
    copy(ROOT / 'iso/vendor/neofetch', output, 'config/includes.binary/sources/neofetch-7.1.0')
    copy(ROOT / 'iso/vendor/neofetch-LICENSE.md', output, 'config/includes.binary/sources/neofetch-LICENSE.md')
    copy(ROOT / 'LICENSE', output, 'config/includes.binary/sources/RoseShell-LICENSE')
    bundle_sources(output)
    put(output, 'config/includes.binary/ALLYOS-README.txt', f'AllyOS {VERSION} development\nCriado por gorigamia. Base: Debian GNU/Linux 13 trixie.\nRoseShell e login AllyOS; instalador Debian Live.\nEsta imagem exige teste de boot e instalação antes de distribuição.\n')
    print('Configuração preparada:', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage-only', action='store_true')
    args = parser.parse_args()
    prepare(args.output, not args.stage_only)
