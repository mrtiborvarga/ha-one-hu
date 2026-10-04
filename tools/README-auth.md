# Browser Profile authentication (one_login.py)

This directory contains a standalone helper for the integration's
"Browser Profile" authentication mode. It is run outside of Home Assistant,
on any machine you control, and is never executed by Home Assistant itself.

Home Assistant only ever reads the `cookie.json` file this script produces.
It never launches a browser.

> [!NOTE]
> If you installed this integration through HACS, this `tools/` folder is **not** present on your Home Assistant instance — HACS only installs `custom_components/one_hu` (`content_in_root: false` in `hacs.json`). Get `tools/` separately, on whichever machine will run it: clone the repository (`git clone https://github.com/mrtiborvarga/ha-one-hu`) or download this folder from GitHub directly. This is true even if you intend to run `one_login.py` on the Home Assistant host itself — HACS won't have put it there.

By default the script writes `cookie.json` into its own current directory
(e.g. `tools/cookie.json`), not into Home Assistant's `/config`. Home
Assistant reads the file from wherever you set the integration's **Cookie
File Path**, which must be inside Home Assistant's config directory — the
recommended location is the integration's own folder:

```text
/config/custom_components/one_hu/cookie.json
```

- If this script runs on a different machine than Home Assistant (the
  common case), copy or sync the local `cookie.json` to that path after each
  run, e.g. `scp cookie.json user@homeassistant:/config/custom_components/one_hu/cookie.json`.
- If it runs directly on the Home Assistant host, you can skip the copy step
  and pass `--cookie-output /config/custom_components/one_hu/cookie.json`
  directly.

## Setup (once)

On Debian/Ubuntu (and other distributions that follow PEP 668), `pip install`
into the system Python is blocked with an `externally-managed-environment`
error, and Playwright's browser binaries shouldn't be installed system-wide
in any case. Use a virtual environment:

```bash
cd tools
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

On Debian/Ubuntu, Chromium also needs a few system libraries that Playwright
does not install automatically. Install them with:

```bash
.venv/bin/playwright install-deps chromium
```

(This runs `apt-get` under the hood and needs `sudo`/root.)

All commands below assume this virtual environment, i.e. `.venv/bin/python`
instead of a bare `python`.

## First login

```bash
.venv/bin/python one_login.py --headed
```

You will first be asked for your One Hungary username and password on the
console. A browser window then opens; accept the cookie banner if shown, and
solve the CAPTCHA if one appears (the script fills in and submits the
username/password form for you).

`--headed` needs a display. On a headless Debian server with no desktop
environment, either run this step from a machine that does have one (the
browser profile directory can then be copied over), or install a virtual
display such as `xvfb` and run under `xvfb-run`:

```bash
sudo apt-get install xvfb
xvfb-run .venv/bin/python one_login.py --headed
```

On success, the script saves a persistent browser profile (default directory:
`one-browser-profile/`, override with `--profile-dir`) and writes
`cookie.json` in the current directory.

Copy it to Home Assistant's config, then point the integration's "Browser
Profile" config flow step at that same path:

```bash
cp cookie.json /config/custom_components/one_hu/cookie.json
```

## Refreshing the cookie export

As long as the stored browser profile's session is still valid (One Hungary
uses a "remember me" style session), you can refresh `cookie.json` headlessly:

```bash
.venv/bin/python one_login.py
cp cookie.json /config/custom_components/one_hu/cookie.json
```

This does not open a visible browser and does not attempt a new login. If the
stored session has expired, the script exits with an error and asks you to
re-run with `--headed`. Schedule the headless form with cron or a systemd
timer if you want the export refreshed periodically.

## Scheduling the headless refresh

Run this on the same machine where you did the first `--headed` login, since
it reuses that machine's `--profile-dir`. It only re-exports cookies from the
already-authenticated profile; it never attempts a new login, so a non-zero
exit code means the session expired and you need to re-run with `--headed`
(see below) — make sure your scheduler surfaces that failure instead of
silently ignoring it.

### cron

If cron runs on the same host as Home Assistant, write directly to the
integration's folder:

```cron
*/15 * * * * cd /opt/one-hu-login && /opt/one-hu-login/.venv/bin/python one_login.py --profile-dir /opt/one-hu-login/one-browser-profile --cookie-output /config/custom_components/one_hu/cookie.json >> /var/log/one-hu-login.log 2>&1
```

If it runs on a separate machine, write locally and sync it across instead:

```cron
*/15 * * * * cd /opt/one-hu-login && /opt/one-hu-login/.venv/bin/python one_login.py --profile-dir /opt/one-hu-login/one-browser-profile --cookie-output /opt/one-hu-login/cookie.json && scp /opt/one-hu-login/cookie.json user@homeassistant:/config/custom_components/one_hu/cookie.json >> /var/log/one-hu-login.log 2>&1
```

Adjust the `.venv` path, `--profile-dir`, and the destination path(s) to your
setup. Checking the log (or cron's mail, if configured) is how you'll notice
a session expiry, since cron does not alert on failures by itself.

### systemd timer

Example unit files are in `tools/systemd/`. Edit the paths in
`one-hu-login.service` to match where you installed the script and virtual
environment, then install both units:

```bash
sudo cp tools/systemd/one-hu-login.service tools/systemd/one-hu-login.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now one-hu-login.timer
```

Check status and catch an expired-session failure with:

```bash
systemctl status one-hu-login.service
journalctl -u one-hu-login.service
```

## When the session expires

Delete the stored browser profile directory first (default:
`one-browser-profile/`, or whatever you passed to `--profile-dir`), then run
the script again with `--headed`:

```bash
rm -rf one-browser-profile
.venv/bin/python one_login.py --headed
cp cookie.json /config/custom_components/one_hu/cookie.json
```

Re-running against the old profile directory reuses whatever stale session
state is already in it, which can make the script skip straight to a login
attempt with cookies/local storage from the expired session still present
and confuse the flow. Deleting it first guarantees a clean login.

Note (from field testing): a headless login is not guaranteed to succeed,
because the One Hungary login flow may present a reCAPTCHA challenge. Always
use `--headed` for the initial login and for any re-login after a session has
actually expired.

## Multiple accounts

The integration supports more than one config entry, so you can monitor
several One Hungary accounts at once. A `cookie_header` represents a single
logged-in session for a single account, so you cannot merge two accounts'
cookies into one `cookie.json` — keep everything (profile directory, cookie
file, scheduled refresh job) separate per account:

```bash
.venv/bin/python one_login.py --headed --profile-dir profile-account-a --cookie-output cookie-account-a.json
.venv/bin/python one_login.py --headed --profile-dir profile-account-b --cookie-output cookie-account-b.json

cp cookie-account-a.json /config/custom_components/one_hu/cookie-account-a.json
cp cookie-account-b.json /config/custom_components/one_hu/cookie-account-b.json
```

Then add the integration once per account from **Settings > Devices &
services > Add integration > One Hungary Unofficial**, each time in Browser
Profile mode, pointing at that account's own cookie file. For cron or
systemd scheduling, duplicate the job/unit per account with its own
`--profile-dir` and output/destination path (e.g.
`one-hu-login-account-a.service` / `one-hu-login-account-b.service`).
