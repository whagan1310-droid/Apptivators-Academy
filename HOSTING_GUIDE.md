# 🤖 Bot Hosting Guide

## Current Status (Development)

Bots are running LOCALLY on your Windows PC via PowerShell. This is for **development/testing only**.

**To keep bots online permanently, you need a hosting solution.**

---

## Production Hosting Options

### Option 1: Cloud VPS (Recommended)
**Best for 24/7 bot hosting**

| Provider | Cost/Month | Specs | Notes |
|----------|-------------|-------|-------|
| **DigitalOcean** | $4-6 | 1GB RAM, 1 CPU | Good for 4 bots |
| **Linode/Akamai** | $5 | 1GB RAM, 1 CPU | Reliable |
| **Vultr** | $5 | 1GB RAM, 1 CPU | Easy setup |
| **Hetzner** | €3-5 | 2GB RAM, 1 CPU | Best value |

**Setup Steps:**
1. Create VPS (Ubuntu 22.04 recommended)
2. Install Python 3.10+
3. Install: `pip install discord.py python-dotenv aiohttp`
4. Upload bot files
5. Use `systemd` or `pm2` to keep bots running

---

### Option 2: Heroku (Free Tier Discontinued)
**No longer free** - $5-7/month minimum

---

### Option 3: Railway.app / Render.com
**Easier deployment**

| Platform | Cost | Notes |
|----------|------|-------|
| Railway | $5/month | Simple GitHub deploy |
| Render | Free tier | Limited hours/month |

---

### Option 4: Discord Bot Hosting Services
**Managed hosting**

| Service | Cost/Month | Notes |
|---------|------------|-------|
| Pterodactyl Panel | $2-10 | Self-hosted or rented |
| BotGhost | Free-$10 | Limited control |
| PebbleHost | $2-5 | Good for bots |

---

## Quick Start: systemd Service (Linux VPS)

Create a service for each bot:

```bash
# /etc/systemd/system/clawbot.service
[Unit]
Description=StrikeSource Clawbot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/bots
ExecStart=/usr/bin/python3 StrikeSource_Clawbot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable clawbot
sudo systemctl start clawbot
```

---

## Current Architecture

```
GitHub (Master Repo)
       ↓
   Your PC (Development)
       ↓ PowerShell
   Local Python Processes
       ↓ Discord Gateway
   Discord Server (Cloud)
       ↓
   Users see bots ONLINE
```

---

## Recommended Production Architecture

```
GitHub (Master Repo)
       ↓ Deploy
   Cloud VPS / Hosting Service
       ↓ systemd/screen
   24/7 Python Processes
       ↓ Discord Gateway
   Discord Server (Cloud)
       ↓
   Users see bots ONLINE 24/7
```

---

## Environment Variables Needed

Each bot requires `.env` file with:
```
DISCORD_BOT_TOKEN=your_token_here
GOOGLE_API_KEY=your_google_key (Clawbot only)
GITHUB_PAT=your_github_token (Clawbot only)
GUILD_ID=1482341738956980266
```

---

## Next Steps

1. **For Development:** Keep using PowerShell (current setup)
2. **For Production:** Choose a VPS provider and deploy
3. **Cost Estimate:** $4-6/month for all 4 bots

*Last Updated: 2026-03-15*