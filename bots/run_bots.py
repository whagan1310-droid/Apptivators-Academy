#!/usr/bin/env python3
"""
Apptivators Academy Bot Launcher
================================
Master script to start all bots or individual bots.
Usage:
    python run_bots.py                    # Start all bots
    python run_bots.py --clawbot          # Start StrikeSource_Clawbot only
    python run_bots.py --sampi            # Start S.A.M.P.I.RT only
    python run_bots.py --sonic            # Start SonicForge only
    python run_bots.py --sync             # Start SyncFlux only
"""

import subprocess
import sys
import os
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

BOT_DIR = Path(__file__).parent

BOTS = {
    "clawbot": {
        "name": "StrikeSource_Clawbot",
        "script": BOT_DIR / "StrikeSource_Clawbot.py",
        "env": BOT_DIR / ".env",
        "description": "Admin & Onboarding Bot"
    },
    "sampi": {
        "name": "S.A.M.P.I.RT",
        "script": BOT_DIR / "S.A.M.P.I.RT" / "sampi_rt_bot.py",
        "env": BOT_DIR / "S.A.M.P.I.RT" / ".env",
        "description": "Security & Threat Detection Bot"
    },
    "sonic": {
        "name": "SonicForge",
        "script": BOT_DIR / "SonicForge" / "sonic_forge_bot.py",
        "env": BOT_DIR / "SonicForge" / ".env",
        "description": "Audio & Music Bot"
    },
    "sync": {
        "name": "SyncFlux",
        "script": BOT_DIR / "SyncFlux" / "sync_flux_bot.py",
        "env": BOT_DIR / "SyncFlux" / ".env",
        "description": "Media Synchronization Bot"
    }
}

def check_env(bot_key):
    env_path = BOTS[bot_key]["env"]
    if not env_path.exists():
        print(f"[ERROR] Missing .env for {BOTS[bot_key]['name']}: {env_path}")
        print(f"  Create it with: DISCORD_BOT_TOKEN=your_token_here")
        return False
    
    load_dotenv(env_path)
    bot_token = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("SONIC_FORGE_TOKEN") or os.getenv("SYNC_FLUX_TOKEN")
    
    if not bot_token:
        print(f"[ERROR] No token found in {env_path}")
        return False
    
    return True

def run_bot(bot_key):
    if not check_env(bot_key):
        return False
    
    bot_info = BOTS[bot_key]
    print(f"\n[STARTING] {bot_info['name']} - {bot_info['description']}")
    print(f"  Script: {bot_info['script']}")
    
    try:
        os.chdir(bot_info['script'].parent)
        subprocess.run([sys.executable, str(bot_info['script'])], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {bot_info['name']} exited with error: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n[STOPPED] {bot_info['name']} - Interrupted by user")
        return True
    
    return True

def run_all_bots():
    print("=" * 60)
    print("APPTIVATORS ACADEMY - STARTING ALL BOTS")
    print("=" * 60)
    
    processes = []
    
    for bot_key, bot_info in BOTS.items():
        if not check_env(bot_key):
            print(f"[SKIPPING] {bot_info['name']} - Missing token")
            continue
        
        print(f"\n[LAUNCHING] {bot_info['name']} - {bot_info['description']}")
        
        try:
            os.chdir(bot_info['script'].parent)
            proc = subprocess.Popen(
                [sys.executable, str(bot_info['script'])],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append((bot_key, proc))
            print(f"  [PID {proc.pid}] {bot_info['name']} started")
        except Exception as e:
            print(f"[ERROR] Failed to start {bot_info['name']}: {e}")
    
    if not processes:
        print("\n[ERROR] No bots started. Check your .env files.")
        return False
    
    print("\n" + "=" * 60)
    print(f"ALL BOTS RUNNING - {len(processes)} active")
    print("Press Ctrl+C to stop all bots")
    print("=" * 60)
    
    try:
        for bot_key, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping all bots...")
        for bot_key, proc in processes:
            proc.terminate()
            print(f"  [STOPPED] {BOTS[bot_key]['name']}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Apptivators Academy Bot Launcher")
    parser.add_argument("--clawbot", action="store_true", help="Start StrikeSource_Clawbot only")
    parser.add_argument("--sampi", action="store_true", help="Start S.A.M.P.I.RT only")
    parser.add_argument("--sonic", action="store_true", help="Start SonicForge only")
    parser.add_argument("--sync", action="store_true", help="Start SyncFlux only")
    parser.add_argument("--all", action="store_true", help="Start all bots (default)")
    parser.add_argument("--list", action="store_true", help="List available bots")
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable Bots:")
        print("-" * 40)
        for key, info in BOTS.items():
            print(f"  --{key:10} {info['name']:20} {info['description']}")
        print()
        return
    
    if args.clawbot:
        run_bot("clawbot")
    elif args.sampi:
        run_bot("sampi")
    elif args.sonic:
        run_bot("sonic")
    elif args.sync:
        run_bot("sync")
    else:
        run_all_bots()

if __name__ == "__main__":
    main()