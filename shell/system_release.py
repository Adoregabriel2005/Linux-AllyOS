"""Identidade real do sistema; não transforma uma sessão de teste em outra distro."""
import platform


def allyos_identity():
    try:
        release = platform.freedesktop_os_release()
    except OSError:
        return None
    if release.get('ID') != 'allyos':
        return None
    return release.get('PRETTY_NAME', 'AllyOS')
