"""Ponte temporária local de testes: somente pastas compartilhadas, sem rede/senhas.

Iniciada manualmente durante esta validação e encerrada ao final. Não é
instalada, não tem autostart e não faz parte do desktop distribuído.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import time

namespace = os.environ.get('ALLYOS_TEST_BRIDGE', '')
assert re.fullmatch(r'[a-zA-Z0-9_-]{0,40}', namespace)
request = Path('/mnt/interface-src') / ('.vm-command' + ('-' + namespace if namespace else '') + '.json')
output = Path('/mnt/allyos-output') / namespace if namespace else Path('/mnt/allyos-output')
output.mkdir(parents=True, exist_ok=True)
(output / 'bridge-ready.json').write_text(json.dumps({'pid': os.getpid()}))
last = ''
while True:
    try:
        job = json.loads(request.read_text())
    except (OSError, ValueError):
        time.sleep(0.5)
        continue
    identity = job.get('id', '')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', identity) or identity == last:
        time.sleep(0.5)
        continue
    last = identity
    if job.get('stop') is True:
        (output / 'bridge-stopped.json').write_text(json.dumps({'id': identity}))
        break
    args = job.get('argv')
    if not isinstance(args, list) or not args or not all(isinstance(arg, str) for arg in args):
        continue
    result = {'id': identity}
    try:
        env = dict(os.environ)
        env.update(job.get('env', {}))
        completed = subprocess.run(args, cwd=job.get('cwd') or str(Path.home()), env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=min(1800, max(1, int(job.get('timeout', 60)))))
        result.update(code=completed.returncode, output=completed.stdout.decode('utf-8', 'replace')[-24000:])
    except Exception as error:
        result.update(code=-1, output=str(error))
    target = output / (identity + '.json')
    temporary = output / (identity + '.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    temporary.replace(target)
