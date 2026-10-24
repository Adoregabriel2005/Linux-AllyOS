"""Audit the exact Git index before publishing; never print matched secrets."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[1]
names = subprocess.check_output(['git', 'ls-files', '--cached', '-z'], cwd=root).decode().split('\0')
forbidden = ('iso/output/', 'iso/local-assets/', 'vms/', 'iso/build-preview', '.aws/', '.codex/')
patterns = {
    'private-key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'github-token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,})',
    'openai-token': rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}',
    'aws-access-key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'credential-url': rb'https?://[^\s/@:]+:[^\s/@]+@',
    'literal-password': rb'(?im)^\s*(?:password|passwd|api_key|access_token|secret_key)\s*=\s*[\x22\x27][^\x22\x27\r\n]{4,}[\x22\x27]\s*$',
}
report = {'files': [], 'findings': [], 'scope': 'exact staged Git blobs; no local assets, output, VMs or command requests'}
for name in filter(None, names):
    data = subprocess.check_output(['git', 'show', ':' + name], cwd=root)
    if name.startswith(forbidden) or '.vm-command' in name or Path(name).name in ('.env', '.git-credentials'):
        report['findings'].append({'file': name, 'kind': 'forbidden-path'})
    if len(data) > 100_000_000:
        report['findings'].append({'file': name, 'kind': 'oversized-binary'})
    if b'\0' not in data[:8192]:
        for kind, pattern in patterns.items():
            if re.search(pattern, data):
                report['findings'].append({'file': name, 'kind': kind})
    report['files'].append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
report['passed'] = not report['findings']
destination = root / 'iso/output/publication-audit.json'
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': report['passed'], 'files': len(report['files']), 'findings': report['findings']}))
raise SystemExit(0 if report['passed'] else 1)
