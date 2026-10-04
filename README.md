<p align="center">
  <img src="custom_components/one_hu/assets/logo.png" width="180" alt="One Hungary Unofficial logo">
</p>

# One Hungary Unofficial

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5)
![HACS](https://img.shields.io/badge/HACS-Compatible-41BDF5)
![Version](https://img.shields.io/badge/version-0.4.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)

An unofficial Home Assistant custom integration for monitoring One Hungary mobile subscriptions, balances, data usage, allowances, account status, and mobile services.

> [!WARNING]
> This project is not affiliated with, endorsed by, or maintained by One Hungary. It uses undocumented interfaces that may change without notice.

## Highlights

- Installation through HACS
- Home Assistant Config Flow
- Two authentication modes: pasted Cookie Header, or a Browser Profile cookie export file
- Account-level device with status and refresh controls
- Automatic discovery of mobile subscriptions
- Separate Home Assistant device for each subscription
- Balance and validity monitoring
- Mobile-data allowance and consumption sensors
- Selected allowance-specific sensors
- Tariff and subscription-status information
- Prepaid, eSIM, and barred-state binary sensors
- Mobile-service status binary sensors
- Coordinator-based periodic updates
- Manual refresh button

## Devices and entities

### Account-level device

The integration creates a primary account device. When account information is available, its name includes the primary account name:

```text
One Hungary (Account Name)
```

The account device provides:

- **API Status**: current API connection status
- **Last Successful Sync**: timestamp of the latest successful update
- **Mobile Services Count**: number of discovered mobile subscriptions
- **Refresh**: manually requests an immediate update

### Subscription devices

Every discovered mobile subscription is represented as a separate device:

```text
One Hungary 3670XXXXXXX
```

Each subscription can expose the following entities, depending on the information returned by One Hungary.

#### Subscription information

- **Balance**: prepaid balance
- **Days Available**: number of validity days reported by the API
- **Tariff**: current tariff name
- **Subscription Status**: current service status
- **Bundles Count**: number of returned bundle objects
- **Buckets Count**: number of returned data-bucket objects

#### Mobile-data usage

- **Data Allowance**: total active data allowance in GB
- **Data Remaining**: remaining data in GB
- **Data Used**: calculated consumed data in GB
- **Data Used Percentage**: calculated consumed percentage
- **Data Expires In**: days remaining until the earliest active data bucket expires

Example:

```text
Data Allowance       5.0 GB
Data Remaining       2.1 GB
Data Used            2.9 GB
Data Used Percentage 58 %
Data Expires In      18 d
```

#### Allowance monitoring

The current release includes dedicated sensors for the recurring `100MB adat` allowance:

- **100MB adat Remaining**
- **100MB adat Expires In**

The parsed allowance list is also available as an attribute of the Bundles Count entity.

#### Subscription binary sensors

- **Prepaid**
- **eSIM**
- **Barred**

#### Mobile-service binary sensors

Where reported by One Hungary, the integration exposes the active state of services including:

- Hívástartás
- Roaming üdvözlő SMS
- Hívószámkijelzés tiltás
- Mobil MMS szolgáltatás
- Hívásátirányítás (foglalt)
- Hívásátirányítás (feltétel nélküli)
- Hívásátirányítás
- Hívás várakoztatás
- Mobilvásárlás szolgáltatás
- Hívásátirányítás (nem elérhető)
- Hatósági felnőtt tartalom szűrés
- Hívásértesítő szolgáltatás
- Hívásátirányítás (nem válaszol)
- Roaming szolgáltatás
- Hívószámkijelzés

If a service is not reported for a subscription, the corresponding entity can be unavailable rather than incorrectly shown as inactive.

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Open **Custom repositories**.
3. Add the following repository:

   ```text
   https://github.com/mrtiborvarga/ha-one-hu
   ```

4. Select **Integration** as the category.
5. Install **One Hungary Unofficial**.
6. Restart Home Assistant.
7. Open **Settings > Devices & services > Add integration**.
8. Search for **One Hungary Unofficial**.

### Manual installation

Copy:

```text
custom_components/one_hu
```

into:

```text
/config/custom_components/
```

The resulting path must be:

```text
/config/custom_components/one_hu
```

Restart Home Assistant, then add **One Hungary Unofficial** under **Settings > Devices & services**.

## Authentication

The integration authenticates against One Hungary using a browser session. As of 0.4.0, there are two ways to provide that session, selected as the **Authentication Mode** in the config flow:

- **Cookie Header** — paste a session cookie manually (the original method).
- **Browser Profile** — point the integration at a `cookie.json` file produced by the `tools/one_login.py` helper script.

Both modes extract the `CSRF_TOKEN` value from the cookie and use it for authenticated requests. Home Assistant never launches a browser itself in either mode.

### Mode 1: Cookie Header

1. Sign in to your One Hungary account in a desktop browser.
2. While signed in, open:

   ```text
   https://www.one.hu/o/nc-framework-kernel/localization/getJson?locale=hu_HU
   ```

3. Open Developer Tools with `F12`.
4. Select the **Network** tab.
5. Reload the page.
6. Select the request ending with:

   ```text
   /o/nc-framework-kernel/localization/getJson?locale=hu_HU
   ```

7. Open **Request Headers**.
8. Locate the `Cookie` header.
9. Copy the complete value after `Cookie:`. Do not copy the `Cookie:` label itself.
10. Choose **Cookie Header** as the Authentication Mode and paste the value into the **Cookie Header** field.

Example format:

```text
JSESSIONID_VHPRTP_7500=...; CSRF_TOKEN=...; LFR_SESSION_STATE_20105=...; ...
```

#### Session expiration (Cookie Header mode)

Browser sessions eventually expire. If authentication fails or entities become unavailable:

1. Sign in to One Hungary again.
2. Obtain a fresh Cookie Header using the procedure above.
3. Reconfigure the integration with the new value.

### Mode 2: Browser Profile (cookie export file)

This mode avoids manually copying cookies out of developer tools. Instead, a standalone script (not part of the Home Assistant integration, and never run by it) performs the browser login and writes the session cookie to a file that the integration reads.

> [!NOTE]
> If you installed this integration through HACS, the `tools/` folder is **not** downloaded to your Home Assistant instance — HACS only installs `custom_components/one_hu` (see `hacs.json`'s `content_in_root: false`). Get `tools/` separately, on whichever machine will run it (which does not need to be the Home Assistant host): clone the repository (`git clone https://github.com/mrtiborvarga/ha-one-hu`) or download the `tools/` folder from GitHub directly.

1. On any machine you control (it does not need to be the Home Assistant host), set up `tools/one_login.py` in a virtual environment. A venv is required on Debian/Ubuntu and similar distributions, since they block `pip install` into the system Python (PEP 668) and Playwright's browser binaries shouldn't be installed system-wide anyway:

   ```bash
   cd tools
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/playwright install chromium
   ```

2. Run the first login with a visible browser window, since the login flow may require solving a CAPTCHA. By default this writes `cookie.json` into the current directory (`tools/`), not into Home Assistant's `/config`:

   ```bash
   .venv/bin/python one_login.py --headed
   ```

3. Copy the resulting `cookie.json` into the integration's folder under Home Assistant's config directory:

   ```bash
   cp cookie.json /config/custom_components/one_hu/cookie.json
   ```

   If `tools/one_login.py` runs on a different machine than Home Assistant, transfer the file instead, e.g. `scp cookie.json user@homeassistant:/config/custom_components/one_hu/cookie.json`.

4. In Home Assistant, choose **Browser Profile** as the Authentication Mode and set the **Cookie File Path** to where you copied the file, e.g. `/config/custom_components/one_hu/cookie.json`.

Full setup, headless refresh, and scheduling details (including cron and systemd timer examples) are documented in [`tools/README-auth.md`](tools/README-auth.md).

#### Session expiration (Browser Profile mode)

If the stored browser profile's session expires, the integration raises an authentication error until the cookie file is refreshed. Delete the stored browser profile directory first (default: `one-browser-profile/`), then re-run the login script with `--headed` and copy the refreshed `cookie.json` to the same path again:

```bash
rm -rf one-browser-profile
.venv/bin/python one_login.py --headed
cp cookie.json /config/custom_components/one_hu/cookie.json
```

Re-running against the old profile directory reuses its stale session state, which can interfere with a fresh login attempt — deleting it first avoids that. See [`tools/README-auth.md`](tools/README-auth.md) for details.

### Multiple accounts

The integration supports more than one config entry, so you can monitor more than one One Hungary account side by side. Each account's devices and entities are keyed by that account's data (account ID, subscription MSISDNs), so two accounts never collide.

A `cookie_header` represents one logged-in session for one account — you cannot combine two accounts into a single `cookie.json`. Instead, keep them fully separate:

1. Run `tools/one_login.py` once per account, each with its own profile directory and output file:

   ```bash
   .venv/bin/python one_login.py --headed --profile-dir profile-account-a --cookie-output cookie-account-a.json
   .venv/bin/python one_login.py --headed --profile-dir profile-account-b --cookie-output cookie-account-b.json
   ```

2. Copy each file to the integration's folder under a distinct name:

   ```bash
   cp cookie-account-a.json /config/custom_components/one_hu/cookie-account-a.json
   cp cookie-account-b.json /config/custom_components/one_hu/cookie-account-b.json
   ```

3. Add the integration again from **Settings > Devices & services > Add integration > One Hungary Unofficial** for each account, choosing Browser Profile mode and pointing each entry at its own file.

Refresh and reauthenticate each account independently, using that account's `--profile-dir` and `--cookie-output`/copy destination.

No reconfiguration of the integration is needed — it re-reads the same file path once it is updated.

## Update behavior

The integration uses Home Assistant's `DataUpdateCoordinator`.

Default polling interval:

```text
300 seconds
```

An immediate update can be requested with the **Refresh** button on the account-level device.

## Security

> [!CAUTION]
> The Cookie Header, and the `cookie.json` file produced in Browser Profile mode, grant access to an active One Hungary browser session. Treat both like a password.

Never publish or include session information in:

- GitHub issues
- Screenshots
- HAR files
- Home Assistant diagnostics shared publicly
- Log excerpts
- Chat messages
- Commits or configuration examples

This includes the contents of `cookie.json` and the `tools/one-browser-profile` directory (or wherever `--profile-dir` points), which contains a logged-in browser profile.

If a real Cookie Header or cookie.json is exposed, sign out of One Hungary to invalidate the session, sign in again, and create a new one.

## Known limitations

- Authentication is cookie-based; Home Assistant itself never performs an interactive login.
- Session renewal is not automated inside Home Assistant. In Browser Profile mode, renewal still requires running `tools/one_login.py` (headlessly for a routine cookie refresh, or with `--headed` once the session actually expires) outside of Home Assistant.
- An automated login (username/password, no browser) cannot be guaranteed to succeed, because the One Hungary login flow may present a reCAPTCHA challenge.
- One Hungary uses undocumented APIs that may change without notice.
- Not every subscription type returns the same data.
- Usage retrieval can fail independently for individual subscriptions.
- Allowance-specific entities are currently implemented only for selected allowances.
- The integration is read-only and does not modify subscriptions or services.

## Troubleshooting

### Authentication failed

- **Cookie Header mode**: sign in again, obtain a fresh Cookie Header, and reconfigure the integration.
- **Browser Profile mode**: delete `tools/one-browser-profile` (or your `--profile-dir`), run `tools/.venv/bin/python tools/one_login.py --headed`, then copy the resulting `cookie.json` to the path configured as the integration's **Cookie File Path** (e.g. `/config/custom_components/one_hu/cookie.json`), and wait for the next update (no reconfiguration needed).

### Integration does not appear

Verify that the following directory exists:

```text
/config/custom_components/one_hu
```

Then restart Home Assistant.

### New entities do not appear after updating

Reload the integration from **Settings > Devices & services**, or restart Home Assistant if Python platform files were added or changed.

### A subscription is unavailable

The One Hungary API may not return usage information for every subscription type. A failure for one subscription should not prevent other subscriptions from updating.

## Roadmap

Planned improvements include:

- Dynamic allowance entity discovery
- More allowance-specific sensors
- Improved account metadata
- Repair issue guiding users to re-run `tools/one_login.py` on session expiry
- Automatic secret redaction in diagnostics
- Hungarian translations
- Automated tests and validation
- Improved HACS and Home Assistant branding

## Development

Validate all Python modules before committing:

```bash
python3 -m py_compile custom_components/one_hu/*.py
```

Validate the manifest:

```bash
python3 -m json.tool custom_components/one_hu/manifest.json >/dev/null
```

The `tools/one_login.py` helper is not part of the Home Assistant integration and has its own dependencies (`tools/requirements.txt`). Validate it separately:

```bash
python3 -m py_compile tools/one_login.py
```

Recommended branch model:

```text
master   stable releases
develop  ongoing integration work
feature  isolated feature development
```

## Privacy

The integration communicates only with the One Hungary endpoints needed to retrieve account, subscription, service, and usage information. Credentials, cookies, and session tokens must not be exposed through logging or diagnostics.

## Disclaimer

Use this integration at your own risk. The maintainer is not responsible for authentication failures, service interruptions, API changes, data inaccuracies, or account-related issues caused by changes to the One Hungary platform.

## License

MIT License
