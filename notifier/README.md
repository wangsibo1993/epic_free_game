# Epic Games Free Game Notifier

API-based notification system for Epic Games free games.

## 📁 Directory Structure

```
epic_free_game/
├── claimer/              # Browser automation (original, paused)
│   └── epic-games.js     # Puppeteer-based auto-claimer
├── notifier/             # NEW: API-based notification system
│   ├── notify_free_games.py       # Main notification script
│   ├── epic_auto_claimer.py       # API auto-claim (experimental)
│   ├── epic_api_claimer.py        # API testing framework
│   ├── cookie_manager.py          # Cookie extraction & management
│   ├── run_notifier.sh            # Shell wrapper for cron
│   ├── install_notifier_cron.sh   # Cron job installer
│   ├── notified_games.json        # Tracking sent notifications
│   └── notifier.log               # Log file
├── .env                  # Email & proxy configuration
└── README.md

```

## 🚀 Quick Start

### 1. Configure Email (Required)

Edit `.env` in project root:
```bash
# Email Configuration
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASS=your_auth_code
TO_EMAIL=recipient@example.com
```

### 2. Install Cron Job (Runs daily at 11:00 AM)

```bash
cd notifier
bash install_notifier_cron.sh
```

### 3. Test Manually

```bash
cd notifier
python3 notify_free_games.py
```

## 📧 How It Works

1. **API Detection**: Fetches free games from Epic Games API (fast & reliable)
2. **Deduplication**: Only notifies about NEW games (tracks in `notified_games.json`)
3. **Email Notification**: Sends HTML email with game links
4. **Manual Claiming**: You claim games in real browser (100% reliable)

## 🔧 Components

### notify_free_games.py
- **Purpose**: Main notification script
- **Schedule**: Daily at 11:00 AM via cron
- **Output**: Email with new free games
- **Status**: ✅ Production Ready

### epic_auto_claimer.py
- **Purpose**: Experimental API-based auto-claiming
- **Status**: ⚠️ Not Working (Epic API changed/protected)
- **Note**: Keep for future research

### cookie_manager.py
- **Purpose**: Extract & decrypt browser cookies
- **Dependencies**: `browser-cookie3`
- **Commands**:
  - `python3 cookie_manager.py refresh` - Extract cookies from Chrome
  - `python3 cookie_manager.py check` - Validate cookies
  - `python3 cookie_manager.py info` - Show cookie details

## 📋 Cron Jobs

### Active Jobs
```bash
# Notifier (runs daily at 11:00 AM)
0 11 * * * /path/to/notifier/run_notifier.sh >> /path/to/notifier.log 2>&1
```

### Paused Jobs
```bash
# Browser automation (paused)
# [PAUSED] 0 11 * * * /path/to/run_auto.sh >> /path/to/claim.log 2>&1
```

To view all cron jobs:
```bash
crontab -l
```

To unpause browser automation:
```bash
crontab -e
# Remove the "# [PAUSED]" prefix
```

## 🐛 Troubleshooting

### No email received?
1. Check `.env` email configuration
2. Verify SMTP credentials (use QQ Mail auth code, not password)
3. Check logs: `tail -f notifier.log`

### Cookie extraction failed?
```bash
cd notifier
pip3 install browser-cookie3
python3 cookie_manager.py refresh
```

### API timeout?
- Epic Games API may be temporarily unavailable
- Cron will retry next day automatically
- Check logs: `tail -f notifier.log`

## 📝 Logs

- **Notifier logs**: `notifier/notifier.log`
- **Browser automation logs**: `claim.log` (paused)

View recent logs:
```bash
tail -f notifier/notifier.log
```

## 🎯 Recommendations

### Current Setup (Recommended)
- ✅ API detects free games (fast, reliable)
- ✅ Email notifies you immediately
- ✅ You manually claim in browser (100% success rate)

### Alternative (If you want full automation)
- Browser automation is paused but available
- Unpause by editing crontab
- Note: May be blocked by Cloudflare/anti-bot

## 📚 Documentation

- `API_AUTO_CLAIM_GUIDE.md` - Detailed API claiming guide
- `FINAL_IMPLEMENTATION.md` - Implementation summary
- `URL_FIX_NOTES.md` - URL slug resolution fixes

## 🔄 Updates

### 2026-02-11
- ✅ Fixed Cookie extraction (added browser-cookie3)
- ✅ Fixed URL 404 issues (prioritize offerMappings)
- ✅ Fixed price filtering (exclude discounted games)
- ✅ Created notifier directory structure
- ✅ Set up daily cron job at 11:00 AM
- ⏸️ Paused browser automation

---

**Need help?** Check the logs or run `python3 notify_free_games.py` manually to debug.
