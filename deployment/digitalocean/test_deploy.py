"""Exercise release activation/rollback without touching the real server."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import deploy_bannedbooks as d


class DeployTests(unittest.TestCase):
    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(root / 'bad.zip', 'w') as z:
                z.writestr('../outside', 'bad')
            with self.assertRaisesRegex(RuntimeError, 'Unsafe archive'):
                d.extract_checked(root / 'bad.zip', root / 'extract')
            self.assertFalse((root / 'outside').exists())

    def test_checksum_rejects_modified_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'file'
            p.write_text('changed')
            with self.assertRaisesRegex(RuntimeError, 'Checksum mismatch'):
                d.require_hash(p, '0' * 64)

    def test_tls_confined_to_separate_certificate(self):
        text = d.config(True)
        self.assertEqual(text.count('server_name ' + d.DOMAIN + ';'), 2)
        self.assertIn('/etc/letsencrypt/live/' + d.DOMAIN + '/fullchain.pem', text)
        self.assertNotIn('research3-domains', text)
        self.assertNotIn('proxy_pass', text)
        self.assertIn('location ^~ /.well-known/acme-challenge/', text)

    def exercise_activation(self, fail=False, first=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / 'www' / d.DOMAIN
            available = root / 'available' / d.DOMAIN
            enabled = root / 'enabled' / d.DOMAIN
            available.parent.mkdir()
            enabled.parent.mkdir()
            neighbor = available.parent / 'study'
            neighbor.write_text('DO NOT CHANGE THE STUDY CONFIG')
            base.mkdir(parents=True)
            old = base / 'releases/old'
            if not first:
                old.mkdir(parents=True)
                (base / 'current').symlink_to(old)
                available.write_text(d.MARKER + '\nold config\n')
                enabled.symlink_to(available)
            calls = []

            def fake_run(*args, **kwargs):
                calls.append(args)
                # Fail the first reload, then allow the rollback reload.
                if fail and args == ('systemctl', 'reload', 'nginx') and calls.count(args) == 1:
                    raise subprocess.CalledProcessError(1, args)
                return subprocess.CompletedProcess(args, 0, '', '')

            def fake_prepare(release, cache):
                (release / 'dist').mkdir()
                (release / 'dist/index.html').write_text('new site')

            with patch.multiple(d, BASE=base, AVAILABLE=available, ENABLED=enabled, CERT=root / 'cert'), \
                 patch.object(d, 'preflight'), patch.object(d, 'prepare', side_effect=fake_prepare), \
                 patch.object(d, 'run', side_effect=fake_run), patch.object(d, 'check_live'), \
                 patch.object(d.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                if fail:
                    with self.assertRaises(subprocess.CalledProcessError):
                        d.install(root / 'cache')
                    if first:
                        self.assertFalse(available.exists())
                        self.assertFalse(enabled.is_symlink())
                        self.assertFalse((base / 'current').is_symlink())
                    else:
                        self.assertEqual((base / 'current').resolve(), old)
                        self.assertEqual(available.read_text(), d.MARKER + '\nold config\n')
                else:
                    d.install(root / 'cache')
                    self.assertEqual((base / 'current/dist/index.html').read_text(), 'new site')
                    backup = Path((base / 'last-backup').read_text().strip())
                    self.assertEqual(json.loads((backup / 'state.json').read_text())['current'], str(old))
                    d.rollback()
                    self.assertEqual((base / 'current').resolve(), old)
                self.assertEqual(neighbor.read_text(), 'DO NOT CHANGE THE STUDY CONFIG')
                self.assertTrue(all('restart' not in call for call in calls))

    def test_install_and_manual_rollback_preserve_neighbor(self):
        self.exercise_activation()

    def test_failed_activation_restores_previous_site(self):
        self.exercise_activation(fail=True)

    def test_failed_first_install_removes_only_new_site_config(self):
        self.exercise_activation(fail=True, first=True)

    def test_https_refuses_wrong_dns_before_certbot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'current/dist').mkdir(parents=True)
            (root / 'current/dist/index.html').write_text('site')
            with patch.object(d, 'BASE', root), patch.object(d, 'preflight'), \
                 patch.object(d.shutil, 'which', return_value='/usr/bin/certbot'), \
                 patch.object(d.socket, 'getaddrinfo', return_value=[(None, None, None, None, ('192.0.2.1', 80))]), \
                 patch.object(d, 'run') as run:
                with self.assertRaisesRegex(RuntimeError, 'DNS is not ready'):
                    d.enable_https()
                run.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
