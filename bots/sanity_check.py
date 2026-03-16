#!/usr/bin/env python3
"""
Apptivators Academy - Sanity Check
====================================
Verifies all bots are online and connected to Discord.
Run after start_bots.py to verify everything is working.
"""

import os
import sys
import discord
from dotenv import load_dotenv

# Bot directory
BOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Server ID
SERVER_ID = 1482341738956980266  # Apptivator's Coding Academy

# Bot tokens
BOTS = {
    "StrikeSource_Clawbot": {
        "env_file": ".env",
        "token_var": "DISCORD_BOT_TOKEN"
    },
    "S.A.M.P.I.RT": {
        "env_file": "S.A.M.P.I.RT/.env",
        "token_var": "DISCORD_BOT_TOKEN"
    },
    "SonicForge": {
        "env_file": "SonicForge/.env",
        "token_var": "SONIC_FORGE_TOKEN"
    },
    "SyncFlux": {
        "env_file": "SyncFlux/.env",
        "token_var": "SYNC_FLUX_TOKEN"
    }
}

def check_bot(name, config):
    """Check if a single bot is online."""
    env_path = os.path.join(BOT_DIR, config["env_file"])
    load_dotenv(env_path)
    token = os.getenv(config["token_var"])
    
    if not token:
        return None, "Token not found"
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    
    client = discord.Client(intents=intents)
    
    result = {"name": name, "status": "unknown", "guild": None, "error": None}
    
    @client.event
    async def on_ready():
        guild = client.get_guild(SERVER_ID)
        if guild:
            result["status"] = "online"
            result["guild"] = guild.name
        else:
            result["status"] = "not_in_server"
        await client.close()
    
    @client.event
    async def on_error(event, *args, **kwargs):
        result["error"] = "Connection error"
        await client.close()
    
    try:
        client.run(token, log_handler=None)
    except Exception as e:
        result["error"] = str(e)[:50]
        result["status"] = "error"
    
    return result

def main():
    print("="*60)
    print("  APPTIVATORS ACADEMY - SANITY CHECK")
    print("="*60)
    print()
    
    results = []
    
    for name, config in BOTS.items():
        print(f"  Checking: {name}...", end=" ", flush=True)
        result = check_bot(name, config)
        
        if result["status"] == "online":
            print(f"[OK] Online")
            results.append((name, "OK", result["guild"]))
        elif result["status"] == "not_in_server":
            print(f"[WARN] Not in server")
            results.append((name, "WARN", "Not in server"))
        else:
            print(f"[ERROR] {result.get('error', 'Unknown')}")
            results.append((name, "ERROR", result.get("error", "Unknown")))
    
    print()
    print("="*60)
    print("  SANITY CHECK RESULTS")
    print("="*60)
    print()
    
    online_count = sum(1 for r in results if r[1] == "OK")
    
    for name, status, details in results:
        status_icon = "[OK]" if status == "OK" else "[ERROR]" if status == "ERROR" else "[WARN]"
        print(f"  {status_icon} {name}: {details}")
    
    print()
    
    if online_count == len(BOTS):
        print(f"[SUCCESS] All {online_count}/{len(BOTS)} bots ONLINE")
        return 0
    else:
        print(f"[WARNING] Only {online_count}/{len(BOTS)} bots online")
        return 1

if __name__ == "__main__":
    sys.exit(main())