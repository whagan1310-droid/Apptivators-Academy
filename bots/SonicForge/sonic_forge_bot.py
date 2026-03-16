import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!sonic_", intents=intents)

PLAYLIST_FILE = "playlist.json"

def load_playlist():
    if os.path.exists(PLAYLIST_FILE):
        import json
        with open(PLAYLIST_FILE, "r") as f:
            return json.load(f)
    return []

def save_playlist(playlist):
    import json
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(playlist, f, indent=2)

@bot.event
async def on_ready():
    print(f"SonicForge Online: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="the forge beats"))

@bot.command(name="forge")
async def forge(ctx, *, search: str):
    """Search and queue a track to the forge playlist."""
    playlist = load_playlist()
    
    track = {
        "id": len(playlist) + 1,
        "query": search,
        "user": ctx.author.name,
        "user_id": str(ctx.author.id),
        "channel": ctx.channel.name,
        "timestamp": str(ctx.message.created_at)
    }
    
    playlist.append(track)
    save_playlist(playlist)
    
    embed = discord.Embed(
        title="🎵 Track Queued for the Forge",
        description=f"**Query**: `{search}`",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    embed.add_field(name="👤 Added By", value=ctx.author.mention, inline=True)
    embed.add_field(name="📋 Queue Position", value=f"#{track['id']}", inline=True)
    embed.set_footer(text="SonicForge • Academy Audio Engine")
    
    await ctx.send(embed=embed)

@bot.command(name="playlist")
async def playlist(ctx, limit: int = 10):
    """View the current Academy queue."""
    playlist = load_playlist()
    
    if not playlist:
        await ctx.send("📭 The forge playlist is empty. Add a track with `!sonic_forge <search>`!")
        return
    
    playlist = playlist[-limit:]
    
    embed = discord.Embed(
        title="🎵 Academy Forge Playlist",
        description=f"Total tracks: **{len(load_playlist())}**",
        color=discord.Color.from_rgb(155, 89, 182)
    )
    
    for track in playlist:
        embed.add_field(
            name=f"#{track['id']} • {track['user']}",
            value=f"`{track['query']}`",
            inline=False
        )
    
    embed.set_footer(text="SonicForge • Academy Audio Engine")
    await ctx.send(embed=embed)

@bot.command(name="skip")
async def skip(ctx):
    """Skip the current track (placeholder for voice integration)."""
    await ctx.send("⏭️ **Skip**: Voice control coming soon! Currently in demo mode.")

@bot.command(name="pause")
async def pause(ctx):
    """Pause the current stream."""
    await ctx.send("⏸️ **Pause**: Audio control coming soon!")

@bot.command(name="queue_clear")
async def queue_clear(ctx):
    """Clear the entire playlist."""
    playlist = []
    save_playlist(playlist)
    await ctx.send("🗑️ **Playlist Cleared**: The forge is silent.")

@bot.command(name="now_playing")
async def now_playing(ctx):
    """Show what's currently playing."""
    await ctx.send("🎧 **Now Playing**: Demo mode - Use `!sonic_forge <search>` to add tracks!")

@bot.command(name="volume")
async def volume(ctx, level: int = 50):
    """Adjust volume (0-100)."""
    if level < 0 or level > 100:
        await ctx.send("❌ Volume must be between 0 and 100.")
        return
    await ctx.send(f"🔊 **Volume Set**: {level}%")

if __name__ == "__main__":
    token = os.getenv("SONIC_FORGE_TOKEN")
    if token:
        bot.run(token)
    else:
        print("SonicForge: No SONIC_FORGE_TOKEN found. Standing by.")
        import time
        while True: time.sleep(3600)
