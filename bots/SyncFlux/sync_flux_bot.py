import discord
from discord.ext import commands
import os
import json
import re
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!sync_", intents=intents)

YOUTUBE_LINKS_FILE = "youtube_links.json"
COLAB_LINKS_FILE = "colab_links.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def is_youtube_url(url):
    return "youtube.com" in url or "youtu.be" in url

def is_colab_url(url):
    return "colab.research.google.com" in url

@bot.event
async def on_ready():
    print(f"SyncFlux Online: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Academy media pipeline"))

@bot.command(name="sync")
async def sync(ctx, url: str, *, description: str = None):
    """Synchronize a new video or Colab notebook."""
    await ctx.message.delete()
    
    if not url or not url.startswith("http"):
        await ctx.send("❌ Please provide a valid URL.", delete_after=5)
        return
    
    is_youtube = is_youtube_url(url)
    is_colab = is_colab_url(url)
    
    if not is_youtube and not is_colab:
        await ctx.send("❌ Only YouTube and Google Colab links are supported.", delete_after=8)
        return
    
    link_data = {
        "id": len(load_json(YOUTUBE_LINKS_FILE if is_youtube else COLAB_LINKS_FILE)) + 1,
        "url": url.strip(),
        "description": description or "No description provided",
        "user": ctx.author.name,
        "user_id": str(ctx.author.id),
        "channel": ctx.channel.name,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if is_youtube:
        links = load_json(YOUTUBE_LINKS_FILE)
        links.append(link_data)
        save_json(YOUTUBE_LINKS_FILE, links)
        color = discord.Color.red()
        title = "🎥 YouTube Link Synced"
    else:
        links = load_json(COLAB_LINKS_FILE)
        links.append(link_data)
        save_json(COLAB_LINKS_FILE, links)
        color = discord.Color.blue()
        title = "📓 Colab Notebook Synced"
    
    embed = discord.Embed(
        title=title,
        color=color,
        url=url.strip()
    )
    embed.add_field(name="🔗 URL", value=f"[Link]({url.strip()})", inline=False)
    embed.add_field(name="📝 Description", value=link_data["description"], inline=False)
    embed.add_field(name="👤 Synced By", value=ctx.author.mention, inline=True)
    embed.add_field(name="💬 Channel", value=f"#{ctx.channel.name}", inline=True)
    embed.set_footer(text="SyncFlux • Academy Media Integration")
    
    await ctx.send(embed=embed)

@bot.command(name="flux_status")
async def flux_status(ctx):
    """Check health of the media pipeline."""
    yt_links = load_json(YOUTUBE_LINKS_FILE)
    colab_links = load_json(COLAB_LINKS_FILE)
    
    embed = discord.Embed(
        title="🔄 SyncFlux Pipeline Status",
        color=discord.Color.green()
    )
    embed.add_field(name="🎥 YouTube Links", value=f"**{len(yt_links)}** synced", inline=True)
    embed.add_field(name="📓 Colab Notebooks", value=f"**{len(colab_links)}** synced", inline=True)
    embed.add_field(name="🟢 Status", value="**ONLINE**", inline=True)
    embed.set_footer(text="SyncFlux • Academy Media Integration")
    
    await ctx.send(embed=embed)

@bot.command(name="youtube")
async def youtube(ctx, limit: int = 10):
    """List synced YouTube videos."""
    links = load_json(YOUTUBE_LINKS_FILE)
    
    if not links:
        await ctx.send("📭 No YouTube links synced yet. Use `!sync_ <youtube_url>` to add one!")
        return
    
    links = links[-limit:]
    
    embed = discord.Embed(
        title="🎥 Synced YouTube Videos",
        color=discord.Color.red()
    )
    
    for link in links:
        embed.add_field(
            name=f"#{link['id']} • {link['user']}",
            value=f"[{link['url']}]({link['url']})\n{link['description'][:80]}",
            inline=False
        )
    
    embed.set_footer(text="SyncFlux • Academy Media Integration")
    await ctx.send(embed=embed)

@bot.command(name="colab")
async def colab(ctx, limit: int = 10):
    """List synced Colab notebooks."""
    links = load_json(COLAB_LINKS_FILE)
    
    if not links:
        await ctx.send("📭 No Colab notebooks synced yet. Use `!sync_ <colab_url>` to add one!")
        return
    
    links = links[-limit:]
    
    embed = discord.Embed(
        title="📓 Synced Colab Notebooks",
        color=discord.Color.blue()
    )
    
    for link in links:
        embed.add_field(
            name=f"#{link['id']} • {link['user']}",
            value=f"[{link['url']}]({link['url']})\n{link['description'][:80]}",
            inline=False
        )
    
    embed.set_footer(text="SyncFlux • Academy Media Integration")
    await ctx.send(embed=embed)

@bot.command(name="my_syncs")
async def my_syncs(ctx):
    """Show your synced media."""
    yt_links = load_json(YOUTUBE_LINKS_FILE)
    colab_links = load_json(COLAB_LINKS_FILE)
    
    user_yt = [l for l in yt_links if str(l["user_id"]) == str(ctx.author.id)]
    user_colab = [l for l in colab_links if str(l["user_id"]) == str(ctx.author.id)]
    
    if not user_yt and not user_colab:
        await ctx.send("📭 You haven't synced any media yet.")
        return
    
    embed = discord.Embed(
        title=f"🔗 Your Synced Media",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎥 YouTube", value=f"**{len(user_yt)}** videos", inline=True)
    embed.add_field(name="📓 Colab", value=f"**{len(user_colab)}** notebooks", inline=True)
    embed.set_footer(text="SyncFlux • Academy Media Integration")
    
    await ctx.send(embed=embed)

@bot.command(name="clear_media")
async def clear_media(ctx, media_type: str = "all"):
    """Clear synced media (youtube, colab, or all). Owner & Lvl 4-5 Mods only."""
    # Check if user is owner or level 4-5 moderator
    is_owner = ctx.author.id == 1477203354038833375
    is_mod_lvl_4_5 = any(
        "level 4" in r.name.lower() or "level 5" in r.name.lower() 
        for r in ctx.author.roles
    ) if ctx.author.roles else False
    
    if not is_owner and not is_mod_lvl_4_5:
        await ctx.send("❌ This command is for Owner and Level 4-5 Moderators only.")
        return
    
    if media_type == "youtube":
        save_json(YOUTUBE_LINKS_FILE, [])
        await ctx.send("🗑️ **YouTube links cleared**.")
    elif media_type == "colab":
        save_json(COLAB_LINKS_FILE, [])
        await ctx.send("🗑️ **Colab links cleared**.")
    elif media_type == "all":
        save_json(YOUTUBE_LINKS_FILE, [])
        save_json(COLAB_LINKS_FILE, [])
        await ctx.send("🗑️ **All media cleared**.")
    else:
        await ctx.send("❌ Usage: `!sync_clear <youtube|colab|all>`")

if __name__ == "__main__":
    token = os.getenv("SYNC_FLUX_TOKEN")
    if token:
        bot.run(token)
    else:
        print("SyncFlux: No SYNC_FLUX_TOKEN found. Standing by.")
        import time
        while True: time.sleep(3600)
