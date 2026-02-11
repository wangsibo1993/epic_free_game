#!/usr/bin/env python3
"""
Epic Games Free Game Claimer - API-based Version
Uses Epic Games' backend API instead of browser automation
More stable and less likely to be detected
"""
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class EpicGamesClaimer:
    def __init__(self):
        self.session = requests.Session()
        self.base_dir = Path(__file__).parent
        self.cookies_file = self.base_dir / 'claimer' / 'data' / 'cookies.json'

        # Epic Games API endpoints
        self.api_endpoints = {
            'free_games': 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
            'graphql': 'https://graphql.epicgames.com/graphql',
            'order': 'https://www.epicgames.com/store/purchase',
        }

        # Setup headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://store.epicgames.com',
            'Referer': 'https://store.epicgames.com/',
        })

    def load_cookies(self):
        """Load cookies from file (extracted from real browser)"""
        if not self.cookies_file.exists():
            print(f"❌ Cookie file not found: {self.cookies_file}")
            print("   Please run: python3 extract_cookies.py")
            return False

        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)

            # Convert cookie format and add to session
            for cookie in cookies:
                self.session.cookies.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain', '.epicgames.com'),
                    path=cookie.get('path', '/'),
                    secure=cookie.get('secure', True)
                )

            print(f"✅ Loaded {len(cookies)} cookies from file")

            # Check for critical authentication cookies
            critical_cookies = ['EPIC_SSO', 'EPIC_BEARER_TOKEN', 'eg-auth']
            found = [c['name'] for c in cookies if c['name'] in critical_cookies]

            if found:
                print(f"🔑 Found critical auth cookies: {', '.join(found)}")
                return True
            else:
                print("⚠️  Warning: No authentication cookies found!")
                return False

        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return False

    def get_free_games(self):
        """Fetch list of free games from Epic's backend API"""
        print("\n🔍 Fetching free games list...")

        try:
            response = self.session.get(
                self.api_endpoints['free_games'],
                params={
                    'locale': 'zh-CN',
                    'country': 'CN',
                    'allowCountries': 'CN'
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Parse the response to find free games
            free_games = []
            elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])

            for game in elements:
                # Check if game has active free promotion
                promotions = game.get('promotions')
                if not promotions:
                    continue

                promo_offers = promotions.get('promotionalOffers', [])
                if not promo_offers:
                    continue

                # Check if actually free (not just discounted)
                price_info = game.get('price', {})
                total_price = price_info.get('totalPrice', {})
                discount_price = total_price.get('discountPrice', -1)

                # Skip if not free (discountPrice must be 0)
                if discount_price != 0:
                    continue

                # Game is currently free
                title = game.get('title', 'Unknown')
                description = game.get('description', '')

                # Get correct URL slug - always prefer offerMappings/catalogNs
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

                # Get offer ID and namespace (needed for claiming)
                namespace = game.get('namespace')
                offer_id = game.get('id')

                free_games.append({
                    'title': title,
                    'description': description,
                    'url': game_url,
                    'namespace': namespace,
                    'id': offer_id,
                    'url_slug': url_slug
                })

            print(f"✅ Found {len(free_games)} free games")
            for game in free_games:
                print(f"   📦 {game['title']}")

            return free_games

        except Exception as e:
            print(f"❌ Failed to fetch free games: {e}")
            return []

    def check_ownership(self, namespace, offer_id):
        """Check if user already owns the game via GraphQL API"""
        # This would require reverse-engineering the GraphQL query
        # For now, we'll skip ownership check and attempt to claim all
        return False

    def claim_game_api(self, game):
        """
        Attempt to claim game using API
        NOTE: This is the challenging part - Epic doesn't provide a public API
        We would need to reverse-engineer the checkout process
        """
        print(f"\n🎮 Attempting to claim: {game['title']}")
        print(f"   URL: {game['url']}")

        # The claiming process typically involves:
        # 1. POST to checkout endpoint with namespace and offer ID
        # 2. Confirm order (for $0.00 items)
        # 3. Handle any captcha/verification

        # This is a placeholder - the actual implementation would require
        # analyzing network traffic during a manual claim to find the exact endpoints

        print("   ⚠️  API claiming not yet implemented")
        print("   💡 Recommendation: Use hybrid approach (browser for claiming, API for detection)")

        return False

    def run(self):
        """Main execution flow"""
        print("=" * 60)
        print("Epic Games Free Game Claimer - API Version")
        print("=" * 60)

        # Step 1: Load cookies
        if not self.load_cookies():
            return

        # Step 2: Get free games list
        free_games = self.get_free_games()

        if not free_games:
            print("\n❌ No free games found or API request failed")
            return

        # Step 3: Attempt to claim each game
        claimed = 0
        failed = 0

        for game in free_games:
            if self.claim_game_api(game):
                claimed += 1
            else:
                failed += 1

            # Rate limiting
            time.sleep(2)

        # Summary
        print("\n" + "=" * 60)
        print(f"Summary: {claimed} claimed, {failed} failed")
        print("=" * 60)

if __name__ == '__main__':
    claimer = EpicGamesClaimer()
    claimer.run()
