"""Adiciona três atalhos de demonstração sem substituir os existentes."""
import json
from PySide6.QtCore import QSettings
from applications import installed_apps
from shortcuts import read_shortcuts

settings = QSettings('RoseShell', 'Desktop')
entries = read_shortcuts(settings)
for app in installed_apps():
    if any(key in app['path'].lower() for key in ('supertux', 'pcmanfm-qt', 'featherpad')):
        if not any(entry['path'] == app['path'] for entry in entries):
            entries.append({key: app[key] for key in ('path', 'name', 'icon')})
settings.setValue('desktop_shortcuts', json.dumps(entries))
print('Atalhos de demonstracao:', ', '.join(entry['name'] for entry in entries))
