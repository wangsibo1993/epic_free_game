#!/usr/bin/env python3
"""
Epic Games Auto Claimer - Full API Implementation
Uses reverse-engineered API to automatically claim free games
"""
import os
import sys
import json
import time
import random
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode

class EpicGamesAPI:
    """Epic Games API client with anti-detection measures"""

    def __init__(self, cookies_file='claimer/data/cookies.json'):
        self.base_dir = Path(__file__).parent
        self.cookies_file = self.base_dir / cookies_file
        self.session = requests.Session()

        # API endpoints (discovered through network analysis)
        self.endpoints = {
            'free_games': 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
            'graphql': 'https://graphql.epicgames.com/graphql',
            'library': 'https://library-service.live.use1a.on.epicgames.com/library/api/public/items',
            'order_preview': 'https://payment-website-pci.ol.epicgames.com/purchase/order-preview',
            'order_confirm': 'https://payment-website-pci.ol.epicgames.com/purchase/confirm-order',
        }

        # User agents pool for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        ]

        self._setup_session()

    def _setup_session(self):
        """Setup session with anti-detection headers"""
        # Rotate user agent
        user_agent = random.choice(self.user_agents)

        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://store.epicgames.com',
            'Referer': 'https://store.epicgames.com/',
            'Sec-Ch-Ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        })

    def load_cookies(self):
        """Load cookies from file"""
        if not self.cookies_file.exists():
            raise FileNotFoundError(f"Cookie file not found: {self.cookies_file}")

        with open(self.cookies_file, 'r') as f:
            cookies = json.load(f)

        # Add cookies to session
        for cookie in cookies:
            self.session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain', '.epicgames.com'),
                path=cookie.get('path', '/'),
                secure=cookie.get('secure', True)
            )

        print(f"✅ Loaded {len(cookies)} cookies")

        # Extract bearer token from cookies if available
        bearer_token = None
        for cookie in cookies:
            if cookie['name'] == 'EPIC_BEARER_TOKEN':
                bearer_token = cookie['value']
                break

        if bearer_token:
            self.session.headers['Authorization'] = f'Bearer {bearer_token}'

        return True

    def random_delay(self, min_sec=1, max_sec=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def get_account_info(self):
        """Get current account information via GraphQL"""
        query = """
        query {
            Launcher {
                userInfo {
                    accountId
                    displayName
                    email
                }
            }
        }
        """

        try:
            response = self.session.post(
                self.endpoints['graphql'],
                json={'query': query},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                user_info = data.get('data', {}).get('Launcher', {}).get('userInfo', {})
                return user_info
            else:
                print(f"⚠️  Failed to get account info: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return None

    def get_free_games(self):
        """Get list of free games"""
        try:
            self.random_delay(0.5, 1.5)

            response = self.session.get(
                self.endpoints['free_games'],
                params={
                    'locale': 'zh-CN',
                    'country': 'CN',
                    'allowCountries': 'CN'
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Failed to fetch games: HTTP {response.status_code}")
                return []

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

                # Get correct URL slug - always prefer offerMappings/catalogNs
                url_slug = None

                # Priority 1: offerMappings
                offer_mappings = game.get('offerMappings', [])
                if offer_mappings:
                    url_slug = offer_mappings[0].get('pageSlug')

                # Priority 2: catalogNs.mappings
                if not url_slug:
                    mappings = game.get('catalogNs', {}).get('mappings', [])
                    if mappings:
                        url_slug = mappings[0].get('pageSlug')

                # Priority 3: urlSlug/productSlug (fallback)
                if not url_slug:
                    url_slug = game.get('urlSlug') or game.get('productSlug')

                free_games.append({
                    'id': game.get('id'),
                    'namespace': game.get('namespace'),
                    'title': game.get('title'),
                    'description': game.get('description', ''),
                    'offerType': game.get('offerType'),
                    'url_slug': url_slug,
                })

            return free_games

        except Exception as e:
            print(f"❌ Error fetching free games: {e}")
            return []

    def check_ownership(self, namespace, offer_id):
        """Check if user already owns the game via GraphQL"""
        # GraphQL query to check ownership
        query = """
        query getOwnedGames($namespace: String!, $offerId: String!) {
            Catalog {
                catalogOffer(namespace: $namespace, id: $offerId, locale: "zh-CN") {
                    id
                    namespace
                    title
                    ownedInformation {
                        owned
                        quantity
                    }
                }
            }
        }
        """

        try:
            self.random_delay(0.5, 1.0)

            response = self.session.post(
                self.endpoints['graphql'],
                json={
                    'query': query,
                    'variables': {
                        'namespace': namespace,
                        'offerId': offer_id
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                offer = data.get('data', {}).get('Catalog', {}).get('catalogOffer', {})
                owned_info = offer.get('ownedInformation', {})
                return owned_info.get('owned', False)

            return None  # Unknown

        except Exception as e:
            print(f"⚠️  Error checking ownership: {e}")
            return None

    def claim_game_graphql(self, namespace, offer_id):
        """
        Attempt to claim game using GraphQL mutation
        This is the most likely method based on analysis
        """
        # GraphQL mutation for claiming/purchasing free game
        mutation = """
        mutation claimFreeCatalogOffer($namespace: String!, $offerId: String!, $lineOffers: [LineOfferInput!]!) {
            Purchase {
                freeOrder(namespace: $namespace, offerId: $offerId, lineOffers: $lineOffers) {
                    orderId
                    orderState
                    message
                }
            }
        }
        """

        variables = {
            'namespace': namespace,
            'offerId': offer_id,
            'lineOffers': [{
                'offerId': offer_id,
                'quantity': 1
            }]
        }

        try:
            self.random_delay(1.5, 3.0)  # Longer delay before claim attempt

            response = self.session.post(
                self.endpoints['graphql'],
                json={
                    'query': mutation,
                    'variables': variables
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # Check for errors
                if 'errors' in data:
                    errors = data['errors']
                    error_msg = errors[0].get('message', 'Unknown error')
                    return {'success': False, 'error': error_msg, 'data': data}

                # Check purchase result
                purchase = data.get('data', {}).get('Purchase', {})
                order = purchase.get('freeOrder', {})

                if order:
                    return {
                        'success': True,
                        'order_id': order.get('orderId'),
                        'state': order.get('orderState'),
                        'message': order.get('message')
                    }

                return {'success': False, 'error': 'No order data', 'data': data}

            else:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'body': response.text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def claim_game_order_api(self, namespace, offer_id):
        """
        Alternative: Use order API (payment-website-pci)
        This is a backup method
        """
        try:
            # Step 1: Create order preview
            self.random_delay(1.0, 2.0)

            preview_payload = {
                'useDefault': True,
                'setDefault': False,
                'namespace': namespace,
                'country': 'CN',
                'countryName': 'China',
                'orderId': None,
                'orderComplete': False,
                'orderError': None,
                'orderPending': False,
                'offers': [offer_id],
                'includeAccountBalance': False
            }

            preview_response = self.session.post(
                self.endpoints['order_preview'],
                json=preview_payload,
                timeout=30
            )

            if preview_response.status_code != 200:
                return {'success': False, 'error': f'Preview failed: {preview_response.status_code}'}

            # Step 2: Confirm order
            self.random_delay(1.5, 2.5)

            confirm_payload = preview_payload.copy()
            confirm_payload['orderComplete'] = True

            confirm_response = self.session.post(
                self.endpoints['order_confirm'],
                json=confirm_payload,
                timeout=60
            )

            if confirm_response.status_code == 200:
                result = confirm_response.json()
                return {
                    'success': True,
                    'method': 'order_api',
                    'data': result
                }
            else:
                return {'success': False, 'error': f'Confirm failed: {confirm_response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def claim_game(self, game):
        """
        Main claim function - tries multiple methods
        """
        namespace = game['namespace']
        offer_id = game['id']
        title = game['title']

        print(f"\n🎮 Attempting to claim: {title}")
        print(f"   Namespace: {namespace}")
        print(f"   Offer ID: {offer_id}")

        # Check if already owned
        owned = self.check_ownership(namespace, offer_id)
        if owned is True:
            print(f"   ✅ Already owned")
            return {'success': True, 'status': 'already_owned'}
        elif owned is False:
            print(f"   🆕 Not owned, proceeding to claim...")
        else:
            print(f"   ❓ Ownership unknown, attempting claim anyway...")

        # Method 1: Try GraphQL mutation (most likely to work)
        print(f"   📡 Method 1: GraphQL Mutation...")
        result = self.claim_game_graphql(namespace, offer_id)

        if result.get('success'):
            print(f"   ✅ Claimed successfully via GraphQL!")
            print(f"      Order ID: {result.get('order_id')}")
            print(f"      State: {result.get('state')}")
            return result

        print(f"   ❌ GraphQL method failed: {result.get('error')}")

        # Method 2: Try Order API (backup)
        print(f"   📡 Method 2: Order API...")
        result = self.claim_game_order_api(namespace, offer_id)

        if result.get('success'):
            print(f"   ✅ Claimed successfully via Order API!")
            return result

        print(f"   ❌ Order API method failed: {result.get('error')}")

        # Both methods failed
        return {'success': False, 'error': 'All claim methods failed', 'details': result}


class AutoClaimer:
    """Main auto-claimer orchestrator"""

    def __init__(self):
        self.api = EpicGamesAPI()
        self.log_file = Path(__file__).parent / 'auto_claim.log'

    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

    def run(self):
        """Main execution flow"""
        self.log("=" * 70)
        self.log("Epic Games Auto Claimer - Full API Implementation")
        self.log("=" * 70)

        # Step 1: Load cookies
        self.log("\n📋 Step 1: Loading cookies...")
        try:
            self.api.load_cookies()
        except Exception as e:
            self.log(f"❌ Failed to load cookies: {e}")
            self.log("   Please run: python3 extract_cookies.py")
            return False

        # Step 2: Verify account
        self.log("\n📋 Step 2: Verifying account...")
        account = self.api.get_account_info()
        if account:
            self.log(f"✅ Logged in as: {account.get('displayName')} ({account.get('email')})")
        else:
            self.log("⚠️  Could not verify account (may still work)")

        # Step 3: Get free games
        self.log("\n📋 Step 3: Fetching free games...")
        games = self.api.get_free_games()

        if not games:
            self.log("❌ No free games found or API unavailable")
            return False

        self.log(f"✅ Found {len(games)} free game(s):")
        for game in games:
            self.log(f"   • {game['title']}")

        # Step 4: Claim each game
        self.log("\n📋 Step 4: Claiming games...")

        results = {
            'claimed': [],
            'already_owned': [],
            'failed': []
        }

        for i, game in enumerate(games, 1):
            self.log(f"\n[{i}/{len(games)}] Processing: {game['title']}")

            result = self.api.claim_game(game)

            if result.get('success'):
                if result.get('status') == 'already_owned':
                    results['already_owned'].append(game['title'])
                else:
                    results['claimed'].append(game['title'])
            else:
                results['failed'].append({
                    'title': game['title'],
                    'error': result.get('error')
                })

            # Anti-detection: random delay between games
            if i < len(games):
                delay = random.uniform(3, 6)
                self.log(f"   ⏱️  Waiting {delay:.1f}s before next game...")
                time.sleep(delay)

        # Step 5: Summary
        self.log("\n" + "=" * 70)
        self.log("Summary")
        self.log("=" * 70)
        self.log(f"✅ Claimed: {len(results['claimed'])}")
        for title in results['claimed']:
            self.log(f"   • {title}")

        if results['already_owned']:
            self.log(f"\n📦 Already owned: {len(results['already_owned'])}")
            for title in results['already_owned']:
                self.log(f"   • {title}")

        if results['failed']:
            self.log(f"\n❌ Failed: {len(results['failed'])}")
            for item in results['failed']:
                self.log(f"   • {item['title']}: {item['error']}")

        self.log("\n" + "=" * 70)

        # Return success if any games were claimed
        return len(results['claimed']) > 0 or len(results['already_owned']) > 0


def main():
    claimer = AutoClaimer()
    success = claimer.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
