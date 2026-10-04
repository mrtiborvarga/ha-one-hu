#!/usr/bin/env python3
"""Standalone One Hungary login helper for the Browser Profile auth mode.

This script is NOT part of the Home Assistant integration runtime. It is run
manually (or via your own cron job) on a machine of your choosing, outside of
Home Assistant, to:

  1. Launch a real Chromium browser (via Playwright) against a persistent
     browser profile directory.
  2. Log in to https://www.one.hu if the stored profile session is missing or
     expired.
  3. Export the resulting session Cookie header to a JSON file that the
     Home Assistant "Browser Profile" authentication mode reads.

Home Assistant itself never launches a browser. It only reads the cookie file
this script produces. See tools/README-auth.md for setup and usage.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = "https://www.one.hu"
ACCOUNT_URL = f"{BASE_URL}/one-fiok"
LOGIN_INFO_URL = f"{BASE_URL}/o/ecare/loginInfo"

USERNAME_SELECTOR = "#loginForm\\:username"
PASSWORD_SELECTOR = "#loginForm\\:step0Password"
LOGIN_BUTTON_SELECTOR = "#loginForm\\:loginButton"
CAPTCHA_SELECTORS = ("#captchaFrame", ".captcha-challenge-container")

COOKIE_CONSENT_SELECTORS = (
    "button:has-text(\"Elfogadom\")",
    "button:has-text(\"Accept\")",
    "#onetrust-accept-btn-handler",
)

NAVIGATION_TIMEOUT_MS = 30_000
LOGIN_TIMEOUT_MS = 60_000


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--profile-dir",
        default=os.environ.get("ONE_HU_PROFILE_DIR", "one-browser-profile"),
        help="Persistent Playwright browser profile directory "
        "(default: %(default)s, or $ONE_HU_PROFILE_DIR)",
    )
    parser.add_argument(
        "--cookie-output",
        default=os.environ.get("ONE_HU_COOKIE_FILE", "cookie.json"),
        help="Path to write the exported cookie.json "
        "(default: %(default)s, or $ONE_HU_COOKIE_FILE)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Show the browser window. Required for the first login "
        "and whenever a CAPTCHA challenge must be solved manually.",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("ONE_HU_USERNAME"),
        help="One Hungary username (or $ONE_HU_USERNAME). "
        "Prompted interactively if not given and a login is needed.",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("ONE_HU_PASSWORD"),
        help="One Hungary password (or $ONE_HU_PASSWORD). "
        "Prompted interactively if not given and a login is needed.",
    )

    return parser.parse_args()


def dismiss_cookie_consent(page: Page) -> None:
    """Best-effort dismissal of the cookie consent banner."""
    for selector in COOKIE_CONSENT_SELECTORS:
        try:
            locator = page.locator(selector)
            locator.first.click(timeout=3_000)
            return
        except Exception:  # noqa: BLE001
            continue


def is_captcha_present(page: Page) -> bool:
    """Return whether a CAPTCHA challenge is currently visible."""
    for selector in CAPTCHA_SELECTORS:
        if page.locator(selector).count() > 0:
            return True
    return False


def check_session(page: Page) -> dict:
    """Call the loginInfo endpoint through the browser context and return it."""
    response = page.request.get(LOGIN_INFO_URL)

    if response.status in (204, 401, 403):
        return {"authorized": False, "active": False, "sessionInitialized": False}

    if not response.ok:
        raise RuntimeError(
            f"loginInfo request failed with status {response.status}: "
            f"{response.text()}"
        )

    return response.json()


def session_is_valid(login_info: dict) -> bool:
    """Return whether a loginInfo response represents a valid session."""
    return bool(
        login_info.get("authorized")
        and login_info.get("active")
        and login_info.get("sessionInitialized")
    )


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve the username and password from args, env vars, or the console."""
    username = args.username or input("One Hungary username: ")
    password = args.password or getpass.getpass("One Hungary password: ")
    return username, password


def perform_login(page: Page, username: str, password: str) -> None:
    """Fill and submit the One Hungary login form."""
    page.wait_for_selector(USERNAME_SELECTOR, timeout=LOGIN_TIMEOUT_MS)

    if is_captcha_present(page):
        raise RuntimeError(
            "A CAPTCHA challenge is displayed. Re-run this script with "
            "--headed and solve it manually in the browser window."
        )

    page.fill(USERNAME_SELECTOR, username)
    page.fill(PASSWORD_SELECTOR, password)

    login_button = page.locator(LOGIN_BUTTON_SELECTOR)
    if login_button.count() > 0:
        login_button.first.click()
    else:
        page.press(PASSWORD_SELECTOR, "Enter")

    page.wait_for_url(f"{BASE_URL}/one-fiok/**", timeout=LOGIN_TIMEOUT_MS)


def export_cookie_header(page: Page, output_path: Path) -> None:
    """Export the current session as a Cookie header to a JSON file."""
    cookies = page.context.cookies()
    relevant = [c for c in cookies if "one.hu" in c.get("domain", "")]

    if not relevant:
        raise RuntimeError("No one.hu cookies found in the browser context.")

    cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in relevant)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "cookie_header": cookie_header,
                "exported_at": datetime.now(UTC).isoformat(),
                "source": "tools/one_login.py",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    """Run the login/export workflow. Returns a process exit code."""
    args = parse_args()
    profile_dir = Path(args.profile_dir)
    cookie_output = Path(args.cookie_output)

    # Ask for credentials before opening the browser: if a (re-)login turns
    # out to be needed, they're already on hand and the flow isn't
    # interrupted partway through for console input.
    username = password = None
    if args.headed:
        username, password = resolve_credentials(args)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile_dir),
            headless=not args.headed,
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(ACCOUNT_URL, timeout=NAVIGATION_TIMEOUT_MS)
            dismiss_cookie_consent(page)

            login_info = check_session(page)

            if session_is_valid(login_info):
                print("Existing browser profile session is still valid.")
                export_cookie_header(page, cookie_output)
                print(f"Cookie header exported to {cookie_output}")
                return 0

            print("No valid session found in the browser profile. Logging in...")

            if not args.headed:
                print(
                    "Refusing to attempt login in headless mode: the initial "
                    "(or re-)login may require solving a CAPTCHA. Re-run with "
                    "--headed.",
                    file=sys.stderr,
                )
                return 1

            perform_login(page, username, password)
            dismiss_cookie_consent(page)

            login_info = check_session(page)

            if not session_is_valid(login_info):
                print(
                    "Login did not result in a valid session. "
                    f"loginInfo response: {login_info}",
                    file=sys.stderr,
                )
                return 1

            export_cookie_header(page, cookie_output)
            print(f"Login succeeded. Cookie header exported to {cookie_output}")
            return 0
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
