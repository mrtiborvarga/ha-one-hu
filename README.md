<p align="center">
  <img src="assets/logo.png" width="160" alt="Unofficial Assistant](https://img.shields.io/tant-Custom%20Integration-blue
![Hps://img.shields.io/badge/HACS-Compatible-green
![Versionmg.shields.io/badge/Version-0.3.0-orange

Unofficial Home Assistant integration for monitoring **One Hungary** mobile subscriptions, balances, mobile data usage, services and account-level information.

> ⚠️ This project is not affiliated with, endorsed by, or maintained by One Hungary.

---

# Features

## Account-Level Monitoring

Dedicated account device:

```text
One Hungary
```

Provides:

- Mobile Services Count
- API Status
- Last Successful Sync
- Manual Refresh

---

## Subscription Monitoring

Each mobile subscription appears as a separate Home Assistant device.

Example:

```text
One Hungary 36309742918
```

---

## Subscription Information

Available sensors:

- Balance
- Days Available
- Tariff
- Subscription Status

---

## Mobile Data Usage

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

---

## Allowance Monitoring

Currently supported:

```text
100MB adat Remaining
100MB adat Expires In
```

---

## Service Monitoring

The integration exposes service states through binary sensors.

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

---

## Binary Sensors

Available binary sensors:

- Prepaid
- eSIM
- Barred

---

# Installation

## HACS

1. Open HACS
2. Add this repository as a Custom Repository
3. Category: **Integration**
4. Install **Unofficial One Hungary**
5. Restart Home Assistant

## Manual Installation

Copy:

```text
custom_components/one_hu
```

to:

```text
/config/custom_components/
```

Restart Home Assistant.

---

# Authentication

The integration currently uses an authenticated One Hungary browser session.

## Cookie Header Extraction

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

---

## Session Expiration

Sessions eventually expire.

If authentication stops working:

1. Login again
2. Obtain a fresh Cookie Header
3. Update the integration configuration

---

# Account Device

The integration creates an account-level device:

```text
One Hungary
```

Entities:

```text
API Status
Last Successful Sync
Mobile Services Count
Refresh
```

---

# Subscription Devices

Each discovered mobile subscription creates a separate Home Assistant device.

Example:

```text
One Hungary 36309742918
```

Entities:

### General

```text
Balance
Days Available
Tariff
Subscription Status
```

### Data Usage

```text
Data Allowance
Data Remaining
Data Used
Data Used Percentage
Data Expires In
```

### Binary Sensors

```text
Prepaid
eSIM
Barred
```

### Service Status

```text
Call Hold
Call Waiting
Call Forwarding
Caller ID
MMS
Roaming
...
```

---

# Update Interval

Default update interval:

```text
300 seconds
```

Manual refresh is available through the account-level Refresh button.

---

# Security Warning

The Cookie Header grants access to an active One Hungary session.

Treat it like a password.

Never share:

- Cookie Headers
- Session IDs
- Authentication Tokens
- HAR files
- Screenshots containing authentication information

If a Cookie Header is accidentally exposed:

1. Sign out of One Hungary
2. Sign in again
3. Obtain a new Cookie Header

---

# Known Limitations

- Browser Cookie Header authentication is still required
- Session renewal is not yet automatic
- One Hungary APIs are undocumented
- APIs may change without notice

---

# Roadmap

## v0.3.x

- Dynamic allowance discovery
- Additional allowance sensors
- Improved account-level metadata

## Future

- Automatic session renewal
- Repair workflow
- Additional service management capabilities
- HACS / Brands integration

---

# Troubleshooting

## Authentication Failed

1. Login again
2. Obtain a fresh Cookie Header
3. Update the integration

## Missing Sensors

Reload the integration or restart Home Assistant.

## Empty Usage Data

Some subscription types do not expose the same level of information through the One Hungary APIs.

---

# Development

Validate Python files:

```bash
python3 -m py_compile custom_components/one_hu/*.py
```

Validate manifest:

```bash
python3 -m json.tool custom_components/one_hu/manifest.json >/dev/null
```

---

# License

MIT License
