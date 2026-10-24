"""Créditos, dependências e licença exibidos dentro da interface."""
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QTabWidget, QLabel
from icons import illustrated_icon
from preferences import fit_dialog
from i18n import tr
from system_release import allyos_identity
from html import escape
import shutil


def open_about(panel):
    previous = getattr(panel, 'about_dialog', None)
    if previous is not None:
        previous.close()
        previous.deleteLater()
    dialog = QDialog(panel)
    dialog.setWindowTitle(tr('Sobre a RoseShell'))
    fit_dialog(dialog, panel, 680, 510)
    layout = QVBoxLayout(dialog)
    emblem = QLabel()
    emblem.setPixmap(illustrated_icon('jewel').pixmap(48, 48))
    layout.addWidget(emblem)
    text = QTextBrowser()
    text.setOpenExternalLinks(True)
    text.document().setDefaultStyleSheet('a { color: #c58f9d; }')
    identity = allyos_identity()
    tools = [('thunar', 'Thunar'), ('tux-manager', 'TuxManager'), ('xfce4-taskmanager', 'XFCE Task Manager'),
             ('fastfetch', 'Fastfetch'), ('neofetch', 'Neofetch'), ('hardinfo2', 'Hardinfo2'),
             ('sensors', 'lm-sensors'), ('nvtop', 'NVTOP'), ('gsmartcontrol', 'GSmartControl'),
             ('smartctl', 'smartmontools'), ('nvme', 'nvme-cli'), ('inxi', 'inxi'),
             ('lshw', 'lshw'), ('dmidecode', 'dmidecode'), ('glxinfo', 'Mesa'),
             ('vulkaninfo', 'Vulkan tools'), ('/usr/games/supertux2', 'SuperTux'),
             ('firefox-esr', 'Firefox ESR'), ('wine', 'Wine'), ('pavucontrol', 'Pavucontrol'),
             ('jstest-gtk', 'jstest-gtk')]
    included = ' · '.join(label for command, label in tools
                          if (Path(command).is_file() if '/' in command else shutil.which(command)))
    heading = escape(identity) + '<br><small>RoseShell</small>' if identity else 'RoseShell'
    text.setHtml('<h1>' + heading + '</h1><p><b>' + tr('Criada por gorigamia.') + '</b></p><p>' +
        tr('Uma interface sóbria, angular e leve sobre Debian.') + '</p><h3>' + tr('Licença') +
        '</h3><p>Copyright © 2026 gorigamia · GPL-3.0-or-later</p><p>' +
        tr('Você pode usar, estudar, modificar e redistribuir a RoseShell, inclusive comercialmente, seguindo a GPLv3 ou posterior. Preserve os créditos e forneça o código-fonte correspondente ao redistribuir binários. Sem garantia.') +
        '</p><h3>' + tr('Dependências da interface') + '</h3><p>' +
        'Python 3 · PySide6-Essentials / Qt Widgets · X11 · Openbox · wmctrl · '
        'libxcb-cursor0 · GLib/gio · polkit/MATE Polkit · setxkbmap · iproute2 · pciutils · '
        'util-linux · pactl/wpctl · qt6ct</p><h3>' + tr('Aplicativos incluídos') + '</h3><p>' +
        escape(included) + '</p><p>' +
        tr('Debian, Qt e aplicativos incluídos pertencem aos respectivos autores e mantêm suas próprias licenças. O crédito de gorigamia refere-se à RoseShell.') +
        '</p><p><a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPL v3</a> · '
        '<a href="https://github.com/benapetr/TuxManager">TuxManager</a></p>')
    tabs = QTabWidget()
    tabs.addTab(text, tr('Sobre a RoseShell'))
    license_text = QTextBrowser()
    license_text.setPlainText(Path(__file__).with_name('LICENSE').read_text(encoding='utf-8'))
    tabs.addTab(license_text, tr('Licença'))
    layout.addWidget(tabs)
    button = QPushButton(tr('Fechar'))
    button.clicked.connect(dialog.close)
    layout.addWidget(button)
    panel.about_dialog = dialog
    dialog.show()

