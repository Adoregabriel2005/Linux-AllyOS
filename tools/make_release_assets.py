"""Package an already validated public ISO within GitHub's per-file size limit."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Adoregabriel2005/Linux-AllyOS'
LIMIT = 1_900_000_000
MAX_ASSET_BYTES = 2 * 1024 ** 3


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('validation', type=Path)
    parser.add_argument('public_audit', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    image = args.image.resolve()
    assert re.fullmatch(r'AllyOS-\d+\.\d+\.\d+-dev-amd64\.iso', image.name)
    image_hash = sha(image)
    validation = json.loads(args.validation.read_text(encoding='utf-8'))
    audit = json.loads(args.public_audit.read_text(encoding='utf-8'))
    assert validation['passed'] and validation['image_sha256'] == image_hash
    assert audit['passed'] and audit['local_audio_absent'] and audit['image_sha256'] == image_hash
    release = json.loads((ROOT / 'iso/release.json').read_text())
    version = release['version']
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'iso/output')
    assert not output.exists(), 'Use a new output directory; do not overwrite release assets'
    output.mkdir(parents=True)
    parts = []
    if image.stat().st_size < MAX_ASSET_BYTES:
        shutil.copyfile(image, output / image.name)
        parts.append({'name': image.name, 'sha256': image_hash})
    else:
        with image.open('rb') as source:
            number = 1
            while source.tell() < image.stat().st_size:
                path = output / (image.name + f'.part{number:02d}')
                remaining = min(LIMIT, image.stat().st_size - source.tell())
                with path.open('wb') as destination:
                    while remaining:
                        data = source.read(min(4 * 1024 * 1024, remaining))
                        assert data
                        destination.write(data)
                        remaining -= len(data)
                parts.append({'name': path.name, 'sha256': sha(path)})
                number += 1
        base = f'https://github.com/{REPO}/releases/download/v{version}'
        # Constant filenames and hashes are embedded; no remote code is executed.
        ps_parts = '@(' + ','.join("@{name='" + part['name'] + "';sha256='" + part['sha256'] + "'}" for part in parts) + ')'
        ps = (
            "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; "
            "Import-Module ($PSHOME+'\\Modules\\Microsoft.PowerShell.Utility\\Microsoft.PowerShell.Utility.psd1') -ErrorAction Stop; "
            f"$base='{base}'; $image='{image.name}'; $hash='{image_hash}'; "
            f"$parts={ps_parts}; "
            "if(Test-Path -LiteralPath $image){if((Get-FileHash -LiteralPath $image -Algorithm SHA256).Hash.ToLower() -eq $hash){Write-Host 'ISO pronta e verificada.'; exit 0};throw 'Ja existe uma ISO diferente nesta pasta.'}; "
            "foreach($p in $parts){Write-Host ('Baixando/verificando '+$p.name); "
            "if(!(Test-Path -LiteralPath $p.name)){Invoke-WebRequest -UseBasicParsing -Uri ($base+'/'+$p.name) -OutFile ($p.name+'.download'); "
            "if((Get-FileHash -LiteralPath ($p.name+'.download') -Algorithm SHA256).Hash.ToLower() -ne $p.sha256){throw 'Download incompleto ou corrompido'}; "
            "Move-Item -LiteralPath ($p.name+'.download') -Destination $p.name}; "
            "if((Get-FileHash -LiteralPath $p.name -Algorithm SHA256).Hash.ToLower() -ne $p.sha256){throw ('Parte invalida: '+$p.name)}}; "
            "$out=[IO.File]::Create((Join-Path (Get-Location) ($image+'.assembling'))); "
            "try{foreach($p in $parts){$inputStream=[IO.File]::OpenRead((Join-Path (Get-Location) $p.name));try{$inputStream.CopyTo($out)}finally{$inputStream.Dispose()}}}finally{$out.Dispose()}; "
            "if((Get-FileHash -LiteralPath ($image+'.assembling') -Algorithm SHA256).Hash.ToLower() -ne $hash){throw 'Falha ao verificar a ISO'}; "
            "Move-Item -LiteralPath ($image+'.assembling') -Destination $image; Write-Host ('ISO pronta: '+$image)"
        )
        assert '"' not in ps
        (output / 'Baixar-AllyOS.cmd').write_text('@echo off\r\nsetlocal\r\ncd /d "%~dp0"\r\npowershell.exe -NoProfile -Command "' + ps + '"\r\nset "result=%errorlevel%"\r\nif not "%result%"=="0" echo Nao foi possivel concluir o download. Confira a mensagem acima.\r\npause\r\nexit /b %result%\r\n', encoding='ascii', newline='')
        lines = ['#!/bin/sh', 'set -eu', 'cd "$(dirname "$0")"', f'image="{image.name}"',
                 'if [ -e "$image" ]; then echo "ISO já existe; confira SHA256SUMS.txt antes de substituir."; exit 1; fi']
        for part in parts:
            lines += [f'test -f "{part["name"]}" || curl --fail --location --retry 3 "{base}/{part["name"]}" -o "{part["name"]}"',
                      f'printf \'%s\\n\' \'{part["sha256"]}  {part["name"]}\' | sha256sum -c -']
        lines += ['cat ' + ' '.join('"' + part['name'] + '"' for part in parts) + ' > "$image.assembling"',
                  f'printf \'%s\\n\' \'{image_hash}  {image.name}.assembling\' | sha256sum -c -',
                  'mv "$image.assembling" "$image"', 'echo "ISO pronta e verificada: $image"']
        (output / 'Baixar-AllyOS.sh').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    checksums = [f'{image_hash}  {image.name}']
    checksums += [f'{part["sha256"]}  {part["name"]}' for part in parts if part['name'] != image.name]
    (output / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='ascii')
    assets = [{'name': path.name, 'size': path.stat().st_size, 'sha256': sha(path)} for path in sorted(output.iterdir())]
    manifest = {'repository': REPO, 'tag': 'v' + version, 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'title': f'AllyOS {version} — pré-release para testes', 'validated': True, 'public_audio': 'original',
                'notes': 'NOTES_PENDING', 'image_sha256': image_hash, 'assets': assets}
    (output / 'release-manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'assets': len(assets), 'split': len(parts) > 1, 'sha256': image_hash}))


if __name__ == '__main__':
    main()
