# Unofficial One Hungary

Unofficial Home Assistant integration for One Hungary mobile subscriptions.

> ⚠️ This project is not affiliated with, endorsed by, or maintained by One Hungary.

## Features

Planned support for:

- Mobile subscriptions
- Prepaid balances
- Remaining allowance bundles
- Data usage information
- Expiry information
- HACS installation
- Home Assistant Config Flow

## Current Status

Early development.

The integration is currently able to:

- Discover mobile subscriptions through the One eCare API
- Retrieve usage information for supported subscriptions

Home Assistant platform support is currently under development.

## Installation

### HACS

1. Add this repository as a custom repository in HACS
2. Category: Integration
3. Install "Unofficial One Hungary"
4. Restart Home Assistant

### Manual

Copy:

```text
custom_components/one_hu
```

to your Home Assistant:

```text
config/custom_components/
```

Restart Home Assistant.

## Authentication

The current development version uses:

- Session Cookie
- CSRF Token

Future versions may support automated authentication if technically feasible.

## Disclaimer

This integration relies on unofficial APIs which may change without notice.

Use at your own risk.

## License

MIT License