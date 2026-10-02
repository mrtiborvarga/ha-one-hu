<p align="center">
  <img src="assets/logo.png" width="220">
ungary

Unofficial Home Assistant integration for One Hungary mobile subscriptions.

> ⚠️ This project is not affiliated with, endorsed by, or maintained by One Hungary.

## Features

### Account Overview

Dedicated account-level device:

```text
One Hungary
```

Provides:

- Mobile Services Count
- API Status
- Last Successful Sync
- Refresh Button

### Mobile Subscription Monitoring

Each subscription appears as a separate Home Assistant device.

Example:

```text
One Hungary 36309742918
```

### Subscription Information

Available sensors:

- Balance
- Days Available
- Tariff
- Subscription Status

### Mobile Data Usage

Available sensors:

- Data Allowance
- Data Remaining
- Data Used
- Data Used Percentage
- Data Expires In

Example:

```text
Data Allowance      5.0 GB
Data Remaining      2.1 GB
Data Used           2.9 GB
Data Used %         57.8 %
Data Expires In     18 days
```

### Bundle and Allowance Monitoring

Currently supported:

- 100MB adat Remaining
- 100MB adat Expires In

### Service Monitoring

The integration exposes service status information through binary sensors.

Examples:

- Call Hold
- Call Waiting
- Call Forwarding
- Caller ID
- Caller ID Restriction
- MMS
- Mobile Purchase
- Roaming Services
- Roaming Welcome SMS
- Adult Content Filtering

### Binary Sensors

- Prepaid
- eSIM
- Barred

## Installation

### HACS

1. Open HACS
2. Add this repository as a Custom Repository
3. Category: Integration
4. Install **Unofficial One Hungary**
5. Restart Home Assistant

### Manual

Copy:

```text
custom_components/one_hu
```

to:

```text
/config/custom_components/
```

Restart Home Assistant.

## Authentication

The integration currently uses an authenticated One Hungary browser session.

### Cookie Header Extraction

1. Login to One Hungary
2. Press `F12`
3. Open the **Network** tab
4. Reload the page
5. Open:

```text
/o/nc-framework-kernel/localization/getJson?locale=hu_HU
```

6. Open **Request Headers**
7. Locate:

```text
Cookie:
```

8. Copy the full value
9. Paste it into the integration configuration

Example:

```text
JSESSIONID=...
CSRF_TOKEN=...
...
```

### Session Expiration

Sessions eventually expire.

If authentication stops working:

1. Login again
2. Obtain a fresh Cookie Header
3. Update the integration configuration

## Current Status

Current release: **v0.2.8 development branch**

Implemented:

✅ Account device

✅ Subscription devices

✅ Balance monitoring

✅ Data monitoring

✅ Service status monitoring

✅ API status monitoring

✅ Manual refresh

## Screenshots

Add screenshots here after the account model is finalized.

## Known Limitations

- Browser Cookie Header authentication is still required
- Session renewal is not yet automatic
- One Hungary APIs are undocumented
- APIs may change without notice

## Roadmap

### v0.2.x

- Account device improvements
- Additional allowance sensors

### v0.3.x

- Dynamic allowance discovery
- Customer/account metadata
- Enhanced diagnostics

### Future

- Automated session renewal
- Repair flow
- Additional service management capabilities

## Security Warning

Never share:

- Cookie Header
- Session identifiers
- Authentication tokens
- HAR files containing authentication information

Treat these values like passwords.

## License

MIT License
