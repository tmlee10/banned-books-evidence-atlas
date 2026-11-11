#!/usr/bin/env python3
"""Install only the Banned Books static site on the existing Research3 droplet."""
import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

DOMAIN = 'bannedbooks.research3.org'
EXPECTED_IP = '143.198.36.166'
UPSTREAM = '56d0fc2d22c43410685e2bfbfe3ff9430fb69794'
PROJECT_SHA = 'f77fb0f44eeb52132c4f104ee1cd77147ad8ed85d6ad12174770d0e7f8456e8e'
EXTRAS = {
    'banned-books-revised-data-code.zip': '944687e953be7ecd484c94b4db183dbb239c9fba181e504c58f5ca7b0091a022',
    'banned-books-gdelt-reviewed.zip': 'c2bad90c0952b20ea9eb52efde22b71fd3ef713beaee32dbbac7e0a901b70def',
}
BASE = Path('/var/www') / DOMAIN
AVAILABLE = Path('/etc/nginx/sites-available') / DOMAIN
ENABLED = Path('/etc/nginx/sites-enabled') / DOMAIN
CERT = Path('/etc/letsencrypt/live') / DOMAIN
MARKER = '# Managed by Research3 Banned Books deployment v1'
PACKAGE = Path(__file__).resolve().parents[2]


def run(*args, capture=False):
    return subprocess.run(args, check=True, text=True, capture_output=capture)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require_hash(path, expected):
    if not path.is_file() or digest(path) != expected:
        raise RuntimeError(f'Checksum mismatch or missing file: {path.name}')


