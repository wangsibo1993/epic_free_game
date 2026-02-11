#!/usr/bin/env python3
"""
Cookie Manager - Advanced cookie extraction and management
Handles cookie validation, refresh, and automatic updates
"""
import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

try:
    import browser_cookie3
    BROWSER_COOKIE_AVAILABLE = True
except ImportError:
    BROWSER_COOKIE_AVAILABLE = False

class CookieManager:
    """Manage Epic Games cookies with validation and refresh"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.cookies_file = self.base_dir / 'claimer' / 'data' / 'cookies.json'
        self.cookies_backup_dir = self.base_dir / 'claimer' / 'data' / 'cookies_backup'
        self.cookies_backup_dir.mkdir(parents=True, exist_ok=True)

        # Browser cookie database paths
        self.browser_paths = {
            'chrome': Path.home() / 'Library/Application Support/Google/Chrome/Default/Cookies',
            'edge': Path.home() / 'Library/Application Support/Microsoft Edge/Default/Cookies',
            'brave': Path.home() / 'Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies',
        }

    def backup_cookies(self):
        """Backup current cookies"""
        if self.cookies_file.exists():
            backup_name = f"cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.cookies_backup_dir / backup_name
            shutil.copy2(self.cookies_file, backup_path)
            print(f"✅ Backed up cookies to: {backup_path}")

            # Keep only last 10 backups
            backups = sorted(self.cookies_backup_dir.glob('cookies_*.json'))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()

    def extract_from_browser(self, browser='chrome'):
        """Extract cookies from specified browser using browser-cookie3"""
        if not BROWSER_COOKIE_AVAILABLE:
            raise ImportError("browser-cookie3 is required. Install with: pip3 install browser-cookie3")

        if browser not in self.browser_paths:
            raise ValueError(f"Unsupported browser: {browser}")

        db_path = self.browser_paths[browser]

        if not db_path.exists():
            raise FileNotFoundError(f"{browser.title()} cookies database not found: {db_path}")

        cookies = []
        try:
            # Use browser-cookie3 to extract cookies
            if browser == 'chrome':
                cj = browser_cookie3.chrome(domain_name='epicgames.com')
            elif browser == 'edge':
                cj = browser_cookie3.edge(domain_name='epicgames.com')
            elif browser == 'brave':
                cj = browser_cookie3.brave(domain_name='epicgames.com')
            else:
                raise ValueError(f"Unsupported browser: {browser}")

            for cookie in cj:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value or '',
                    'domain': cookie.domain or '.epicgames.com',
                    'path': cookie.path or '/',
                    'expires': cookie.expires or -1,
                    'httpOnly': bool(cookie.has_nonstandard_attr('HttpOnly')),
                    'secure': bool(cookie.secure),
                    'sameSite': 'None' if cookie.secure else 'Lax'
                })

        except Exception as e:
            raise Exception(f"Failed to extract cookies from {browser}: {e}")

        return cookies

    def validate_cookies(self, cookies):
        """Validate cookie completeness and freshness"""
        if not cookies:
            return False, "No cookies provided"

        # Check for critical cookies
        critical_cookies = ['EPIC_SSO', 'EPIC_BEARER_TOKEN']
        found_cookies = {c['name']: c for c in cookies}

        missing = [name for name in critical_cookies if name not in found_cookies]
        if missing:
            return False, f"Missing critical cookies: {', '.join(missing)}"

        # Check expiration
        now = time.time()
        expired = []
        for cookie in cookies:
            if cookie['expires'] > 0 and cookie['expires'] < now:
                expired.append(cookie['name'])

        if expired:
            return False, f"Expired cookies: {', '.join(expired[:5])}"

        return True, "Cookies are valid"

    def load_cookies(self):
        """Load cookies from file"""
        if not self.cookies_file.exists():
            return None

        try:
            with open(self.cookies_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load cookies: {e}")
            return None

    def save_cookies(self, cookies):
        """Save cookies to file"""
        self.cookies_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Saved {len(cookies)} cookies to: {self.cookies_file}")

    def get_cookie_info(self, cookies):
        """Get information about cookies"""
        if not cookies:
            return {}

        info = {
            'count': len(cookies),
            'domains': list(set(c['domain'] for c in cookies)),
            'critical_cookies': {},
            'expiration': {}
        }

        # Check critical cookies
        critical = ['EPIC_SSO', 'EPIC_BEARER_TOKEN', 'EPIC_DEVICE', 'eg-auth']
        for name in critical:
            cookie = next((c for c in cookies if c['name'] == name), None)
            if cookie:
                expires = cookie.get('expires', -1)
                if expires > 0:
                    expires_dt = datetime.fromtimestamp(expires)
                    days_left = (expires_dt - datetime.now()).days
                    info['critical_cookies'][name] = {
                        'found': True,
                        'expires': expires_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'days_left': days_left
                    }
                else:
                    info['critical_cookies'][name] = {
                        'found': True,
                        'expires': 'Session cookie',
                        'days_left': -1
                    }
            else:
                info['critical_cookies'][name] = {'found': False}

        return info

    def check_need_refresh(self):
        """Check if cookies need refresh"""
        cookies = self.load_cookies()

        if not cookies:
            return True, "No cookies file found"

        valid, message = self.validate_cookies(cookies)
        if not valid:
            return True, message

        # Check if close to expiration (< 7 days)
        info = self.get_cookie_info(cookies)
        for name, data in info['critical_cookies'].items():
            if data.get('found') and data.get('days_left', -1) >= 0:
                if data['days_left'] < 7:
                    return True, f"{name} expires in {data['days_left']} days"

        return False, "Cookies are fresh"

    def auto_refresh(self):
        """Automatically refresh cookies from browser"""
        print("🔄 Auto-refreshing cookies...")

        # Backup existing cookies
        if self.cookies_file.exists():
            self.backup_cookies()

        # Try each browser
        for browser in ['chrome', 'edge', 'brave']:
            try:
                print(f"\n🔍 Trying {browser.title()}...")
                cookies = self.extract_from_browser(browser)

                if not cookies:
                    print(f"   ⚠️  No Epic Games cookies found in {browser.title()}")
                    continue

                # Validate
                valid, message = self.validate_cookies(cookies)
                if not valid:
                    print(f"   ⚠️  Invalid cookies: {message}")
                    continue

                # Save
                self.save_cookies(cookies)

                # Show info
                info = self.get_cookie_info(cookies)
                print(f"\n   ✅ Successfully extracted from {browser.title()}")
                print(f"   📊 Cookie count: {info['count']}")
                print(f"   🔑 Critical cookies:")
                for name, data in info['critical_cookies'].items():
                    if data.get('found'):
                        expires_info = data.get('expires', 'Unknown')
                        days_left = data.get('days_left', -1)
                        if days_left >= 0:
                            print(f"      • {name}: expires in {days_left} days")
                        else:
                            print(f"      • {name}: {expires_info}")

                return True

            except FileNotFoundError:
                print(f"   ⏭️  {browser.title()} not found, skipping...")
                continue
            except Exception as e:
                print(f"   ❌ Error with {browser.title()}: {e}")
                continue

        print("\n❌ Failed to extract cookies from any browser")
        print("   Please make sure:")
        print("   1. You're logged into Epic Games in Chrome/Edge/Brave")
        print("   2. The browser is completely closed")
        print("   3. You've visited https://store.epicgames.com recently")

        return False

    def info(self):
        """Display information about current cookies"""
        print("=" * 70)
        print("Cookie Status")
        print("=" * 70)

        cookies = self.load_cookies()

        if not cookies:
            print("\n❌ No cookies file found")
            print(f"   Expected location: {self.cookies_file}")
            print("\n💡 Run: python3 cookie_manager.py refresh")
            return

        info = self.get_cookie_info(cookies)

        print(f"\n📊 Cookie Statistics:")
        print(f"   Total cookies: {info['count']}")
        print(f"   Domains: {', '.join(info['domains'])}")

        print(f"\n🔑 Critical Cookies:")
        all_found = True
        for name, data in info['critical_cookies'].items():
            if data.get('found'):
                status = "✅"
                expires_info = data.get('expires', 'Unknown')
                days_left = data.get('days_left', -1)

                if days_left >= 0:
                    if days_left < 7:
                        status = "⚠️ "
                        expires_info = f"EXPIRES IN {days_left} DAYS"
                    else:
                        expires_info = f"Expires in {days_left} days"

                print(f"   {status} {name}: {expires_info}")
            else:
                all_found = False
                print(f"   ❌ {name}: Not found")

        # Validation
        valid, message = self.validate_cookies(cookies)

        print(f"\n🔍 Validation:")
        if valid:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")

        # Recommendation
        print(f"\n💡 Recommendation:")
        need_refresh, reason = self.check_need_refresh()
        if need_refresh:
            print(f"   ⚠️  {reason}")
            print(f"   Run: python3 cookie_manager.py refresh")
        else:
            print(f"   ✅ {reason}")
            print(f"   No action needed")

        print("\n" + "=" * 70)


def main():
    manager = CookieManager()

    if len(sys.argv) < 2:
        # Default: show info
        manager.info()
    else:
        command = sys.argv[1].lower()

        if command == 'refresh':
            success = manager.auto_refresh()
            sys.exit(0 if success else 1)

        elif command == 'info':
            manager.info()

        elif command == 'backup':
            manager.backup_cookies()

        elif command == 'check':
            need_refresh, reason = manager.check_need_refresh()
            print(f"Need refresh: {need_refresh}")
            print(f"Reason: {reason}")
            sys.exit(0 if not need_refresh else 1)

        else:
            print("Usage: python3 cookie_manager.py [command]")
            print()
            print("Commands:")
            print("  info     - Show cookie status (default)")
            print("  refresh  - Extract cookies from browser")
            print("  backup   - Backup current cookies")
            print("  check    - Check if refresh needed")
            print()
            print("Examples:")
            print("  python3 cookie_manager.py")
            print("  python3 cookie_manager.py refresh")
            print("  python3 cookie_manager.py info")


if __name__ == '__main__':
    main()
