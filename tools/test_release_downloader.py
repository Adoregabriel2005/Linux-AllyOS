"""Exercise Windows multipart reconstruction locally, without network or publishing."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
import make_release_assets as package

project = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='downloader-selftest-', dir=project / 'iso/output') as directory:
    root = Path(directory).resolve()
    assert root.is_relative_to(project / 'iso/output')
    (root / 'iso').mkdir()
    (root / 'iso/release.json').write_text('{"version":"0.0.0"}')
    image = root / 'AllyOS-0.0.0-dev-amd64.iso'
    data = bytes(range(250)) * 4
    image.write_bytes(data)
    checksum = hashlib.sha256(data).hexdigest()
    for name, report in [('fixture-validation.json', {'passed': True, 'image_sha256': checksum}),
                         ('fixture-audit.json', {'passed': True, 'image_sha256': checksum, 'local_audio_absent': True})]:
        (root / name).write_text(json.dumps(report))
    assets = root / 'iso/output/test-assets'
    with patch.object(package, 'ROOT', root), patch.object(package, 'REPO', 'example/selftest-only'), \
         patch.object(package, 'LIMIT', 600), patch.object(package, 'MAX_ASSET_BYTES', 700), \
         patch.object(sys, 'argv', ['test', str(image), str(root / 'fixture-validation.json'),
                                  str(root / 'fixture-audit.json'), str(assets)]):
        package.main()
    result = subprocess.run(['cmd.exe', '/d', '/c', 'Baixar-AllyOS.cmd <NUL'], cwd=assets,
                            capture_output=True, text=True, errors='replace', timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (assets / image.name).exists(), result.stdout + result.stderr
    assert (assets / image.name).read_bytes() == data
    assert not (assets / (image.name + '.assembling')).exists()
    print('WINDOWS DOWNLOADER OK: two parts, exact byte reconstruction and SHA256 verification; no network')