def extract_checked(archive, destination):
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            name = PurePosixPath(member.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in member.filename:
                raise RuntimeError('Unsafe archive path')
            if stat.S_ISLNK(member.external_attr >> 16):
                raise RuntimeError('Archive symlinks are not allowed')
        if z.testzip() is not None:
            raise RuntimeError('Corrupt project archive')
        z.extractall(destination)


def prepare(destination, cache):
    archive = PACKAGE / 'banned-books-project.zip'
    require_hash(archive, PROJECT_SHA)
    extract_checked(archive, destination)
    cache.mkdir(parents=True, exist_ok=True)
    for name, expected in EXTRAS.items():
        cached = cache / name
        if not cached.is_file() or digest(cached) != expected:
            url = f'https://raw.githubusercontent.com/tmlee10/banned-books-evidence-atlas/{UPSTREAM}/{name}'
            print(f'Downloading preserved research archive: {name}', flush=True)
            temp = cached.with_suffix('.part')
            try:
                with urllib.request.urlopen(url, timeout=120) as response, temp.open('wb') as out:
                    shutil.copyfileobj(response, out)
                require_hash(temp, expected)
                os.replace(temp, cached)
            finally:
                temp.unlink(missing_ok=True)
        require_hash(cached, expected)
        shutil.copyfile(cached, destination / 'dist/downloads' / name)
    for check in ('check_website.py', 'check_gdelt.py', 'check_current.py'):
        run(sys.executable, str(destination / 'scripts' / check))
    # Check all locally linked pages/assets, including links not covered by the original checks.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from verify_links import verify
    verify(destination / 'dist')
    print('PASS: supplied website, all downloads, source checksums and local links.', flush=True)


def config(https=False):
    common = f'''    root {BASE}/current/dist;
    index index.html;
    autoindex off;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    location ~ /\\. {{ deny all; }}
    location / {{ try_files $uri $uri/ =404; }}
'''
    challenge = f'''    location ^~ /.well-known/acme-challenge/ {{
        root {BASE}/current/dist;
        default_type text/plain;
        try_files $uri =404;
    }}
'''
    head = f'''{MARKER}
server {{
    listen 80;
    listen [::]:80;
    server_name {DOMAIN};
'''
    if not https:
        return head + challenge + common + '}\n'
    return head + challenge + f'''    location / {{ return 301 https://{DOMAIN}$request_uri; }}
}}
server {{
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name {DOMAIN};
    ssl_certificate {CERT}/fullchain.pem;
    ssl_certificate_key {CERT}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
''' + common + '}\n'


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.bannedbooks-')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        os.chmod(name, 0o644)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def atomic_link(path, target):
    temporary = path.with_name(path.name + '.new')
    if temporary.exists() or temporary.is_symlink():
        raise RuntimeError(f'Unexpected temporary path exists: {temporary}')
    temporary.symlink_to(target)
    os.replace(temporary, path)


def preflight():
    if os.geteuid() != 0:
        raise RuntimeError('Run the install/https/rollback command with sudo.')
    for command in ('nginx', 'systemctl', 'curl', 'ip'):
        if not shutil.which(command):
            raise RuntimeError(f'Missing expected server command: {command}')
    interfaces = json.loads(run('ip', '-j', '-4', 'address', 'show', capture=True).stdout)
    addresses = {a['local'] for item in interfaces for a in item.get('addr_info', [])}
    if EXPECTED_IP not in addresses:
        raise RuntimeError(f'This helper is for the existing droplet {EXPECTED_IP}; address not found.')
    run('nginx', '-t')
    if AVAILABLE.is_symlink() or (AVAILABLE.exists() and not AVAILABLE.read_text().startswith(MARKER)):
        raise RuntimeError('Existing Banned Books config is not managed by this installer; refusing replacement.')
    if ENABLED.exists() or ENABLED.is_symlink():
        if not ENABLED.is_symlink() or ENABLED.resolve() != AVAILABLE:
            raise RuntimeError('Unexpected enabled-site entry; refusing replacement.')
    if (BASE / 'current').exists() and not (BASE / 'current').is_symlink():
        raise RuntimeError('Existing current path is not a managed release symlink.')
    dump = run('nginx', '-T', capture=True)
    filename = ''
    for line in dump.stdout.splitlines():
        if line.startswith('# configuration file '):
            filename = line[len('# configuration file '):].rstrip(':')
        uncommented = line.split('#', 1)[0]
        for names in re.findall(r'\bserver_name\s+([^;]+);', uncommented):
            if DOMAIN in names.split() and Path(filename) not in (AVAILABLE, ENABLED):
                raise RuntimeError(f'{DOMAIN} is already configured elsewhere: {filename}')
    if 'conflicting server name' in (dump.stdout + dump.stderr).lower():
        raise RuntimeError('Existing Nginx server-name conflict; resolve before adding this site.')


def snapshot():
    return {
        'config': AVAILABLE.read_text() if AVAILABLE.exists() else None,
        'enabled': str(ENABLED.readlink()) if ENABLED.is_symlink() else None,
        'current': str((BASE / 'current').readlink()) if (BASE / 'current').is_symlink() else None,
    }


def restore(saved):
    if saved['current'] is None:
        (BASE / 'current').unlink(missing_ok=True)
    else:
        atomic_link(BASE / 'current', saved['current'])
    if saved['config'] is None:
        AVAILABLE.unlink(missing_ok=True)
    else:
        atomic_write(AVAILABLE, saved['config'])
    if saved['enabled'] is None:
        ENABLED.unlink(missing_ok=True)
    else:
        atomic_link(ENABLED, saved['enabled'])
    run('nginx', '-t')
    run('systemctl', 'reload', 'nginx')


def check_live(https=False):
    scheme, port = ('https', 443) if https else ('http', 80)
    root = BASE / 'current/dist'
    manifest = json.loads((root / 'data/download_manifest.json').read_text())
    paths = ['/', '/current-2025-2026.html', '/data/state_analysis_2025_2026.csv']
    for path in paths:
        result = run('curl', '--noproxy', '*', '--fail', '--silent', '--show-error',
                     '--max-time', '20', '--resolve', f'{DOMAIN}:{port}:127.0.0.1',
                     f'{scheme}://{DOMAIN}{path}', capture=True)
        expected = root / ('index.html' if path == '/' else path.lstrip('/'))
        if result.stdout != expected.read_text():
            raise RuntimeError(f'Unexpected live response for {path}')
    for item in manifest:
        run('curl', '--noproxy', '*', '--fail', '--silent', '--show-error', '--head',
            '--max-time', '20', '--resolve', f'{DOMAIN}:{port}:127.0.0.1',
            f'{scheme}://{DOMAIN}/downloads/{item["filename"]}', capture=True)
    print(f'PASS: {scheme.upper()} pages, state data and {len(manifest)} downloads served by Nginx.', flush=True)


def install(cache):
    preflight()
    version = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    release = BASE / 'releases' / version
    release.mkdir(parents=True)
    prepare(release, cache)
    for path in [BASE, BASE / 'releases', release, *release.rglob('*')]:
        os.chmod(path, 0o755 if path.is_dir() else 0o644)
    saved = snapshot()
    backup = BASE / 'backups' / version
    backup.mkdir(parents=True, mode=0o700)
    atomic_write(backup / 'state.json', json.dumps(saved, indent=2))
    has_cert = (CERT / 'fullchain.pem').is_file() and (CERT / 'privkey.pem').is_file()
    try:
        atomic_link(BASE / 'current', str(release))
        atomic_write(AVAILABLE, config(has_cert))
        atomic_link(ENABLED, str(AVAILABLE))
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        time.sleep(0.3)
        check_live(has_cert)
    except Exception:
        restore(saved)
        print('Restored the previous Banned Books configuration after a failed activation.', file=sys.stderr)
        raise
    atomic_write(BASE / 'last-backup', str(backup) + '\n')
    print(f'Installed release: {version}\nBackup: {backup}')
    if has_cert:
        print(f'HTTPS ready on the droplet: https://{DOMAIN}/ (check public DNS separately).')
    else:
        print(f'HTTP installed. Set Namecheap A record bannedbooks -> {EXPECTED_IP}, then run the https command.')


def enable_https():
    preflight()
    if not (BASE / 'current/dist/index.html').is_file():
        raise RuntimeError('Run install first.')
    if not shutil.which('certbot'):
        raise RuntimeError('Certbot is missing; install it using the existing server administration process.')
    addresses = {item[4][0] for item in socket.getaddrinfo(DOMAIN, 80, type=socket.SOCK_STREAM)}
    if addresses != {EXPECTED_IP}:
        raise RuntimeError(f'DNS is not ready: {sorted(addresses)}. Set only A bannedbooks -> {EXPECTED_IP}; remove a stale AAAA for this host.')
    # certonly never rewrites any Nginx site or expands the shared Research3 certificate.
    run('certbot', 'certonly', '--webroot', '-w', str(BASE / 'current/dist'),
        '--cert-name', DOMAIN, '-d', DOMAIN, '--non-interactive', '--keep-until-expiring',
        '--deploy-hook', 'nginx -t && systemctl reload nginx')
    previous = AVAILABLE.read_text()
    try:
        atomic_write(AVAILABLE, config(True))
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        time.sleep(0.3)
        check_live(True)
    except Exception:
        atomic_write(AVAILABLE, previous)
        run('nginx', '-t')
        run('systemctl', 'reload', 'nginx')
        raise
    print(f'HTTPS ready: https://{DOMAIN}/\nCurrent analysis: https://{DOMAIN}/current-2025-2026.html')


def rollback():
    preflight()
    backup = Path((BASE / 'last-backup').read_text().strip())
    if backup.parent != BASE / 'backups':
        raise RuntimeError('Unexpected rollback backup location')
    restore(json.loads((backup / 'state.json').read_text()))
    print(f'Rolled back the last install using {backup}. Release files and certificates were kept.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'install', 'https', 'status', 'rollback'))
    parser.add_argument('--cache-dir', type=Path, help='Optional cache of the two checksum-pinned research ZIPs')
    args = parser.parse_args()
    cache = args.cache_dir or (Path('/var/cache/bannedbooks-research3') if args.command == 'install'
                               else Path(tempfile.gettempdir()) / 'bannedbooks-research3-cache')
    if args.command == 'verify':
        with tempfile.TemporaryDirectory(prefix='bannedbooks-verify-') as temporary:
            prepare(Path(temporary), cache)
    elif args.command == 'install':
        install(cache)
    elif args.command == 'https':
        enable_https()
    elif args.command == 'rollback':
        rollback()
    else:
        preflight()
        https = 'listen 443 ssl;' in AVAILABLE.read_text() if AVAILABLE.exists() else False
        check_live(https)
        print('Public DNS:', sorted({x[4][0] for x in socket.getaddrinfo(DOMAIN, 80, type=socket.SOCK_STREAM)}))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f'STOP: {error}', file=sys.stderr)
        sys.exit(1)
