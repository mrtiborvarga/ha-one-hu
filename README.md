# Unofficial One Hungary

Unofficial Home Assistant integration for One Hungary mobile subscriptions.

> ⚠️ This project is not affiliated with, endorsed by, or maintained by One Hungary.

## Features

Current development goals:

- Discover mobile subscriptions
- Display prepaid balances
- Display remaining data allowances
- Display available bundles
- Display subscription status
- Home Assistant Config Flow
- HACS support

## Current Status

🚧 Early development

The integration is under active development and should currently be considered experimental.

## Installation

### HACS

1. Open HACS
2. Add this repository as a custom repository
3. Category: **Integration**
4. Search for **Unofficial One Hungary**
5. Download
6. Restart Home Assistant

### Manual Installation

Copy:

```text
custom_components/one_hu
```

into:

```text
/config/custom_components/
```

Restart Home Assistant.

## Configuration

The current development version requires a valid authenticated browser session.

### Cookie Header

The integration currently uses a browser session exported from the One Hungary customer portal.

Future versions may support automated authentication, depending on what is technically possible.

## Planned Sensors

Examples:

- Mobile balance
- Remaining allowance
- Data usage
- Days remaining
- Subscription status

## Development

Repository:

```text
https://github.com/mrtiborvarga/ha-one-hu
```

Development branch:

```text
develop
```

## Disclaimer

This integration relies on unofficial APIs which may change without notice.

Use at your own risk.

## License

MIT
