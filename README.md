# Unofficial One Hungary

Unofficial Home Assistant custom integration for displaying One Hungary mobile subscriptions and usage information.

> [!WARNING]
> This project is not affiliated with, endorsed by, or maintained by One Hungary.
> It uses undocumented interfaces that may change without notice.

## Features

- HACS installation
- Home Assistant Config Flow
- Discovery of mobile subscriptions linked to a One account
- Mobile subscription count sensor
- Per-subscription Home Assistant device
- Per-subscription balance sensor
- Per-subscription available-days sensor
- Per-subscription bundle count sensor
- Per-subscription bucket count sensor
- Coordinator-based periodic updates

## Current status

This integration is under active development and should be considered experimental.

The current authentication method requires the complete `Cookie` request-header value from an authenticated One Hungary browser session. The browser session eventually expires and must then be replaced manually.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Open **Custom repositories**.
3. Add the repository:
   [mrtiborvarga/ha-one-hu](https://github.com/mrtiborvarga/ha-one-hu)
4. Select **Integration** as the category.
5. Download **Unofficial One Hungary**.
6. Restart Home Assistant.
7. Open **Settings > Devices & services > Add integration**.
8. Search for **Unofficial One Hungary**.

## Manual installation

Copy the following directory:

```text
custom_components/one_hu
```

into the Home Assistant configuration directory:

```text
/config/custom_components/one_hu
```

Restart Home Assistant, then add **Unofficial One Hungary** under **Settings > Devices & services**.

## Authentication

### Obtain the Cookie Header

1. Sign in to your One Hungary account in a desktop browser.
2. While signed in, open the following lightweight endpoint:
   [One Hungary localization endpoint](https://www.one.hu/o/nc-framework-kernel/localization/getJson?locale=hu_HU)
3. Open Developer Tools by pressing `F12`.
4. Select the **Network** tab.
5. Reload the page.
6. Select the request whose URL ends with:

   ```text
   /o/nc-framework-kernel/localization/getJson?locale=hu_HU
   ```

7. Open **Request Headers**.
8. Locate the header named `Cookie`.
9. Copy the entire value after `Cookie:`. Do not include the word `Cookie:` itself.
10. Paste the complete value into the integration's **Cookie Header** field.

Example format:

```text
JSESSIONID_VHPRTP_7500=...; CSRF_TOKEN=...; LFR_SESSION_STATE_20105=...; ...
```

The integration extracts the `CSRF_TOKEN` value from the supplied Cookie Header and uses the complete header for authenticated One eCare API requests.

### Session expiry

The browser session eventually expires. If entities become unavailable or authentication fails:

1. Sign in to One Hungary again.
2. Obtain a fresh Cookie Header using the procedure above.
3. Reconfigure the integration with the new value.

## Entities

### Account-level entity

- **Mobile services count**: number of mobile subscriptions discovered in the One account.

### Per-subscription entities

For every discovered MSISDN, the integration creates a Home Assistant device and these sensors:

- **Balance**: prepaid balance when returned by the One API.
- **Days available**: number of days reported by the usage endpoint.
- **Bundles count**: number of returned bundle objects.
- **Buckets count**: number of returned bucket objects.

Some subscriptions may not expose all usage information. Sensors for such subscriptions can be unavailable while other subscriptions continue to update.

## Update interval

The integration polls One Hungary periodically through Home Assistant's `DataUpdateCoordinator`. The current default interval is 300 seconds.

## Security warning

The Cookie Header grants access to the active One Hungary browser session. Treat it like a password.

Never include it in:

- GitHub issues
- screenshots
- Home Assistant diagnostics shared publicly
- log excerpts
- chat messages
- commits or configuration examples

If a real Cookie Header is accidentally disclosed, sign out of One Hungary to invalidate the session and sign in again before creating a new one.

## Known limitations

- Authentication is manual and cookie-based.
- Session renewal is not automated.
- One Hungary uses undocumented APIs that can change without notice.
- Bundle and bucket details are currently exposed only as counts.
- Usage retrieval can fail independently for individual subscriptions.

## Planned improvements

- Reauthentication and repair flow
- Individual bundle and allowance sensors
- Remaining data-volume sensors
- Expiry timestamp sensors
- Better diagnostics with automatic secret redaction
- Hungarian translation
- Tests and automated validation

## Troubleshooting

### Integration cannot authenticate

Obtain a fresh Cookie Header from a newly authenticated browser session and reconfigure the integration.

### Integration does not appear after installation

Restart Home Assistant and verify that this directory exists:

```text
/config/custom_components/one_hu
```

### An individual subscription is unavailable

The One usage endpoint may not return data for every subscription type. Other subscriptions should continue to work.

## Development

The active development branch is `develop`. Stable releases are published as GitHub releases and can be installed through HACS.

Before committing Python changes, run:

```bash
python3 -m py_compile \
  custom_components/one_hu/__init__.py \
  custom_components/one_hu/api.py \
  custom_components/one_hu/config_flow.py \
  custom_components/one_hu/coordinator.py \
  custom_components/one_hu/sensor.py
```

Validate the manifest with:

```bash
python3 -m json.tool custom_components/one_hu/manifest.json > /dev/null
```

## Privacy

The integration sends requests only to One Hungary endpoints required to retrieve subscription and usage information. Credentials and session data must not be logged or exposed in diagnostics.

## Disclaimer

Use this integration at your own risk. The maintainer is not responsible for account access issues, service changes, data inaccuracies, or interruptions caused by changes to the One Hungary website or APIs.

## License

MIT License
