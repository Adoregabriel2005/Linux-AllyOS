"""Supervisor da sessão RoseShell; Openbox gerencia janelas, nossa UI é Qt."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def main():
    root = Path(__file__).resolve().parent
    if not shutil.which('openbox'):
        raise SystemExit('RoseShell precisa do pacote openbox.')
    os.environ['XDG_CURRENT_DESKTOP'] = 'RoseShell'
    os.environ['XDG_SESSION_DESKTOP'] = 'roseshell'
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    os.environ['PATH'] = os.pathsep.join([str(Path.home() / '.local/bin'), os.environ.get('PATH', ''), '/usr/sbin', '/sbin'])
    from PySide6.QtCore import QSettings
    if not os.environ.get('ROSESHELL_NESTED'):
        from application_theme import configure_external_theme
        configure_external_theme(QSettings('RoseShell', 'Desktop').value('theme', 'dark') == 'light')
    keyboard = QSettings('RoseShell', 'Desktop').value('keyboard', 'br')
    if keyboard in ('br', 'us') and shutil.which('setxkbmap'):
        subprocess.run(['setxkbmap', keyboard], check=False)
    wm = subprocess.Popen(['openbox', '--sm-disable', '--config-file', str(root / 'openbox.xml')])
    sound = subprocess.Popen([sys.executable, str(root / 'entry_sound.py')])
    agent = None
    # O agente real fala com polkit; a RoseShell nunca lê nem guarda senhas.
    # Não registrar um segundo agente na prévia Xephyr dentro do LXQt.
    if not os.environ.get('ROSESHELL_NESTED'):
        for candidate in ('/usr/libexec/polkit-mate-authentication-agent-1',
                          '/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1',
                          '/usr/bin/lxqt-policykit-agent'):
            if Path(candidate).is_file():
                agent = subprocess.Popen([candidate])
                break
    try:
        # Falha inesperada da UI: tentar recuperar sem deixar apenas o fundo X11.
        # Saída normal (menu sair) encerra a sessão imediatamente.
        for attempt in range(3):
            result = subprocess.call([sys.executable, str(root / 'main.py'), '--session', *sys.argv[1:]])
            if result == 0:
                return 0
            print(f'RoseShell: UI encerrou com {result}; tentativa {attempt + 1}/3.', file=sys.stderr, flush=True)
            time.sleep(1)
        return result
    finally:
        if sound.poll() is None:
            sound.terminate()
            try:
                sound.wait(timeout=2)
            except subprocess.TimeoutExpired:
                sound.kill()
                sound.wait()
        if agent is not None:
            agent.terminate()
            try:
                agent.wait(timeout=3)
            except subprocess.TimeoutExpired:
                agent.kill()
                agent.wait()
        wm.terminate()
        try:
            wm.wait(timeout=5)
        except subprocess.TimeoutExpired:
            wm.kill()
            wm.wait()


if __name__ == '__main__':
    sys.exit(main())
