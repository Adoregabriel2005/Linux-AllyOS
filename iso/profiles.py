"""Uma lista de aplicativos para gerar o metapacote e a escolha do instalador."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package_names(filename):
    return [line.strip() for line in (ROOT / 'shell' / filename).read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.lstrip().startswith('#')]


def recommended_extras():
    minimum = set(package_names('packages-minimal.txt'))
    packages = [name for name in package_names('packages-default.txt') if name not in minimum]
    return list(dict.fromkeys(packages + ['firefox-esr', 'firefox-esr-l10n-pt-br', 'tux-manager', 'neofetch']))
