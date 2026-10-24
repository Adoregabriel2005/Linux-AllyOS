"""Integração de janelas em display separado, com o Openbox real."""
import os
import subprocess
import sys
import time

source = '/mnt/interface-src'
with open('/mnt/allyos-output/task-x11-smoke.log', 'w') as log:
    server = subprocess.Popen(['Xephyr', ':13', '-screen', '1280x800', '-ac', '-nolisten', 'tcp'],
                              stdout=log, stderr=subprocess.STDOUT)
    manager = None
    try:
        time.sleep(1)
        assert server.poll() is None
        environment = {**os.environ, 'DISPLAY': ':13', 'ROSESHELL_NESTED': '1'}
        manager = subprocess.Popen(['openbox', '--sm-disable', '--config-file', source + '/openbox.xml'],
                                   env=environment, stdout=log, stderr=subprocess.STDOUT)
        time.sleep(1)
        result = subprocess.run(['python3', source + '/verify_tasks.py'], env=environment, timeout=25)
        raise SystemExit(result.returncode)
    finally:
        if manager is not None:
            manager.terminate()
            manager.wait(timeout=5)
        server.terminate()
        server.wait(timeout=5)
