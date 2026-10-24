"""Read-only dpkg integrity audit of a stable, completed image root."""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('root', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = args.root.resolve()
assert 'ID=allyos\n' in (root / 'usr/lib/os-release').read_text()
assert (root / 'usr/share/allyos/package-versions.txt').is_file()
args.output.mkdir(parents=True, exist_ok=True)
log = args.output / 'image-integrity.log'
with log.open('w') as stream:
    result = subprocess.run(['dpkg', '--root=' + str(root), '--verify'],
                            stdout=stream, stderr=subprocess.STDOUT,
                            env={**os.environ, 'LC_ALL': 'C'})
configuration, overlays, unexpected = [], [], []
for line in log.read_text().splitlines():
    if not line.strip():
        continue
    if ' c ' in line:
        configuration.append(line)
    elif line.endswith(' /usr/share/sddm/themes/allyos/Main.qml') and (
        root / 'usr/share/sddm/themes/allyos/Main.qml'
    ).read_bytes() == (Path(__file__).parent / 'sddm/Main.qml').read_bytes():
        overlays.append(line)
    else:
        unexpected.append(line)
report = {'dpkg_exit_code': result.returncode,
          'configuration_changes': configuration,
          'reviewed_source_overlays': overlays,
          'unexpected_changes': unexpected,
          'passed': result.returncode == 0 and not unexpected}
target = args.output / 'image-integrity.json'
temporary = target.with_suffix('.tmp')
temporary.write_text(json.dumps(report, indent=2))
temporary.replace(target)
print(json.dumps(report))
raise SystemExit(0 if report['passed'] else 1)
