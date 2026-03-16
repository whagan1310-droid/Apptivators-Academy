#!/usr/bin/env python3
"""
Apptivators Academy - Start All Bots (Windows)
===============================================
Double-click to run, or run from command line:
    python start_bots.py
    
This script starts all 4 bots and runs a sanity check.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Bot directory
BOT_DIR = Path(__file__).parent

BOTS = [
    {"name": "StrikeSource_Clawbot", "script": "StrikeSource_Clawbot.py", "dir": "."},
    {"name": "S.A.M.P.I.RT", "script": "sampi_rt_bot.py", "dir": "S.A.M.P.I.RT"},
    {"name": "SonicForge", "script": "sonic_forge_bot.py", "dir": "SonicForge"},
    {"name": "SyncFlux", "script": "sync_flux_bot.py", "dir": "SyncFlux"},
]

def stop_existing_bots():
    """Stop any existing python processes running bots."""
    print("[INFO] Stopping existing bot processes...")
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                          capture_output=True, timeout=10)
        else:
            subprocess.run(["pkill", "-f", "python"], capture_output=True, timeout=10)
        time.sleep(2)
    except Exception:
        pass

def start_bots():
    """Start all bots in background."""
    print("="*60)
    print("  APPTIVATORS ACADEMY - BOT LAUNCHER")
    print("="*60)
    print()
    
    processes = []
    
    for bot in BOTS:
        bot_path = BOT_DIR / bot["dir"]
        bot_file = bot_path / bot["script"]
        
        print(f"  Starting: {bot['name']}", end="")
        
        if not bot_file.exists():
            print(" [ERROR] File not found")
            continue
        
        try:
            proc = subprocess.Popen(
                [sys.executable, str(bot_file)],
                cwd=str(bot_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            processes.append((bot["name"], proc))
            print(f" [OK] PID: {proc.pid}")
        except Exception as e:
            print(f" [ERROR] {e}")
    
    print()
    print("="*60)
    print(f"  {len(processes)} BOTS STARTED")
    print("="*60)
    print()
    
    return processes

def run_sanity_check():
    """Run sanity check to verify bot connections."""
    print("[SANITY CHECK] Verifying bot connections...")
    print()
    
    sanity_script = BOT_DIR / "sanity_check.py"
    if sanity_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(sanity_script)],
                cwd=str(BOT_DIR),
                capture_output=True,
                timeout=30
            )
            print(result.stdout.decode())
            if result.returncode != 0:
                print("[WARNING] Some checks may have failed")
        except Exception as e:
            print(f"[ERROR] Sanity check failed: {e}")
    else:
        print("[WARNING] sanity_check.py not found, skipping...")
    
    print()

def main():
    print()
    stop_existing_bots()
    processes = start_bots()
    
    print("[INFO] Waiting 5 seconds for bots to connect...")
    time.sleep(5)
    print()
    
    run_sanity_check()
    
    print("="*60)
    print("  ALL TASKS COMPLETE")
    print("="*60)
    print()
    print("Bots are now ONLINE in Discord!")
    print("Close this window to stop bots (they will go offline)")
    print()
    input("Press Enter to exit (bots will remain running)...")

if __name__ == "__main__":
    main()