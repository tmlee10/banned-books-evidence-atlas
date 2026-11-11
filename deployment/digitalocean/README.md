# DigitalOcean deployment: bannedbooks.research3.org

Prepared 11 November 2026 for the existing Research3 droplet, `143.198.36.166`, SSH user `deploy`.
The website and research outputs are the user's supplied November 9 package. The installer does not refit models or change research content.

## 1. Upload from Windows PowerShell

Save `Banned_Books_DigitalOcean.zip` to Downloads, then run:

```powershell
scp -i "$env:USERPROFILE\.ssh\starcasm_dang" "$env:USERPROFILE\Downloads\Banned_Books_DigitalOcean.zip" deploy@143.198.36.166:/home/deploy/
ssh -i "$env:USERPROFILE\.ssh\starcasm_dang" deploy@143.198.36.166
```

## 2. Install on the droplet

```bash
python3 -m zipfile -e /home/deploy/Banned_Books_DigitalOcean.zip /home/deploy
cd /home/deploy/Banned_Books_DigitalOcean
sudo python3 deployment/digitalocean/deploy_bannedbooks.py install
```

The first install requires internet access to download two existing research archives from the repository. Both URLs are pinned to Git commit `56d0fc2d22c43410685e2bfbfe3ff9430fb69794`, and both SHA-256 values must match the supplied site's download manifest. They are downloaded automatically, not uploaded separately. The installer stops before activating a release if any download, checksum or website check fails.

Existing `nginx`, `systemctl`, `curl`, `ip` and Python 3.9+ are required. HTTPS additionally requires the droplet's existing Certbot installation and configured ACME account. No new Docker container, application port, account, paid service or database is created.

## 3. Set DNS in Namecheap

In research3.org > Advanced DNS, add or update only this host:

| Type | Host | Value | TTL |
| --- | --- | --- | --- |
| A Record | bannedbooks | 143.198.36.166 | Automatic |

Remove a conflicting CNAME or stale AAAA record for `bannedbooks`, if present. Preserve records for `@`, `www`, `starcasm`, `dang`, `study`, and `redlining`.

## 4. Enable HTTPS after DNS resolves

From the same extracted folder:

```bash
sudo python3 deployment/digitalocean/deploy_bannedbooks.py https
sudo python3 deployment/digitalocean/deploy_bannedbooks.py status
```

The HTTPS command checks that public address resolution points only to the expected droplet. If DNS has not propagated, stop and rerun this command later; do not repeatedly request certificates. It obtains a separate certificate named `bannedbooks.research3.org` via Certbot's webroot mode. It does not expand the shared Research3 certificate or let Certbot edit unrelated Nginx sites. A renewal deploy hook validates/reloads Nginx when this certificate renews. The existing Certbot renewal timer must remain enabled.

Open:

- https://bannedbooks.research3.org/
- https://bannedbooks.research3.org/current-2025-2026.html

The supplied homepage is preserved, with its banner linking to the current analysis. The two-year comparison and earlier verification remain on their supplied pages.

## Files and recovery

- Site root: `/var/www/bannedbooks.research3.org/current/dist`
- Versioned releases: `/var/www/bannedbooks.research3.org/releases/`
- Site-only backups: `/var/www/bannedbooks.research3.org/backups/`
- Nginx file: `/etc/nginx/sites-available/bannedbooks.research3.org`
- Enabled symlink: `/etc/nginx/sites-enabled/bannedbooks.research3.org`
- Download cache: `/var/cache/bannedbooks-research3/`

Activation uses an atomic release symlink, runs `nginx -t`, and reloads Nginx. If activation fails, it attempts to restore the prior Banned Books configuration. It does not stop or restart existing apps. On a first install rollback removes only the newly added Banned Books configuration. Other sites remain enabled. Release files and certificates are retained for inspection.

To undo the most recent successful install:

```bash
sudo python3 deployment/digitalocean/deploy_bannedbooks.py rollback
```

If interrupted during activation, review the newest `backups/*/state.json` before rerunning. This installer refuses unrecognized existing Banned Books configurations and duplicate server names rather than overwriting them. It does not alter DNS, firewall rules or the Research3 landing page.

## Local checks and future updates

```bash
python3 deployment/digitalocean/deploy_bannedbooks.py verify
python3 -m unittest discover -s deployment/digitalocean -p test_deploy.py -v
```

Verification requires no root privileges. The `--cache-dir` option can point to an existing directory containing the two pinned ZIPs to verify offline.

If `banned-books-project.zip` changes in a future revision, update `PROJECT_SHA` in the installer after validating that archive. Updates to the two external research archives require updating both the pinned commit/checksums and the site's own download manifest.

## Validation performed before delivery

- All supplied static website checks passed, including the current-year, GDELT and source-download checks.
- All four HTML pages and 97 local links/anchors passed verification.
- All 16 original audit tests passed in the preparation environment.
- Seven deployment tests passed, covering checksum enforcement, unsafe archive paths, separate certificate configuration, successful install/rollback, failed activation recovery, and DNS mismatch refusal.
- The installer was tested in a clean temporary extraction using the two verified cached archives.

Actual Nginx configuration validation, certificate issuance, public DNS and live deployment must still be verified on the droplet. No live installation or GitHub push was performed from this preparation environment.
