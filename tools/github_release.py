"""Publish an audited, validated AllyOS release using existing Git credentials.

Credentials remain only in memory and are never printed, stored or passed in argv.
Only the explicitly requested repository and manifest-listed assets are accepted.
"""
import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import subprocess
import urllib.parse

REPOSITORY = 'Adoregabriel2005/Linux-AllyOS'
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    assert manifest_path.is_relative_to(ROOT / 'iso/output')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['validated'] is True and manifest['public_audio'] == 'original'
    assert manifest['repository'] == REPOSITORY
    assert manifest['notes'] and manifest['notes'] != 'NOTES_PENDING'
    assets = []
    for entry in manifest['assets']:
        path = (manifest_path.parent / entry['name']).resolve()
        assert path.parent == manifest_path.parent
        assert path.stat().st_size == entry['size'] < 2 * 1024 ** 3
        assert digest(path) == entry['sha256']
        assets.append((path, entry))
    credential = subprocess.run(['git', 'credential', 'fill'], cwd=ROOT,
        input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True,
        env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'}, check=True)
    values = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
    token = values['password']
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'AllyOS-release-builder'}

    def request(method, endpoint, data=None, host='api.github.com', file=None):
        connection = http.client.HTTPSConnection(host, timeout=1800)
        outgoing = dict(headers)
        body = None
        if file:
            body = file.open('rb')
            outgoing.update({'Content-Type': 'application/octet-stream', 'Content-Length': str(file.stat().st_size)})
        elif data is not None:
            body = json.dumps(data).encode()
            outgoing['Content-Type'] = 'application/json'
        try:
            connection.request(method, endpoint, body=body, headers=outgoing)
            response = connection.getresponse()
            raw = response.read()
            if response.status >= 400:
                raise RuntimeError(f'GitHub HTTP {response.status}: {method} {endpoint}')
            return json.loads(raw) if raw else None
        finally:
            if file and body:
                body.close()
            connection.close()

    base = '/repos/' + REPOSITORY
    releases = request('GET', base + '/releases?per_page=100')
    release = next((item for item in releases if item['tag_name'] == manifest['tag']), None)
    if release is None:
        release = request('POST', base + '/releases', {
            'tag_name': manifest['tag'], 'target_commitish': manifest['commit'],
            'name': manifest['title'], 'body': manifest['notes'], 'draft': True, 'prerelease': True})
    assert release['draft'], 'Não alterar uma release já publicada por este script'
    known = {entry['name']: entry for entry in request('GET', base + f'/releases/{release["id"]}/assets?per_page=100')}
    for path, entry in assets:
        existing = known.get(path.name)
        if existing:
            assert existing['size'] == entry['size']
            assert existing.get('digest') == 'sha256:' + entry['sha256']
            continue
        print('Enviando', path.name, path.stat().st_size, flush=True)
        uploaded = request('POST', base + f'/releases/{release["id"]}/assets?name=' + urllib.parse.quote(path.name),
                           host='uploads.github.com', file=path)
        assert uploaded['size'] == entry['size'] and uploaded['state'] == 'uploaded'
        assert uploaded.get('digest') == 'sha256:' + entry['sha256']
    if args.publish:
        release = request('PATCH', base + f'/releases/{release["id"]}', {'draft': False})
    print(json.dumps({'url': release['html_url'], 'draft': release['draft'], 'assets_verified': len(assets)}))


if __name__ == '__main__':
    main()
