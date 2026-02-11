#!/usr/bin/env python3
"""
Epic Games Free Game Notifier
- Uses API to detect free games (fast and reliable)
- Sends email notification with game list
- You manually claim in real browser (most stable way)
"""
import os
import sys
import json
import smtplib
import requests
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

class FreeGameNotifier:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.project_dir = self.base_dir.parent
        load_dotenv(self.project_dir / '.env')

        self.db_file = self.project_dir / 'claimer' / 'data' / 'epic-games.json'
        self.log_file = self.base_dir / 'notifier.log'
        self.cookies_file = self.project_dir / 'claimer' / 'data' / 'cookies.json'
        self.owned_games_file = self.base_dir / 'owned_games.json'

        # Email config from .env
        self.smtp_config = {
            'host': os.getenv('SMTP_HOST', 'smtp.qq.com'),
            'port': int(os.getenv('SMTP_PORT', 465)),
            'user': os.getenv('SMTP_USER'),
            'pass': os.getenv('SMTP_PASS'),
            'to': os.getenv('TO_EMAIL') or os.getenv('SMTP_USER')
        }

        # Session for API requests
        self.session = None

    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except:
            pass

    def load_cookies(self):
        """Load cookies from file for ownership checking"""
        if not self.cookies_file.exists():
            self.log("⚠️  No cookies found, skipping ownership check")
            return False

        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)

            self.session = requests.Session()

            # Add cookies to session
            epic_eg1 = None
            for cookie in cookies:
                self.session.cookies.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain', '.epicgames.com'),
                    path=cookie.get('path', '/'),
                    secure=cookie.get('secure', True)
                )

                # Extract EPIC_EG1 for Authorization header
                if cookie['name'] == 'EPIC_EG1':
                    epic_eg1 = cookie['value']

            # Add headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://store.epicgames.com/',
            })

            # Add Authorization header if EPIC_EG1 token exists
            if epic_eg1:
                self.session.headers['Authorization'] = f'Bearer {epic_eg1}'
                self.log(f"✅ Loaded {len(cookies)} cookies + Authorization token")
            else:
                self.log(f"✅ Loaded {len(cookies)} cookies (no EG1 token found)")

            return True

        except Exception as e:
            self.log(f"⚠️  Failed to load cookies: {e}")
            return False

    def check_owned_games(self, games_info):
        """Check which games are already owned using entitlements API"""
        if not self.session:
            return {}  # Return empty dict if no session

        owned_status = {}

        # Get account_id from JWT token
        import base64

        account_id = None
        for cookie_name in ['EPIC_EG1']:
            cookie = self.session.cookies.get(cookie_name)
            if cookie:
                # Parse JWT to get account_id
                parts = cookie.split('~')
                if len(parts) > 1:
                    jwt_token = parts[1]
                    jwt_parts = jwt_token.split('.')
                    if len(jwt_parts) >= 2:
                        payload_b64 = jwt_parts[1]
                        padding = 4 - len(payload_b64) % 4
                        if padding != 4:
                            payload_b64 += '=' * padding
                        try:
                            payload_json = base64.urlsafe_b64decode(payload_b64)
                            payload = json.loads(payload_json)
                            account_id = payload.get('sub')
                            break
                        except:
                            pass

        if not account_id:
            self.log("⚠️  Could not extract account_id from token")
            return owned_status

        # Use entitlements API with account_id
        try:
            url = f'https://entitlement-public-service-prod08.ol.epicgames.com/entitlement/api/account/{account_id}/entitlements'

            # Get all entitlements (up to 5000)
            response = self.session.get(
                url,
                params={'start': 0, 'count': 5000},
                timeout=10
            )

            if response.status_code == 200:
                entitlements = response.json()
                owned_namespaces = set()
                owned_catalog_items = set()

                for item in entitlements:
                    if 'namespace' in item:
                        owned_namespaces.add(item['namespace'])
                    if 'catalogItemId' in item:
                        owned_catalog_items.add(item['catalogItemId'])

                # Check each game - 只看 namespace，因为 catalogItemId 可能不匹配
                for game in games_info:
                    game_id = game['id']
                    namespace = game.get('namespace', '')

                    # 只检查 namespace（最可靠的匹配方式）
                    is_owned = namespace in owned_namespaces
                    owned_status[game_id] = is_owned

                self.log(f"✅ Checked entitlements: {len(owned_namespaces)} namespaces, {len(owned_catalog_items)} items, {sum(owned_status.values())} games owned")
                return owned_status
            else:
                self.log(f"⚠️  Entitlements API returned {response.status_code}")

        except Exception as e:
            self.log(f"⚠️  Entitlements API failed: {e}")

        # If API fails, return empty (assume nothing owned)
        self.log("⚠️  Ownership check failed, treating all games as not owned")
        return owned_status

    def get_free_games_api(self):
        """Get free games list using API"""
        self.log("🔍 Fetching free games from Epic Games API...")

        try:
            response = requests.get(
                'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
                params={'locale': 'zh-CN', 'country': 'CN'},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])

            free_games = []
            for game in elements:
                promotions = game.get('promotions')
                if not promotions:
                    continue

                promo_offers = promotions.get('promotionalOffers', [])
                if not promo_offers or not promo_offers[0].get('promotionalOffers'):
                    continue

                # Check if actually free (not just discounted)
                price_info = game.get('price', {})
                total_price = price_info.get('totalPrice', {})
                discount_price = total_price.get('discountPrice', -1)

                # Skip if not free (discountPrice must be 0)
                if discount_price != 0:
                    continue

                # Get end date
                end_date_str = promo_offers[0]['promotionalOffers'][0].get('endDate', '')

                title = game.get('title', 'Unknown')
                description = game.get('description', '')[:200]  # Limit length
                game_id = game.get('id')

                # Get correct URL slug - always prefer offerMappings/catalogNs over urlSlug
                # because urlSlug is often inaccurate
                url_slug = None

                # Priority 1: offerMappings (most reliable)
                offer_mappings = game.get('offerMappings', [])
                if offer_mappings:
                    url_slug = offer_mappings[0].get('pageSlug')

                # Priority 2: catalogNs.mappings (also reliable)
                if not url_slug:
                    mappings = game.get('catalogNs', {}).get('mappings', [])
                    if mappings:
                        url_slug = mappings[0].get('pageSlug')

                # Priority 3: urlSlug or productSlug (fallback only)
                if not url_slug:
                    url_slug = game.get('urlSlug') or game.get('productSlug')

                if url_slug:
                    game_url = f"https://store.epicgames.com/zh-CN/p/{url_slug}"
                else:
                    game_url = "https://store.epicgames.com/zh-CN/free-games"

                free_games.append({
                    'id': game_id,
                    'namespace': game.get('namespace'),  # 添加 namespace 用于所有权检查
                    'title': title,
                    'description': description,
                    'url': game_url,
                    'end_date': end_date_str
                })

            self.log(f"✅ Found {len(free_games)} free games")
            return free_games

        except Exception as e:
            self.log(f"❌ Failed to fetch games: {e}")
            return []

    def load_notified_games(self):
        """Load list of games we've already notified about"""
        notified_file = self.base_dir / 'notified_games.json'
        if notified_file.exists():
            try:
                with open(notified_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_notified_game(self, game_id):
        """Save game ID to prevent duplicate notifications"""
        notified_file = self.base_dir / 'notified_games.json'
        notified = self.load_notified_games()
        if game_id not in notified:
            notified.append(game_id)
            # Keep only last 50 games
            notified = notified[-50:]
            with open(notified_file, 'w') as f:
                json.dump(notified, f)

    def load_owned_games(self):
        """Load manually marked owned games"""
        if self.owned_games_file.exists():
            try:
                with open(self.owned_games_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def mark_game_as_owned(self, game_id):
        """Mark a game as owned (after manually claiming)"""
        owned = self.load_owned_games()
        if game_id not in owned:
            owned.append(game_id)
            with open(self.owned_games_file, 'w') as f:
                json.dump(owned, f)

    def send_email(self, new_games):
        """Send email notification about new free games"""
        if not self.smtp_config['user'] or not self.smtp_config['pass']:
            self.log("⚠️  Email not configured, skipping notification")
            return False

        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Epic Games Notifier <{self.smtp_config['user']}>"
            msg['To'] = self.smtp_config['to']
            msg['Subject'] = f"🎁 {len(new_games)} 款新的 Epic Games 免费游戏！"

            # Create HTML email body
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .game {{
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        background: #f9f9f9;
                    }}
                    .game-title {{
                        color: #0078f2;
                        font-size: 18px;
                        font-weight: bold;
                        margin-bottom: 8px;
                    }}
                    .game-desc {{ color: #666; margin: 8px 0; }}
                    .claim-btn {{
                        display: inline-block;
                        background: #0078f2;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 10px;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        color: #888;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <h2>🎮 Epic Games 新的免费游戏</h2>
                <p>发现 <strong>{len(new_games)}</strong> 款新的免费游戏！</p>
            """

            for game in new_games:
                html_body += f"""
                <div class="game">
                    <div class="game-title">{game['title']}</div>
                    <div class="game-desc">{game['description'] or '暂无描述'}</div>
                    <a href="{game['url']}" class="claim-btn">立即领取</a>
                </div>
                """

            html_body += f"""
                <div class="footer">
                    <p>💡 请在真实浏览器中打开链接并手动领取游戏。</p>
                    <p>📅 通知时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>🤖 由 Epic Games Free Game Notifier 自动发送</p>
                </div>
            </body>
            </html>
            """

            # Plain text version
            text_body = f"Epic Games 新的免费游戏\n\n发现 {len(new_games)} 款新游戏：\n\n"
            for game in new_games:
                text_body += f"📦 {game['title']}\n{game['url']}\n\n"
            text_body += f"\n通知时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP_SSL(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.login(self.smtp_config['user'], self.smtp_config['pass'])
                server.send_message(msg)

            self.log(f"✅ Email notification sent to {self.smtp_config['to']}")
            return True

        except Exception as e:
            self.log(f"❌ Failed to send email: {e}")
            return False

    def run(self):
        """Main execution"""
        self.log("=" * 70)
        self.log("Epic Games Free Game Notifier")
        self.log("=" * 70)

        # Get free games
        games = self.get_free_games_api()

        if not games:
            self.log("❌ No games found or API unavailable")
            return False

        # Load cookies for API-based ownership check
        has_cookies = self.load_cookies()

        # Check which games are already owned via API
        if has_cookies:
            owned_status = self.check_owned_games(games)

            # Filter out API-owned games
            api_owned_games = []
            unowned_games = []

            for game in games:
                if owned_status.get(game['id'], False):
                    api_owned_games.append(game['title'])
                else:
                    unowned_games.append(game)

            if api_owned_games:
                self.log(f"✅ Already owned via API ({len(api_owned_games)}): {', '.join(api_owned_games)}")

            games = unowned_games  # Only consider API-unowned games

        # Also filter out manually marked owned games
        owned_game_ids = self.load_owned_games()
        manual_owned_games = []
        final_unowned_games = []

        for game in games:
            if game['id'] in owned_game_ids:
                manual_owned_games.append(game['title'])
            else:
                final_unowned_games.append(game)

        if manual_owned_games:
            self.log(f"✅ Already owned (manually marked, {len(manual_owned_games)}): {', '.join(manual_owned_games)}")

        games = final_unowned_games  # Only consider unowned games

        if not games:
            self.log("✅ All free games are already owned")
            return True

        # Check which games are new (not notified before)
        notified = self.load_notified_games()
        new_games = [g for g in games if g['id'] not in notified]

        if not new_games:
            self.log("✅ No new games - all games already notified")
            self.log("\n📋 Current free games:")
            for game in games:
                self.log(f"   📦 {game['title']}")
            return True

        # Show new games
        self.log(f"\n🆕 Found {len(new_games)} NEW game(s):")
        for game in new_games:
            self.log(f"   🎁 {game['title']}")
            self.log(f"      {game['url']}")

        # Send notification
        if self.send_email(new_games):
            # Mark as notified
            for game in new_games:
                self.save_notified_game(game['id'])
            self.log("\n✅ Notification sent successfully!")
        else:
            self.log("\n⚠️  Failed to send notification")

        self.log("\n💡 Please manually claim games in your browser:")
        self.log("   https://store.epicgames.com/zh-CN/free-games")

        return True

if __name__ == '__main__':
    notifier = FreeGameNotifier()
    success = notifier.run()
    sys.exit(0 if success else 1)
