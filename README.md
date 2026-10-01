Review your One account SIMs and details.

## Authentication

The integration currently requires an authenticated browser session from One Hungary.

### How to obtain the Cookie Header

1. Log in to your One Hungary account.
2. Press `F12` to open Developer Tools.
3. Open the **Network** tab.
4. Refresh the page.
5. Open a request similar to:

```text
https://www.one.hu/o/nc-framework-kernel/localization/getJson?locale=hu_HU
```

6. Open **Request Headers**.
7. Locate the header named:

```text
Cookie
```

8. Copy the **entire Cookie header value**.

Example:

```text
JSESSIONID_VHPRTP_7500=...; CSRF_TOKEN=...; LFR_SESSION_STATE_20105=...;
```

9. Paste the complete value into the Home Assistant configuration field.

### Notes

- The session will eventually expire.
- If the integration stops working, obtain a new Cookie Header.
- Future versions may support automatic authentication.