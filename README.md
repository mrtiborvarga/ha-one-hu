<p align="center">
  <img src="custom_components/one_hu/assets/logo.png" width="180" alt="Unofficial One Hungary logo">
</p>

# Unofficial One Hungary

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5)
![HACS](https://img.shields.io/badge/HACS-Compatible-41BDF5)
![Version](https://img.shields.io/badge/version-0.3.0-orange)
![License](https://img.shields.io/badge/license-MIT-green)

An unofficial Home Assistant custom integration for monitoring One Hungary mobile subscriptions, balances, data usage, allowances, account status, and mobile services.

> [!WARNING]
> This project is not affiliated with, endorsed by, or maintained by One Hungary. It uses undocumented interfaces that may change without notice.

## Highlights

- Installation through HACS
- Home Assistant Config Flow
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
5. Install **Unofficial One Hungary**.
6. Restart Home Assistant.
7. Open **Settings > Devices & services > Add integration**.
8. Search for **Unofficial One Hungary**.

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

Restart Home Assistant, then add **Unofficial One Hungary** under **Settings > Devices & services**.

## Authentication

The integration currently uses an authenticated One Hungary browser session. It requires the complete value of the browser request's `Cookie` header.

### Obtain the Cookie Header

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
10. Paste the value into the integration's **Cookie Header** field.

Example format:

```text
JSESSIONID_VHPRTP_7500=...; CSRF_TOKEN=...; LFR_SESSION_STATE_20105=...; ...
```

The integration extracts the `CSRF_TOKEN` value and uses the supplied Cookie Header for authenticated requests.

### Session expiration

Browser sessions eventually expire. If authentication fails or entities become unavailable:

1. Sign in to One Hungary again.
2. obtain a fresh Cookie Header using the procedure above.
3. Reconfigure the integration with the new value.

## Update behavior

The integration uses Home Assistant's `DataUpdateCoordinator`.

Default polling interval:

```text
300 seconds
```

An immediate update can be requested with the **Refresh** button on the account-level device.

## Security

> [!CAUTION]
> The Cookie Header grants access to an active One Hungary browser session. Treat it like a password.

Never publish or include session information in:

- GitHub issues
- Screenshots
- HAR files
- Home Assistant diagnostics shared publicly
- Log excerpts
- Chat messages
- Commits or configuration examples

If a real Cookie Header is exposed, sign out of One Hungary to invalidate the session, sign in again, and create a new one.

## Known limitations

- Authentication is manual and cookie-based.
- Session renewal is not automated.
- One Hungary uses undocumented APIs that may change without notice.
- Not every subscription type returns the same data.
- Usage retrieval can fail independently for individual subscriptions.
- Allowance-specific entities are currently implemented only for selected allowances.
- The integration is read-only and does not modify subscriptions or services.

## Troubleshooting

### Authentication failed

Sign in again, obtain a fresh Cookie Header, and reconfigure the integration.

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
- Reauthentication and repair flow
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
