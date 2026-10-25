"""FailedToStart must settle once, release the process and keep the UI alive."""
import os
import tempfile
from unittest.mock import patch

temporary = tempfile.TemporaryDirectory()
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['XDG_CONFIG_HOME'] = temporary.name
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication
from main import Panel

app = QApplication([])
panel = Panel()
panel.status.shutdown()
panel.tasks.shutdown()
panel.status.stopping = False
answers = []
with patch('system_ui.shutil.which', return_value='/bin/true'):
    panel.status.run(['allyos-nonexistent-review-command'], lambda ok, text: answers.append(ok))
loop = QEventLoop()
QTimer.singleShot(500, loop.quit)
loop.exec()
assert answers == [False], answers
assert not panel.status.processes, 'Failed process leaked'
panel.status.shutdown()
for widget in app.topLevelWidgets():
    widget.close()
app.processEvents()
print('PROCESS FAILURE OK: one failure callback, no pending process, no UI crash')
