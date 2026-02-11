#!/usr/bin/env python3
"""
Mark Game as Owned Tool
Run this after manually claiming games to prevent future notifications
"""
import json
import sys
from pathlib import Path

def load_owned_games():
    """Load owned games list"""
    owned_file = Path(__file__).parent / 'owned_games.json'
    if owned_file.exists():
        with open(owned_file, 'r') as f:
            return json.load(f)
    return []

def save_owned_games(owned_list):
    """Save owned games list"""
    owned_file = Path(__file__).parent / 'owned_games.json'
    with open(owned_file, 'w') as f:
        json.dump(owned_list, f, indent=2)

def get_current_free_games():
    """Get current free games from API"""
    import requests
    try:
        response = requests.get(
            'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
            params={'locale': 'zh-CN', 'country': 'CN'},
            timeout=30
        )
        data = response.json()
        elements = data['data']['Catalog']['searchStore']['elements']

        free_games = []
        for game in elements:
            promotions = game.get('promotions')
            if not promotions:
                continue

            promo_offers = promotions.get('promotionalOffers', [])
            if not promo_offers or not promo_offers[0].get('promotionalOffers'):
                continue

            # Check if actually free
            price_info = game.get('price', {})
            total_price = price_info.get('totalPrice', {})
            discount_price = total_price.get('discountPrice', -1)

            if discount_price != 0:
                continue

            free_games.append({
                'id': game.get('id'),
                'title': game.get('title'),
            })

        return free_games
    except Exception as e:
        print(f"Error fetching games: {e}")
        return []

def main():
    print("=" * 60)
    print("Mark Game as Owned")
    print("=" * 60)

    # Get current free games
    print("\nFetching current free games...")
    free_games = get_current_free_games()

    if not free_games:
        print("No free games found.")
        return

    print(f"\nCurrent free games:")
    for i, game in enumerate(free_games, 1):
        print(f"  {i}. {game['title']} (ID: {game['id']})")

    # Load already owned
    owned = load_owned_games()
    if owned:
        print(f"\nAlready marked as owned: {len(owned)} games")

    print("\n" + "=" * 60)
    print("Options:")
    print("  1-N: Mark specific game as owned")
    print("  all: Mark all current free games as owned")
    print("  list: Show owned game IDs")
    print("  clear: Clear all owned marks")
    print("  q: Quit")
    print("=" * 60)

    while True:
        choice = input("\nYour choice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == 'list':
            print(f"\nOwned game IDs: {owned}")
        elif choice == 'clear':
            owned = []
            save_owned_games(owned)
            print("✅ Cleared all owned marks")
        elif choice == 'all':
            for game in free_games:
                if game['id'] not in owned:
                    owned.append(game['id'])
            save_owned_games(owned)
            print(f"✅ Marked {len(free_games)} games as owned")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(free_games):
                game = free_games[idx]
                if game['id'] not in owned:
                    owned.append(game['id'])
                    save_owned_games(owned)
                    print(f"✅ Marked '{game['title']}' as owned")
                else:
                    print(f"⚠️  '{game['title']}' is already marked as owned")
            else:
                print("Invalid game number")
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()
