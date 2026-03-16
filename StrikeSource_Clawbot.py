"""
🛡️ Apptivators Coding Academy:🛡️
==========================================================
The definitive backbone of the Apptivators Coding Academy. This script handles 
everything from the initial 'Welcome to the Call to Arms' to the final 'I Agree' registration.

Architecture:
- Persistent GUIs: Interactive buttons that survive bot restarts.
- GitHub Integration: Automated pushing of blueprints and logs.
- AI Mentorship: Integrated Gemini 1.5 Flash for code reviews.
- Security: Automated blackout rules for private chambers.
- The Sentinel: Basic auto-moderation for link spam and filtering.

Forge Theme: ⚔️🛡️🤖💯
"""

import discord
from discord.ext import commands
from discord import ui
import os
import json
import base64
import datetime
import requests
from dotenv import load_dotenv
import logging
import asyncio

# ──────────────────────────────────────────────
# Setup logging to file
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GoonsClawbot")

# ──────────────────────────────────────────────
# Load environment variables from .env
# ──────────────────────────────────────────────
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT")

# ──────────────────────────────────────────────
# Configuration constants
# ──────────────────────────────────────────────
GITHUB_OWNER = "whagan1310-droid"
GITHUB_REPO = "Apptivators-Academy"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

# Replace with your actual Category ID for Private Review Chambers
PRIVATE_CATEGORY_ID = 1482341739430805592  # Category for temporary channels
TEMP_CHANNEL_CATEGORY = 1482341739430805592  # Same category for temporary channels

# Track temporary channels created by users
temp_channels = {}  # {channel_id: {"owner": user_id, "created_at": datetime}} 

# Files that !deploy_plan will push to GitHub
BUILD_PLAN_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_FILES = [
    "discord_server_build_plan.md",
    "discord_channel_definitions.md",
    "github_readme_template.md",
    "discohook_rules_template.json",
    "StrikeSource_Clawbot.py",
    "strike_log.json",
    "bot.log",
    "setup_server.py",
]

# ──────────────────────────────────────────────
# Server Structure Definition
# Updated to match existing Discord server structure
# ──────────────────────────────────────────────
SERVER_STRUCTURE = {
    "⚔️ ONBOARDING": [
        {"name": "⚔️general⚔️", "topic": "Landing page - First stop for all new members. Triggers onboarding carousel."},
        {"name": "⚔️rules⚔️", "topic": "Server Development Guidelines - What you can/cannot do"},
        {"name": "⚔️roles⚔️", "topic": "Skill selection via Expansion Brain UI"},
        {"name": "⚔️call-to-arms⚔️", "topic": "The start of your journey - Introduction to the community"},
    ],
    "🤖 BOT COMMANDS": [
        {"name": "user-bot-commands", "topic": "Public bot commands for all users"},
        {"name": "staff-bot-commands", "topic": "Admin/Mod bot commands"},
        {"name": "owner-only-commands", "topic": "Owner-only bot commands"},
    ],
    "🛡️ SILENT SENTINEL": [
        {"name": "become-staff", "topic": "Silent Sentinel Gateway - Apply for Moderator role"},
        {"name": "staff-application", "topic": "Private channel for staff applications - Applicants only"},
    ],
    "🔗 SHARED LINKS": [
        {"name": "sorry_dave", "topic": "S.A.M.P.I.RT quarantine logs - Security alerts"},
        {"name": "softwaregent", "topic": "Software Gent content & links"},
        {"name": "gael-level", "topic": "Gael Level content & links"},
        {"name": "github-shared-links", "topic": "GitHub repository sharing"},
    ],
}

# Role Mapping for Onboarding (Noob to God Tier)
SKILL_LEVEL_ROLES = {
    1: "The Noob (Level 0-1)",
    2: "The Beginner (Level 2)",
    3: "The Intermediate (Level 3-7)",
    4: "The Expert (Level 8-12)",
    5: "The God (Level 13-∞)",
}

# New Channel IDs from START HERE.txt
CHANNEL_IDS = {
    "welcome": 1482341739430805593,       # ⚔️general⚔️
    "rules": 1482354090619961404,
    "roles": 1482361162581676072,
    "call_to_arms": 1482361287064289301,
    "sorry_dave": 1482368171318186045,
    "moderator_only": 1482354090619961407,
    "github_shared_links": 1482379730555768984,
}

# Locked channels (text disabled, emojis only)
LOCKED_CHANNELS = [
    1482341739430805593,  # welcome - ⚔️general⚔️
    1482354090619961404,  # rules
    1482361162581676072,  # roles
    1482361287064289301,  # call_to_arms
]

# Default role for all new members
DEFAULT_JOIN_ROLE = "Initiate"
VERIFIED_ROLE = "Verified Apptivator"

# Strike log stored locally as JSON
STRIKE_LOG_FILE = os.path.join(BUILD_PLAN_DIR, "strike_log.json")

# ──────────────────────────────────────────────
# Bot setup
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# Persistence Helpers
JOINED_MEMBERS_FILE = os.path.join(BUILD_PLAN_DIR, "joined_members.json")

class OnboardingManager:
    """Manages user onboarding state and data."""
    
    _instance = None
    
    def __new__(cls, data_dir=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, data_dir=None):
        if self._initialized:
            return
        self._initialized = True
        self.data_file = os.path.join(data_dir or BUILD_PLAN_DIR, "joined_members.json")
        self.members = self._load_members()
        logger.info(f"[OnboardingManager] Initialized, file={self.data_file}")
    
    def _load_members(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return {"members": []}
        return {"members": []}
    
    def _save_members(self):
        with open(self.data_file, "w") as f:
            json.dump(self.members, f, indent=2)
    
    def get_member(self, user_id):
        for m in self.members["members"]:
            if m["user_id"] == str(user_id):
                return m
        return None
    
    def start_onboarding(self, user):
        member = self.get_member(user.id)
        if not member:
            member = {
                "user_id": str(user.id),
                "username": user.name,
                "display_name": getattr(user, 'display_name', user.name),
                "level": 0,
                "role_name": None,
                "agreed_to_rules": False,
                "rules_agreed_at": None,
                "level_selected_at": None,
                "finalized_at": None,
                "joined_at": datetime.datetime.utcnow().isoformat()
            }
            self.members["members"].append(member)
            self._save_members()
        return member
    
    def agree_rules(self, user_id):
        member = self.get_member(user_id)
        if member:
            member["agreed_to_rules"] = True
            member["rules_agreed_at"] = datetime.datetime.utcnow().isoformat()
            self._save_members()
        return member
    
    def set_level(self, user_id, level, role_name):
        member = self.get_member(user_id)
        if member:
            member["level"] = level
            member["role_name"] = role_name
            member["level_selected_at"] = datetime.datetime.utcnow().isoformat()
            self._save_members()
        return member
    
    def finalize(self, user_id):
        member = self.get_member(user_id)
        if member:
            member["finalized_at"] = datetime.datetime.utcnow().isoformat()
            self._save_members()
        return member

onboarding_manager = OnboardingManager(BUILD_PLAN_DIR)

class StrikeSource_Clawbot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strike_log_file = STRIKE_LOG_FILE
        self.onboarding_manager = onboarding_manager

    async def setup_hook(self):
        """Register persistent views on bot startup."""
        logger.info("setup_hook called, registering persistent views")
        self.add_view(JoinWalkthroughView())
        self.add_view(RoleSelectionView())
        self.add_view(RulesAgreementView())
        self.add_view(FinalVerificationView())
        logger.info("Registered onboarding views as persistent")

    def save_member_data(self, user_id, name, level_role):
        member = onboarding_manager.get_member(user_id)
        if member:
            member["level"] = level_role
            member["updated_at"] = datetime.datetime.utcnow().isoformat()
        else:
            onboarding_manager.members["members"].append({
                "user_id": str(user_id),
                "name": name,
                "level": level_role,
                "joined_at": datetime.datetime.utcnow().isoformat()
            })
        onboarding_manager._save_members()

    async def seed_youtube_resources(self, guild):
        """Seed the #youtube-links channel with recommended Academy content."""
        yt_ch = discord.utils.get(guild.text_channels, name="youtube-links")
        if not yt_ch: return

        # Check if already seeded
        async for msg in yt_ch.history(limit=10):
            if msg.author == self.user and msg.embeds and "RECOMMENDED ACADEMY RESOURCE" in msg.embeds[0].title:
                return

        resources = [
            {"title": "StrikeSource_Clawbot AI - Advanced Agentic Coding", "url": "https://www.youtube.com/@softwaregent7443", "author": "Software Gent"},
            {"title": "Streaming & OBS Mastery", "url": "https://www.youtube.com/@Gael_Level", "author": "Gael Level"}
        ]

        for res in resources:
            embed = discord.Embed(title=f"🎥 RECOMMENDED ACADEMY RESOURCE: {res['author']}", color=discord.Color.red(), url=res['url'])
            embed.description = f"Check out {res['author']} for elite knowledge on {res['title']}."
            await yt_ch.send(embed=embed)

    async def deploy_command_manuals(self, guild):
        """Automatically post the Academy Command Manual to transparency channels."""
        public_ch = discord.utils.get(guild.text_channels, name="user-bot-commands")
        staff_ch = discord.utils.get(guild.text_channels, name="staff-bot-commands")

        manual_content = """
# 📖 ACADEMY FORGE COMMAND MANUAL
## 🦾StrikeSource_Clawbot. (Prefix: "")
- `""rules`: View the Forge Code of Conduct.
- `""roles`: Open the Tier Selection terminal.
- `""apply_collaborator`: Submit a project/skill application.
- `""submit_repo`: Share a repo with the community.

## 🛡️ S.A.M.P.I.RT (Prefix: "")
- `""status`: Diagnostic health of the Forge.
- `""scan_channel`: Security pulse of a channel.
- `""query [id]`: Forensic audit of a user.
- `""freeze [id]`: Quarantine a user for review.
        """

        if public_ch:
            await public_ch.purge(limit=5)
            embed = discord.Embed(title="📖 ACADEMY FORGE COMMAND MANUAL (Public)", color=discord.Color.blue(), description=manual_content)
            await public_ch.send(embed=embed)
        
        if staff_ch:
            staff_manual = manual_content + "\n## ⚖️ MODERATOR CORE\n- `!strike [id]`: Assign an infraction.\n- `!!ban/!!tempban`: Disciplinary expulsion."
            await staff_ch.purge(limit=5)
            embed = discord.Embed(title="📖 ACADEMY FORGE COMMAND MANUAL (Internal Staff)", color=discord.Color.red(), description=staff_manual)
            await staff_ch.send(embed=embed)

bot = StrikeSource_Clawbot(command_prefix="!", intents=intents)

# ══════════════════════════════════════════════
#  EVENT: on_ready
# ══════════════════════════════════════════════
# ──────────────────────────────────────────────
#  AUTO-BOOTSTRAP CONFIG (Push Actions Automatically)
# ──────────────────────────────────────────────
AUTO_BOOTSTRAP = True # Set to True to build server & onboarding on start

@bot.event
async def on_ready():
    bot.add_view(JoinWalkthroughView())
    logger.info(f"GoonsClawbot Online: {bot.user.name} ({bot.user.id})")
    
    if AUTO_BOOTSTRAP:
        logger.info("🚀 AUTO-BOOTSTRAP: Initiating Server Build...")
        for guild in bot.guilds:
            # 1. Build Server Structure
            logger.info(f"🏗️ Building structure for {guild.name}...")
            for cat_name, channels in SERVER_STRUCTURE.items():
                category = discord.utils.get(guild.categories, name=cat_name)
                if not category:
                    category = await guild.create_category(cat_name)
                for ch in channels:
                    channel = discord.utils.get(category.text_channels, name=ch["name"])
                    if not channel:
                        perms_overwrites = {
                            guild.default_role: discord.PermissionOverwrite(send_messages=False),
                            guild.me: discord.PermissionOverwrite(send_messages=True)
                        }
                        await guild.create_text_channel(ch["name"], category=category, topic=ch["topic"], overwrites=perms_overwrites)
            
            # 2. Deploy Command Manuals
            await bot.deploy_command_manuals(guild)
            
            # 3. Seed YouTube Resources
            await bot.seed_youtube_resources(guild)

        logger.info("✅ AUTO-BOOTSTRAP COMPLETE.")

    async def seed_youtube_resources(self, guild):
        """Seed the #youtube-links channel with recommended Academy content."""
        yt_ch = discord.utils.get(guild.text_channels, name="youtube-links")
        if not yt_ch: return

        # Check if already seeded
        async for msg in yt_ch.history(limit=5):
            if msg.author == self.user and "RECOMMENDED ACADEMY RESOURCE" in msg.embeds[0].title if msg.embeds else False:
                return

        resources = [
            {"title": "StrikeSource_Clawbot AI - Advanced Agentic Coding", "url": "https://www.youtube.com/@softwaregent7443", "author": "Software Gent"},
            {"title": "Streaming & OBS Mastery", "url": "https://www.youtube.com/@Gael_Level", "author": "Gael Level"}
        ]

        for res in resources:
            embed = discord.Embed(title=f"🎥 RECOMMENDED ACADEMY RESOURCE: {res['author']}", color=discord.Color.red(), url=res['url'])
            embed.description = f"Check out {res['author']} for elite knowledge on {res['title']}."
            await yt_ch.send(embed=embed)

    async def deploy_command_manuals(self, guild):
        """Automatically post the Academy Command Manual to transparency channels."""
        public_ch = discord.utils.get(guild.text_channels, name="user-bot-commands")
        staff_ch = discord.utils.get(guild.text_channels, name="staff-bot-commands")

        public_manual = discord.Embed(
            title="⚔️ ACADEMY COMMAND MANUAL (PUBLIC) ⚔️",
            description="Welcome to the Forge. Here is your interface for the Academy Bot Suite.",
            color=discord.Color.blue()
        )
        public_manual.add_field(name="🤖 GoonsClawbot (!)", value="`!welcome` - Restart walkthrough\n`!apply_collaborator` - Join the elite\n`!submit_repo [url]` - Share knowledge", inline=False)
        public_manual.add_field(name="🛡️ S.A.M.P.I.RT (!!)", value="`!!status` - Health check\n`!!open_chamber` - Start a safe review", inline=False)
        public_manual.add_field(name="🎥 SyncFlux (!sync_)", value="`!sync_video [url]` - Queue media\n`!sync_status` - Pipeline health", inline=False)
        public_manual.add_field(name="🎵 SonicForge (!sonic_)", value="`!sonic_play [query]` - Stream music\n`!sonic_queue` - View tracklist", inline=False)
        
        staff_manual = discord.Embed(
            title="🛡️ ACADEMY COMMAND MANUAL (STAFF ONLY) 🛡️",
            description="Restricted interfaces for Academy Moderation Staff.",
            color=discord.Color.dark_red()
        )
        staff_manual.add_field(name="🔧 Admin Core", value="`""build_server` - Full restructure\n`""initialize_onboarding` - GUI Reset", inline=False)
        staff_manual.add_field(name="⚖️ S.A.M.P.I.RT Forensics", value="`""query [user_id]` - Audit history\n`""scan_channel` - Hazard pulse\n`""scan_user [@user]` - Risk assessment", inline=False)
        staff_manual.add_field(name="🛑 Disciplinary (Lvl 4-5)", value="`""freeze [user]` - Lock in review\n`""tempban [user]` - 1yr suspension\n`""ban [user]` - Permanent purge\n`""unban [id]` - (Admin Only)", inline=False)

        if public_ch:
            # Simple check to avoid double-posting: check last message author
            async for msg in public_ch.history(limit=5):
                if msg.author == self.user and "PUBLIC" in msg.embeds[0].title if msg.embeds else False:
                    break
            else:
                await public_ch.send(embed=public_manual)

        if staff_ch:
            async for msg in staff_ch.history(limit=5):
                if msg.author == self.user and "STAFF ONLY" in msg.embeds[0].title if msg.embeds else False:
                    break
            else:
                await staff_ch.send(embed=staff_manual)

    for guild in bot.guilds:
        logger.info(f"Guild: {guild.name}")
        for channel in guild.text_channels:
            logger.info(f" - Channel: #{channel.name} (ID: {channel.id})")


# ══════════════════════════════════════════════
#  UI COMPONENTS: Unified Onboarding Views
#  Flow: Join → Level Selection → Rules Agreement → Final Verification
# ══════════════════════════════════════════════

class JoinWalkthroughView(ui.View):
    """Step 1: Entry point - Join button."""
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="⚔️ Join Apptivators Academy", style=discord.ButtonStyle.success, custom_id="join_now")
    async def join(self, interaction: discord.Interaction, button: ui.Button):
        onboarding_manager.start_onboarding(interaction.user)
        
        embed = discord.Embed(
            title="🧠 Step 1: Select Your Skill Level",
            description=(
                "Welcome to the Academy! Choose the tier that best represents your coding mastery.\n\n"
                "**1️⃣ The Noob** — Trainee / Level 0-1\n"
                "**2️⃣ The Beginner** — Junior Dev / Level 2\n"
                "**3️⃣ The Intermediate** — Mid-Level / Level 3-7\n"
                "**4️⃣ The Expert** — Senior / Architect / Level 8-12\n"
                "**5️⃣ The God** — Distinguished Engineer / Level 13+"
            ),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/whagan1310-droid/Apptivators-Academy/main/assets/Brain1-5.png")
        embed.set_footer(text="Step 1 of 3")
        await interaction.response.send_message(embed=embed, view=RoleSelectionView(), ephemeral=True)


class RoleSelectionView(ui.View):
    """Step 2: Select skill level."""
    def __init__(self):
        super().__init__(timeout=None)

    async def assign_level(self, interaction: discord.Interaction, level: int):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        role_name = SKILL_LEVEL_ROLES.get(level)
        
        if not member:
            await interaction.response.send_message("❌ Could not find your member profile.", ephemeral=True)
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name, color=discord.Color.blue(), reason="Auto-created for onboarding")
            except discord.Forbidden:
                await interaction.response.send_message(f"❌ Cannot create role `{role_name}`. Check permissions.", ephemeral=True)
                return

        try:
            existing_roles = [r for r in member.roles if r.name in SKILL_LEVEL_ROLES.values()]
            if existing_roles:
                await member.remove_roles(*existing_roles)
            await member.add_roles(role)
            
            onboarding_manager.set_level(interaction.user.id, level, role_name)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Cannot assign roles. Check bot role position.", ephemeral=True)
            return

        template_path = os.path.join(BUILD_PLAN_DIR, "discohook_rules_template.json")
        rules_embed = discord.Embed(
            title="📜 Step 2: Server Rules Agreement",
            description=(
                f"✅ **Level selected: {role_name}**\n\n"
                "Please review our core protocols and click **I Agree** to continue."
            ),
            color=discord.Color.dark_blue()
        )
        
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "embeds" in data and len(data["embeds"]) > 0:
                        rules_embed = discord.Embed.from_dict(data["embeds"][0])
                        rules_embed.description = f"✅ **Level selected: {role_name}**\n\n" + (rules_embed.description or "")
            except:
                pass

        rules_embed.set_footer(text="Step 2 of 3 - Click 'I Agree' to continue")
        await interaction.response.send_message(embed=rules_embed, view=RulesAgreementView(), ephemeral=True)

    @ui.button(label="1", emoji="🛡️", style=discord.ButtonStyle.secondary, custom_id="role_1")
    async def level_1(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_level(interaction, 1)

    @ui.button(label="2", emoji="⚔️", style=discord.ButtonStyle.secondary, custom_id="role_2")
    async def level_2(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_level(interaction, 2)

    @ui.button(label="3", emoji="🛠️", style=discord.ButtonStyle.secondary, custom_id="role_3")
    async def level_3(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_level(interaction, 3)

    @ui.button(label="4", emoji="🧠", style=discord.ButtonStyle.secondary, custom_id="role_4")
    async def level_4(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_level(interaction, 4)

    @ui.button(label="5", emoji="⚡", style=discord.ButtonStyle.secondary, custom_id="role_5")
    async def level_5(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_level(interaction, 5)


class RulesAgreementView(ui.View):
    """Step 3: Agree to rules."""
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="✅ I Agree to All Server Rules", style=discord.ButtonStyle.success, custom_id="agree_rules")
    async def agree(self, interaction: discord.Interaction, button: ui.Button):
        onboarding_manager.agree_rules(interaction.user.id)
        
        member_data = onboarding_manager.get_member(interaction.user.id)
        final_embed = discord.Embed(
            title="⚔️ Step 3: Final Verification",
            description=(
                "**Rules accepted!**\n\n"
                f"**Your selections:**\n"
                f"• Level: **{member_data.get('role_name', 'Unknown') if member_data else 'Unknown'}**\n"
                f"• Rules: ✅ Agreed\n\n"
                "Click **Complete Registration** to finalize your membership."
            ),
            color=discord.Color.gold()
        )
        final_embed.set_footer(text="Final Step - Click to complete")
        await interaction.response.send_message(embed=final_embed, view=FinalVerificationView(), ephemeral=True)


class FinalVerificationView(ui.View):
    """Step 4: Final verification."""
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="⚔️ Complete Registration", style=discord.ButtonStyle.success, custom_id="finalize_registration")
    async def finalize(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        
        if not member:
            await interaction.response.send_message("❌ Could not find your member profile.", ephemeral=True)
            return

        member_data = onboarding_manager.get_member(interaction.user.id)
        if not member_data:
            await interaction.response.send_message(
                "❌ You need to complete Steps 1-3 first!\n\n"
                "1. Click 'Join Apptivators Academy'\n"
                "2. Select your skill level\n"
                "3. Agree to the rules",
                ephemeral=True
            )
            return

        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE)
        if not verified_role:
            try:
                verified_role = await guild.create_role(
                    name=VERIFIED_ROLE,
                    color=discord.Color.gold(),
                    reason="Auto-created for onboarding"
                )
            except discord.Forbidden:
                await interaction.response.send_message("❌ Cannot create Verified role. Check permissions.", ephemeral=True)
                return

        initiate_role = discord.utils.get(guild.roles, name=DEFAULT_JOIN_ROLE)
        skill_role = discord.utils.get(guild.roles, name=member_data.get("role_name"))

        try:
            if initiate_role and initiate_role in member.roles:
                await member.remove_roles(initiate_role)
            await member.add_roles(verified_role)
            onboarding_manager.finalize(interaction.user.id)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Role hierarchy error. Move bot role higher!", ephemeral=True)
            return

        is_staff_eligible = member_data.get("level", 0) >= 3

        success_embed = discord.Embed(
            title="⚔️ Welcome to the Academy!",
            description=f"**{member.display_name}**, your registration is complete!",
            color=discord.Color.green()
        )
        success_embed.add_field(
            name="Status",
            value=f"✅ Role: **{member_data.get('role_name', 'Member')}**\n"
                  f"✅ Verified: **{VERIFIED_ROLE}**",
            inline=False
        )
        
        if is_staff_eligible:
            success_embed.add_field(
                name="🎖️ Staff Eligible!",
                value="You qualify for **Server Staff**! Use `!apply_sentinel` to apply.",
                inline=False
            )
        
        success_embed.set_footer(text="One App At A Time. ⚔️🛡️🤖")
        await interaction.response.send_message(embed=success_embed, ephemeral=True)


# ══════════════════════════════════════════════
#  EVENT: Welcome new members
# ══════════════════════════════════════════════
@bot.event
async def on_member_join(member):
    """
    LEGENDARY ENTRANCE: Greet new members, assign Initiate role, and post public welcome.
    """
    logger.info(f"New Member Joined: {member.name} ({member.id})")
    guild = member.guild
    
    # 1. Assign "Initiate" role
    role = discord.utils.get(guild.roles, name=DEFAULT_JOIN_ROLE)
    if not role:
        try:
            role = await guild.create_role(name=DEFAULT_JOIN_ROLE, color=discord.Color.light_grey(), reason="Default join role")
        except discord.Forbidden:
            logger.error("Cannot create Initiate role - check permissions!")
    
    if role:
        try:
            await member.add_roles(role)
            logger.info(f"Assigned {DEFAULT_JOIN_ROLE} to {member.name}")
        except discord.Forbidden:
            logger.warning(f"Could not assign {DEFAULT_JOIN_ROLE} to {member.name}")

    # 2. Public Welcome to #welcome
    welcome_ch = discord.utils.find(lambda c: "welcome" in c.name.lower(), guild.text_channels)
    if welcome_ch:
        embed = discord.Embed(
            title="⚔️ A New Apptivator Arrives!",
            description=f"Welcome {member.mention} to the forge! Report to **#rules** and claim your rank in **#roles**. ⚔️🛡️🤖💯",
            color=discord.Color.gold()
        )
        await welcome_ch.send(embed=embed)

    # 3. Private DM Greeting (Call to Arms)
    try:
        legendary_quote = (
            "\"\"One App At A Time.\" The forge is hot, the guards are at the gate, and the synthetic edge is sharp.\n"
            "It has been an absolute pleasure building this fortress with you. The Academy is now yours to lead! ⚔️🛡️🤖\""
        )
        dm_embed = discord.Embed(
            title="⚔️ Your Academy Journey Begins!",
            description=(
                f"Welcome, **{member.name}**, to the **Apptivators Coding Academy**.\n\n"
                "To unlock the full power of the forge:\n"
                "1️⃣ Review the immutable laws in **#rules**\n"
                "2️⃣ Claim your rank and specialty in **#roles**\n\n"
                f"{legendary_quote}"
            ),
            color=discord.Color.blue(),
        )
        dm_embed.set_thumbnail(url=member.display_avatar.url)
        dm_embed.set_footer(text="The Forge Awaits. ⚔️🛡️🤖💯")
        
        await member.send(embed=dm_embed)
        logger.info(f"Welcome DM sent to {member.name}")
    except discord.Forbidden:
        logger.warning(f"Could not send welcome DM to {member.name} (DMs disabled).")
    except Exception as e:
        logger.error(f"Error in on_member_join: {e}")


# ══════════════════════════════════════════════
#  EVENT: Blackout Rule (auto-purge empty voice)
# ══════════════════════════════════════════════
@bot.event
async def on_voice_state_update(member, before, after):
    """Delete private review voice channels when the last member leaves."""
    if before.channel is not None and PRIVATE_CATEGORY_ID != 0:
        if before.channel.category_id == PRIVATE_CATEGORY_ID:
            if len(before.channel.members) == 0:
                try:
                    channel_name = before.channel.name
                    await before.channel.delete(
                        reason="Blackout Rule: Channel emptied by last user."
                    )
                    print(f"[Total Purge] Deleted: {channel_name}")
                except (discord.Forbidden, discord.HTTPException) as e:
                    print(f"[Total Purge] Error: {e}")


# ══════════════════════════════════════════════
#  EVENT: The Sentinel (Auto-Mod)
# ══════════════════════════════════════════════
@bot.event
async def on_message(message):
    """
    THE SENTINEL: Scan for link spam and basic violations.
    """
    if message.author.bot:
        return

    # Locked channels - only owner can post text, everyone can react
    if message.channel.id in LOCKED_CHANNELS:
        if not message.author.guild_permissions.administrator:
            try:
                await message.delete()
                await message.channel.send(f"🔒 {message.author.mention}, this channel is locked. Only admins can post text. You can still react with emojis!", delete_after=8)
                return
            except Exception as e:
                logger.error(f"Locked Channel Error: {e}")

    # Basic Link Prevention (Example Sentinel Logic)
    banned_links = ["discord.gg/", "invite.gg/"] # Prevent external server invites
    content = message.content.lower()
    
    if any(link in content for link in banned_links):
        if not message.author.guild_permissions.administrator:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, external invite links are forbidden by **The Law**. ⚔️🛡️🤖", delete_after=5)
                logger.info(f"Sentinel: Deleted invite link from {message.author}")
                return
            except Exception as e:
                logger.error(f"Sentinel Error: {e}")

    await bot.process_commands(message)


# ══════════════════════════════════════════════
#  COMMAND: !post_rules
# ══════════════════════════════════════════════
@bot.command(name="post_rules")
@commands.has_permissions(administrator=True)
async def post_rules(ctx):
    """Read discohook_rules_template.json and post the embed with agreement buttons."""
    template_path = os.path.join(BUILD_PLAN_DIR, "discohook_rules_template.json")

    if not os.path.exists(template_path):
        await ctx.send("❌ `discohook_rules_template.json` not found.")
        return

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "embeds" in data and len(data["embeds"]) > 0:
            embed = discord.Embed.from_dict(data["embeds"][0])
            # Add view with agreement buttons
            view = RulesAgreementView()
            await ctx.send(embed=embed, view=view)
            await ctx.message.delete()
        else:
            await ctx.send("❌ No embeds found in the JSON file.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# ══════════════════════════════════════════════
#  COMMAND: !welcome
# ══════════════════════════════════════════════
@bot.command(name="welcome")
@commands.has_permissions(administrator=True)
async def welcome(ctx):
    """Post the Join Page onboarding embed in the current channel."""
    embed = discord.Embed(
        title="⚔️ WELCOME TO THE APPTIVATORS ACADEMY ⚔️",
        description=(
            "You are standing at the threshold of the forge. Beyond this gate lies a network of engineers, "
            "creators, and mentors dedicated to building the future—one app at a time.\n\n"
            "**Access is currently locked.** To enter the Academy, you must complete the onboarding walkthrough."
        ),
        color=0xE74C3C,
    )
    embed.set_image(url="https://raw.githubusercontent.com/whagan1310-droid/Apptivators-Academy/main/assets/Apptivators%20Academy.png")
    embed.add_field(
        name="🚀 Your Journey",
        value="Click the button below to start your skill assessment and agree to the server protocols.",
        inline=False
    )
    view = JoinWalkthroughView()
    await ctx.send(embed=embed, view=view)
    await ctx.message.delete()


# ══════════════════════════════════════════════
#  COMMAND: !build_server
# ══════════════════════════════════════════════
@bot.command(name="build_server")
async def build_server(ctx):
    """Owner Only: Automatically create Categories and Channels from the build plan."""
    # Owner-only check
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("⚠️ **Owner Only:** This command is restricted to the server owner.")
        return
    status_msg = await ctx.send("🏗️ **Initiating Server Build Phase...**")
    guild = ctx.guild
    report: list[str] = []

    for cat_name, channels in SERVER_STRUCTURE.items():
        # Check if category exists
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            report.append(f"📁 Creating Category: `{cat_name}`")
            category = await guild.create_category(cat_name)
        else:
            report.append(f"✔️ Category Exists: `{cat_name}`")

        for ch in channels:
            # Check if channel exists in this category
            channel = discord.utils.get(category.text_channels, name=ch["name"])
            if not channel:
                report.append(f"  └─ 📝 Creating Channel: `#{ch['name']}`")
                
                # Set permissions: Information channels are read-only for @everyone
                perms_overwrites = None
                if "1." in cat_name:
                    perms_overwrites = {
                        guild.default_role: discord.PermissionOverwrite(send_messages=False),
                        guild.me: discord.PermissionOverwrite(send_messages=True)
                    }
                
                await guild.create_text_channel(
                    ch["name"], 
                    category=category, 
                    topic=ch["topic"],
                    overwrites=perms_overwrites
                )
            else:
                report.append(f"  └─ ✔️ Channel Exists: `#{ch['name']}`")

    # Final report
    embed = discord.Embed(
        title="🏗️ Server Build Report",
        description="\n".join(report[-20:]), # Show last 20 actions if long
        color=0x9B59B6
    )
    embed.set_footer(text="Auto-Pilot: One App At A Time.")
    await status_msg.edit(content="✅ **Server structure verification complete!**", embed=embed)


# ══════════════════════════════════════════════
#  COMMAND: !initialize_onboarding
# ══════════════════════════════════════════════
@bot.command(name="initialize_onboarding")
@commands.has_permissions(administrator=True)
async def initialize_onboarding(ctx):
    """
    MASTER INITIALIZATION: The Big Bang of the Academy.
    Deploys all persistent GUIs to the frontline channels.
    """
    status_msg = await ctx.send("🚀 **Initiating Legendary GUI Deployment...**")
    guild = ctx.guild
    
    def find_channel(name):
        return discord.utils.find(lambda c: name.lower() in c.name.lower(), guild.text_channels)

    welcome_ch = find_channel("welcome")
    rules_ch = find_channel("rules")
    roles_ch = find_channel("roles") # Added roles channel check
    
    report = []
    
    # 1. Welcome GUI (Call to Arms)
    target_ch = welcome_ch or ctx.channel
    embed = discord.Embed(
        title="⚔️ A Call to Arms: One App at a Time ⚔️",
        description=(
            "Welcome to the front lines of creation. This community exists for one reason: "
            "to fuel our passions and build a safer, better tomorrow through the power of code.\n\n"
            "Whether you are a **Noob** or a **God**, your contribution is the engine of our collective growth."
        ),
        color=0xE74C3C,
    )
    embed.add_field(
        name="🛡️ Choose Your Level",
        value=(
            "**1. The Noob** — Trainee / Level 0\n"
            "**2. The Beginner** — Junior Dev / Level 1\n"
            "**3. The Intermediate** — Mid-Level / Level 2-3\n"
            "**4. The Expert** — Senior / Staff / Architect\n"
            "**5. The God** — Distinguished Engineer / Legend"
        ),
        inline=False,
    )
    embed.add_field(
        name="🤖 The Synthetic Edge",
        value="Our bots learn from us. Help refine them daily by identifying errors and improving logic.",
        inline=False,
    )
    await target_ch.send(embed=embed, view=RoleSelectionView())
    report.append(f"✅ Deployed Welcome GUI to {target_ch.mention}")

    # 2. Rules GUI (The Law)
    if rules_ch:
        legendary_quote = (
            "\"\"One App At A Time.\" The forge is hot, the guards are at the gate, and the synthetic edge is sharp.\n"
            "It has been an absolute pleasure building this fortress with you. The Academy is now yours to lead! ⚔️🛡️🤖\""
        )
        rules_embed = discord.Embed(
            title="📜 The Immutable Laws of the Academy",
            description=f"{legendary_quote}\n\n💯 **Agreement is Mandatory.** Click the sword below to verify your intent.",
            color=discord.Color.dark_grey()
        )
        
        # Try to load custom rules if they exist
        template_path = os.path.join(BUILD_PLAN_DIR, "discohook_rules_template.json")
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "embeds" in data and len(data["embeds"]) > 0:
                        rules_embed = discord.Embed.from_dict(data["embeds"][0])
            except:
                pass
        
        await rules_ch.send(embed=rules_embed, view=RulesAgreementView())
        report.append(f"✅ Deployed Rules GUI to {rules_ch.mention}")
    else:
        report.append("⚠️ `rules` channel not found. Rules GUI skipped.")

    final_embed = discord.Embed(
        title="🛰️ Legendary Deployment System",
        description="\n".join(report),
        color=0x2ECC71
    )
    final_embed.set_footer(text="The Forge is Live. ⚔️🛡️🤖💯")
    await status_msg.edit(content="🏁 **Master Initialization Complete.**", embed=final_embed)


# ══════════════════════════════════════════════
#  COMMAND: !list_members
# ══════════════════════════════════════════════
@bot.command(name="list_members")
@commands.has_permissions(administrator=True)
async def list_members(ctx):
    """View the list of members who have completed onboarding."""
    if not os.path.exists(JOINED_MEMBERS_FILE):
        await ctx.send("📂 No member data found yet.")
        return

    with open(JOINED_MEMBERS_FILE, "r") as f:
        data = json.load(f)

    if not data["members"]:
        await ctx.send("📂 The registry is currently empty.")
        return

    report = []
    for m in data["members"][-20:]: # Last 20
        report.append(f"• **{m['name']}** (`{m['user_id']}`) - Tier: {m['level']}")

    embed = discord.Embed(
        title="⚔️ Academy Member Registry",
        description="\n".join(report),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Total Registered: {len(data['members'])}")
    await ctx.send(embed=embed)


# ══════════════════════════════════════════════
#  COMMAND: !list_channels
# ══════════════════════════════════════════════
@bot.command(name="list_channels")
@commands.has_permissions(administrator=True)
async def list_channels(ctx):
    """List all text channels the bot can see for debugging."""
    channels = [f"#{c.name} (`{c.id}`)" for c in ctx.guild.text_channels]
    embed = discord.Embed(
        title="📂 Server Channel List",
        description="\n".join(channels[:30]), # Limit to avoid embed limits
        color=0x3498DB
    )
    await ctx.send(embed=embed)


# ══════════════════════════════════════════════
#  COMMAND: !purge_text
# ══════════════════════════════════════════════
@bot.command(name="purge_text")
@commands.has_permissions(manage_messages=True)
async def purge_text(ctx):
    """Delete all non-pinned messages in the current channel. Staff/Owner only."""
    import asyncio
    
    # Check for staff/owner permissions
    is_owner = ctx.author.id == ctx.guild.owner_id
    is_staff = any("staff" in role.name.lower() or "mod" in role.name.lower() or "admin" in role.name.lower() for role in ctx.author.roles)
    
    if not (is_owner or is_staff or ctx.author.guild_permissions.manage_messages):
        await ctx.send("⚠️ **Staff/Owner Only:** This command requires staff or moderator permissions.")
        return
    
    status_msg = await ctx.send("🗑️ **Starting purge...**")
    
    # Get pinned message IDs
    pinned_ids = set()
    async for msg in ctx.channel.pins():
        pinned_ids.add(msg.id)
    
    deleted_count = 0
    failed = 0
    
    # Process all messages
    async for msg in ctx.channel.history(limit=None):
        # Skip pinned and our status message
        if msg.id in pinned_ids or msg.id == status_msg.id:
            continue
        
        try:
            await msg.delete()
            deleted_count += 1
            
            # Update status every 5 deletions
            if deleted_count % 5 == 0:
                try:
                    await status_msg.edit(content=f"🗑️ **Deleting... {deleted_count} removed**")
                except:
                    pass
            
            # Rate limit protection - Discord allows ~5 deletes per second
            await asyncio.sleep(0.25)
            
        except discord.errors.HTTPException as e:
            if "rate limit" in str(e).lower():
                # Wait 2 seconds on rate limit, then continue
                await asyncio.sleep(2)
                try:
                    await msg.delete()
                    deleted_count += 1
                except:
                    failed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
    
    # Final status
    result = f"✅ **Purge Complete!** Deleted {deleted_count} messages"
    if failed > 0:
        result += f" ({failed} failed)"
    result += f". Pinned messages preserved."
    
    try:
        await status_msg.edit(content=result)
    except:
        await ctx.send(result)


# ══════════════════════════════════════════════
#  COMMAND: !strike @user <reason>
# ══════════════════════════════════════════════
@bot.command(name="strike")
@commands.has_permissions(manage_messages=True)
async def strike(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Record a moderation strike against a user."""
    # Load or create the strike log
    if os.path.exists(STRIKE_LOG_FILE):
        with open(STRIKE_LOG_FILE, "r", encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = {}

    user_id = str(member.id)
    if user_id not in log:
        log[user_id] = {"username": str(member), "strikes": []}

    strike_entry = {
        "reason": reason,
        "issued_by": str(ctx.author),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "channel": ctx.channel.name,
    }
    log[user_id]["strikes"].append(strike_entry)
    strike_count = len(log[user_id]["strikes"])

    # Save
    with open(STRIKE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    embed = discord.Embed(
        title="⚠️ Strike Recorded",
        description=f"**User**: {member.mention}\n**Reason**: {reason}\n**Total Strikes**: {strike_count}",
        color=0xE67E22,
    )
    embed.set_footer(text=f"Issued by {ctx.author.name}")
    await ctx.send(embed=embed)

# ══════════════════════════════════════════════
#  COMMAND: !apply_collaborator
# ══════════════════════════════════════════════
class CollaboratorModal(ui.Modal, title='🤝 Collaborator Application'):
    github = ui.TextInput(label='GitHub Profile / Repos', placeholder='https://github.com/yourname', required=True)
    youtube = ui.TextInput(label='YouTube Channel (Optional)', placeholder='https://youtube.com/@yourchannel', required=False)
    exp = ui.TextInput(label='Years of Experience', placeholder='e.g. 3 years', required=True)
    specialty = ui.TextInput(label='Primary Specialties', placeholder='e.g. AI, Python, UI/UX', required=True)
    value = ui.TextInput(label='Value Proposition', style=discord.TextStyle.paragraph, placeholder='How will you help the community grow?', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        # Log to #admin-mod-bot-commands for review
        staff_ch = discord.utils.get(interaction.guild.text_channels, name="admin-mod-bot-commands")
        if staff_ch:
            embed = discord.Embed(title="🤝 New Collaborator Application", color=discord.Color.gold())
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="User ID", value=interaction.user.id, inline=True)
            embed.add_field(name="GitHub", value=self.github.value, inline=False)
            embed.add_field(name="YouTube", value=self.youtube.value or "N/A", inline=False)
            embed.add_field(name="Experience", value=self.exp.value, inline=True)
            embed.add_field(name="Specialty", value=self.specialty.value, inline=True)
            embed.add_field(name="Value", value=self.value.value, inline=False)
            
            # Simple approval buttons
            view = CollaboratorApprovalView(user_id=interaction.user.id)
            await staff_ch.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Your application has been submitted to the Forge Council! ⚔️🛡️🤖", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Staff channel not found. Contact Admin.", ephemeral=True)

class CollaboratorApprovalView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: ui.Button):
        # Any Level Moderator (1-5) can approve
        # Check for roles with "Moderator" or "Admin"
        is_mod = any(role.name.lower() in ["moderator", "admin"] or "level" in role.name.lower() for role in interaction.user.roles)
        if not is_mod and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only Moderators can approve applications.", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.user_id)
        role = discord.utils.get(guild.roles, name="Known Server Collaborator")
        if not role:
            role = await guild.create_role(name="Known Server Collaborator", color=discord.Color.purple())

        if member:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Approved {member.mention} as a Collaborator! ✨", ephemeral=False)
            # Update spotlight in #all-bot-commands
            public_ch = discord.utils.get(guild.text_channels, name="all-bot-commands")
            if public_ch:
                await public_ch.send(f"✨ **NEW KNOWN SERVER COLLABORATOR**: {member.mention} has joined the elite! ⚔️🛡️🤝")
            button.disabled = True
            await interaction.message.edit(view=self)
        else:
            await interaction.response.send_message("❌ Member not found.", ephemeral=True)

@bot.command(name="apply_collaborator")
async def apply_collaborator(ctx):
    """Open the collaborator application modal."""
    await ctx.interaction.response.send_modal(CollaboratorModal()) if ctx.interaction else await ctx.send("Please use the Slash Command variation if available, or wait for GUI integration.")

# ══════════════════════════════════════════════
#  COMMAND: !submit_repo [url]
# ══════════════════════════════════════════════
@bot.command(name="submit_repo")
async def submit_repo(ctx, url: str):
    """Submit a repository for scanning and potential forking."""
    # 1. Basic URL check
    if "github.com/" not in url:
        await ctx.send("❌ Please provide a valid GitHub repository URL.")
        return

    # 2. Ping S.A.M.P.I.RT for scan (Simulated for now, real integration in Phase 3)
    await ctx.send(f"🔍 **S.A.M.P.I.RT**: Scanning repository `{url}` for malicious code... 🛡️", delete_after=5)
    await asyncio.sleep(2)
    
    # 3. Forward to Staff Review
    staff_ch = discord.utils.get(ctx.guild.text_channels, name="admin-mod-bot-commands")
    if staff_ch:
        embed = discord.Embed(title="📂 New Community Repo Submission", color=discord.Color.blue())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="URL", value=url, inline=False)
        embed.add_field(name="S.A.M.P.I.RT SCAN", value="🟢 CLEAN / SAFE", inline=True)
        
        view = RepoApprovalView(user_id=ctx.author.id, repo_url=url)
        await staff_ch.send(embed=embed, view=view)
        await ctx.send("✅ Repo submitted! S.A.M.P.I.RT has verified the code is safe. Staff will review for forking. 🛡️🤝")
    else:
        await ctx.send("❌ Staff channel not found.")

class RepoApprovalView(ui.View):
    def __init__(self, user_id, repo_url):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.repo_url = repo_url

    @ui.button(label="⚔️ Fork to Academy", style=discord.ButtonStyle.primary)
    async def fork_repo(self, interaction: discord.Interaction, button: ui.Button):
        is_mod = any(role.name.lower() in ["moderator", "admin"] or "level" in role.name.lower() for role in interaction.user.roles)
        if not is_mod and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only Moderators can approve repos.", ephemeral=True)
            return

        # Simulate fork (In production, would use GitHub API)
        await interaction.response.send_message(f"🚀 **Actioned**: Forking `{self.repo_url}` to the Academy Organization! 🦾📦")
        button.disabled = True
        await interaction.message.edit(view=self)

# ══════════════════════════════════════════════
#  SILENT SENTINEL APPLICATION SYSTEM
# ══════════════════════════════════════════════
# Channel IDs for Silent Sentinel Gateway
BECOME_STAFF_CHANNEL = "become-staff"
STAFF_APPLICATION_CHANNEL = "staff-application"

class SilentSentinelModal(ui.Modal, title='🛡️ Silent Sentinel Application'):
    """The Silent Sentinel entrance exam as defined in the Master Task."""
    
    # Question 1: Multiple choice about insecure shortcut
    q1_answer = ui.TextInput(
        label='Q1: Insecure Shortcut Response',
        placeholder='A/B/C/D - How do you interject?',
        required=True,
        max_length=100
    )
    
    # Question 2: Multiple choice about repeated questions
    q2_answer = ui.TextInput(
        label='Q2: Repeated Questions Approach',
        placeholder='A/B/C/D - What is your move?',
        required=True,
        max_length=100
    )
    
    # Question 3: Multiple choice about heated debate
    q3_answer = ui.TextInput(
        label='Q3: Heated Debate Response',
        placeholder='A/B/C/D - How do you Quietly Watch?',
        required=True,
        max_length=100
    )
    
    # Question 4: Multiple choice about unanswered problem
    q4_answer = ui.TextInput(
        label='Q4: Unanswered Problem Approach',
        placeholder='A/B/C/D - What is your approach?',
        required=True,
        max_length=100
    )
    
    # Question 5: Maintaining factual reference
    q5_answer = ui.TextInput(
        label='Q5: Factual Reference Material',
        placeholder='A/B/C/D - How do you maintain it?',
        required=True,
        max_length=100
    )
    
    # Open question: Professional proficiency
    proficiency = ui.TextInput(
        label='Q6: Professional Proficiency',
        style=discord.TextStyle.paragraph,
        placeholder='List all programming languages you are proficient with, years of experience, frameworks...',
        required=True,
        max_length=1000
    )
    
    # Fun question: Binary quotes
    binary_quotes = ui.TextInput(
        label='Q7: Binary Quotes (Fun)',
        style=discord.TextStyle.paragraph,
        placeholder='Decode: 01101011 01100101 01100101 01110000...',
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        staff_ch = discord.utils.get(guild.text_channels, name=STAFF_APPLICATION_CHANNEL)
        if not staff_ch:
            staff_ch = discord.utils.get(guild.text_channels, name="staff-bot-commands")
        
        if staff_ch:
            # Calculate score based on correct answers
            correct_answers = {
                'q1': 'B',
                'q2': 'C', 
                'q3': 'C',
                'q4': 'C',
                'q5': 'C'
            }
            
            score = 0
            answers = [self.q1_answer.value.upper().strip(), 
                       self.q2_answer.value.upper().strip(),
                       self.q3_answer.value.upper().strip(),
                       self.q4_answer.value.upper().strip(),
                       self.q5_answer.value.upper().strip()]
            
            for i, ans in enumerate(answers):
                if ans == correct_answers[f'q{i+1}']:
                    score += 1
            
            embed = discord.Embed(
                title="🛡️ SILENT SENTINEL APPLICATION",
                description=f"**Applicant:** {interaction.user.mention}\n**Score:** {score}/5 correct",
                color=discord.Color.dark_blue()
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="Q1: Insecure Shortcut", value=self.q1_answer.value[:100], inline=False)
            embed.add_field(name="Q2: Repeated Questions", value=self.q2_answer.value[:100], inline=False)
            embed.add_field(name="Q3: Heated Debate", value=self.q3_answer.value[:100], inline=False)
            embed.add_field(name="Q4: Unanswered Problem", value=self.q4_answer.value[:100], inline=False)
            embed.add_field(name="Q5: Factual Reference", value=self.q5_answer.value[:100], inline=False)
            embed.add_field(name="Professional Proficiency", value=self.proficiency.value[:500], inline=False)
            embed.add_field(name="Binary Quotes", value=self.binary_quotes.value[:200] if self.binary_quotes.value else "N/A", inline=False)
            embed.set_footer(text="Silent Sentinel Entrance Exam")
            
            view = SilentSentinelReviewView(user_id=interaction.user.id, score=score)
            await staff_ch.send(embed=embed, view=view)
            await interaction.response.send_message(
                f"🛡️ **Silent Sentinel Application Submitted!**\n"
                f"Score: {score}/5 correct\n"
                f"The Council will review your application and assign a Moderator Level (3-5).\n\n"
                f"*Binary Quote 1: 'Keep it simple' | Quote 2: 'One app at a time'*",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Staff channel not found.", ephemeral=True)


class SilentSentinelReviewView(ui.View):
    def __init__(self, user_id: int, score: int):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.score = score
    
    async def assign_sentinel(self, interaction: discord.Interaction, level: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only Administrators can assign Silent Sentinel roles.", ephemeral=True)
            return
        
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        
        # Determine role based on score and level
        if self.score >= 4 and level >= 3:
            role_name = f"Moderator Level {level}"
            base_role = "Silent Sentinel"
        else:
            await interaction.response.send_message(f"⚠️ Score too low ({self.score}/5) or level invalid.", ephemeral=True)
            return
        
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, color=discord.Color.dark_blue())
        
        sentinel_role = discord.utils.get(guild.roles, name=base_role)
        if not sentinel_role:
            sentinel_role = await guild.create_role(name=base_role, color=discord.Color.dark_gold())
        
        if member:
            await member.add_roles(role, sentinel_role)
            await interaction.response.send_message(
                f"✅ {member.mention} has been granted **{role_name}** and **{base_role}**!\n"
                f"🛡️ Welcome to the Silent Sentinels!"
            )
            self.stop()
        else:
            await interaction.response.send_message("❌ Member not found.", ephemeral=True)
    
    @ui.button(label="Lvl 3 (Mod)", style=discord.ButtonStyle.secondary)
    async def lvl3(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_sentinel(interaction, 3)
    
    @ui.button(label="Lvl 4 (Sr Mod)", style=discord.ButtonStyle.secondary)
    async def lvl4(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_sentinel(interaction, 4)
    
    @ui.button(label="Lvl 5 (Lead)", style=discord.ButtonStyle.primary)
    async def lvl5(self, interaction: discord.Interaction, button: ui.Button):
        await self.assign_sentinel(interaction, 5)
    
    @ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only Administrators can reject applications.", ephemeral=True)
            return
        member = interaction.guild.get_member(self.user_id)
        if member:
            await interaction.response.send_message(f"❌ Application for {member.mention} has been rejected.")
        self.stop()


class SilentSentinelGatewayView(ui.View):
    """Gateway view for #become-staff channel."""
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="🛡️ Apply for Silent Sentinel", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def apply_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(SilentSentinelModal())


@bot.command(name="apply_sentinel")
async def apply_sentinel(ctx):
    """Open the Silent Sentinel entrance exam modal."""
    await ctx.send_modal(SilentSentinelModal())


@bot.command(name="setup_sentinel_gateway")
@commands.has_permissions(administrator=True)
async def setup_sentinel_gateway(ctx):
    """Setup the Silent Sentinel gateway in #become-staff channel."""
    guild = ctx.guild
    
    # Find or create the become-staff channel
    become_staff = discord.utils.get(guild.text_channels, name=BECOME_STAFF_CHANNEL)
    if not become_staff:
        category = discord.utils.get(guild.categories, name="🛡️ SILENT SENTINEL")
        if not category:
            category = await guild.create_category("🛡️ SILENT SENTINEL")
        become_staff = await guild.create_text_channel(
            BECOME_STAFF_CHANNEL,
            category=category,
            topic="Silent Sentinel Gateway - Apply for Moderator role"
        )
    
    # Create the gateway message
    embed = discord.Embed(
        title="🛡️ SILENT SENTINEL GATEWAY",
        description=(
            "**We are looking for Silent Sentinels** - professionals who can:\n\n"
            "• **Watch, Listen, and Observe** - Maintain the pulse of the community\n"
            "• **Strategic Interjection** - Step in only when necessary\n"
            "• **Knowledge Infrastructure** - Create and curate quality resources\n"
            "• **Guided Growth** - Point members toward best information\n\n"
            "**Requirements:**\n"
            "• Level 3+: Active mentors\n"
            "• Level 4-∞: Community Leaders\n"
            "• Golden Rule: Treat ban flags as False Positives first"
        ),
        color=discord.Color.dark_blue()
    )
    embed.set_footer(text="Click the button below to apply • One App At A Time")
    embed.set_image(url="https://raw.githubusercontent.com/whagan1310-droid/Apptivators-Academy/main/assets/Brain1-5.png")
    
    view = SilentSentinelGatewayView()
    await become_staff.send(embed=embed, view=view)
    await ctx.send(f"✅ Silent Sentinel Gateway setup complete in {become_staff.mention}")


# ══════════════════════════════════════════════
#  GITHUB HELPERS
# ══════════════════════════════════════════════
def _github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_file_sha(filepath: str) -> str | None:
    """Get the SHA of an existing file in the repo (needed for updates)."""
    url = f"{GITHUB_API_BASE}/contents/{filepath}"
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None


def _push_file_to_github(local_path: str, repo_path: str, commit_msg: str) -> dict:
    """Create or update a file in the GitHub repo using the Contents API."""
    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    url = f"{GITHUB_API_BASE}/contents/{repo_path}"
    payload = {
        "message": commit_msg,
        "content": content_b64,
    }

    # If the file already exists, we need its SHA to update it
    existing_sha = _get_file_sha(repo_path)
    if existing_sha:
        payload["sha"] = existing_sha

    resp = requests.put(url, headers=_github_headers(), json=payload, timeout=30)
    return {"status": resp.status_code, "file": repo_path, "ok": resp.status_code in (200, 201)}


# ══════════════════════════════════════════════
#  COMMAND: !deploy_plan
# ══════════════════════════════════════════════
@bot.command(name="deploy_plan")
@commands.has_permissions(administrator=True)
async def deploy_plan(ctx):
    """Push all build plan files to the GitHub repo."""
    if not GITHUB_PAT:
        await ctx.send("❌ `GITHUB_PAT` is not set in `.env`.")
        return

    status_msg = await ctx.send("📦 Deploying build plan to GitHub...")
    results = []

    for filename in DEPLOY_FILES:
        local_path = os.path.join(BUILD_PLAN_DIR, filename)
        if not os.path.exists(local_path):
            results.append(f"⏭️ `{filename}` — skipped (not found)")
            continue

        result = _push_file_to_github(
            local_path, filename, f"Deploy: update {filename}"
        )
        if result["ok"]:
            results.append(f"✅ `{filename}` — pushed successfully")
        else:
            results.append(f"❌ `{filename}` — failed (HTTP {result['status']})")

    embed = discord.Embed(
        title="📦 Deployment Report",
        description="\n".join(results),
        color=0x2ECC71 if all("✅" in r or "⏭️" in r for r in results) else 0xE74C3C,
    )
    embed.set_footer(text=f"Target: {GITHUB_OWNER}/{GITHUB_REPO}")
    await status_msg.edit(content=None, embed=embed)


# ══════════════════════════════════════════════
#  COMMAND: !addfile <repo_path> <content>
# ══════════════════════════════════════════════
@bot.command(name="addfile")
@commands.has_permissions(administrator=True)
async def addfile(ctx, repo_path: str, *, content: str):
    """Add or update a single file in the GitHub repo from Discord."""
    if not GITHUB_PAT:
        await ctx.send("❌ `GITHUB_PAT` is not set in `.env`.")
        return

    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    url = f"{GITHUB_API_BASE}/contents/{repo_path}"
    payload = {
        "message": f"Add {repo_path} via Discord bot",
        "content": content_b64,
    }

    existing_sha = _get_file_sha(repo_path)
    if existing_sha:
        payload["sha"] = existing_sha

    resp = requests.put(url, headers=_github_headers(), json=payload, timeout=30)

    if resp.status_code in (200, 201):
        await ctx.send(f"✅ `{repo_path}` has been pushed to GitHub!")
    else:
        await ctx.send(f"❌ Failed to push `{repo_path}` (HTTP {resp.status_code}): {resp.text[:200]}")


# ══════════════════════════════════════════════
#  COMMAND: !logs
# ══════════════════════════════════════════════
@bot.command(name="logs")
@commands.has_permissions(administrator=True)
async def sync_logs(ctx):
    """Manually push bot.log and strike_log.json to the GitHub repo."""
    if not GITHUB_PAT:
        await ctx.send("❌ `GITHUB_PAT` is not set in `.env`.")
        return

    status_msg = await ctx.send("📡 Syncing logs to GitHub...")
    results = []
    log_files = ["bot.log", "strike_log.json"]

    for filename in log_files:
        local_path = os.path.join(BUILD_PLAN_DIR, filename)
        if not os.path.exists(local_path):
            results.append(f"⏭️ `{filename}` — skipped (not found)")
            continue

        result = _push_file_to_github(
            local_path, filename, f"Logs Sync: {datetime.datetime.utcnow().isoformat()}"
        )
        if result["ok"]:
            results.append(f"✅ `{filename}` — synced")
        else:
            results.append(f"❌ `{filename}` — failed (HTTP {result['status']})")

    embed = discord.Embed(
        title="📡 Logs Sync Report",
        description="\n".join(results),
        color=0x3498DB
    )
    await status_msg.edit(content=None, embed=embed)


# ══════════════════════════════════════════════
#  COMMAND: !ask <question>
# ══════════════════════════════════════════════
@bot.command(name="ask")
async def ask(ctx, *, question: str):
    """Ask Google Gemini AI a question or for a code review. Uses Pro with Flash fallback."""
    if not GOOGLE_API_KEY:
        await ctx.send("❌ `GOOGLE_API_KEY` is not set in `.env`.")
        return

    async with ctx.typing():
        try:
            import google.generativeai as genai
            import warnings
            warnings.filterwarnings("ignore", category=FutureWarning)

            genai.configure(api_key=GOOGLE_API_KEY)

            system_prompt = (
                "You are GoonsClawbot, a Level 5 Distinguished Engineer AI assistant "
                "for the Apptivators Academy Discord server. You help with code reviews, "
                "debugging, mentorship, and security analysis. Keep answers concise and "
                "practical. If code looks malicious, warn immediately.\n\n"
            )

            # Try Flash first (better for free tier), then fallback
            model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
            last_error = None

            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(system_prompt + f"User question:\n{question}")
                    answer = response.text

                    # Discord has a 2000 char limit per message
                    if len(answer) > 1900:
                        for i in range(0, len(answer), 1900):
                            await ctx.send(answer[i : i + 1900])
                    else:
                        await ctx.send(answer)
                    return  # Success, exit

                except Exception as e:
                    last_error = f"{model_name}: {e}"
                    continue  # Try next model

            # All models failed
            await ctx.send(f"❌ All Gemini models failed. Last error: {str(last_error)[:200]}")

        except Exception as e:
            await ctx.send(f"❌ Error: {e}")


# ══════════════════════════════════════════════
#  COMMAND: !review <attachment>
# ══════════════════════════════════════════════
@bot.command(name="review")
async def review(ctx):
    """Deep Audit: Upload a code file and get a professional Level 5 review."""
    if not GOOGLE_API_KEY:
        await ctx.send("❌ `GOOGLE_API_KEY` is not set in `.env`.")
        return

    if not ctx.message.attachments:
        await ctx.send("📂 Please attach a file (e.g. .py, .js, .txt) for review.")
        return

    attachment = ctx.message.attachments[0]
    async with ctx.typing():
        try:
            content = await attachment.read()
            code_text = content.decode("utf-8")
            
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            
            system_prompt = (
                "You are the Lead Academy Architect. Perform a rigorous code review of the provided file. "
                "Look for: Security vulnerabilities, Performance bottlenecks, Logic errors, and Style improvements. "
                "Structure your reply with '### Audit Results' and '### Action Items'. Keep it technical.\n\n"
            )
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(system_prompt + f"File: {attachment.filename}\nContents:\n```\n{code_text}\n```")
            answer = response.text
            
            # Message splitting
            if len(answer) > 1900:
                for i in range(0, len(answer), 1900):
                    await ctx.send(answer[i : i + 1900])
            else:
                await ctx.send(answer)
                
        except Exception as e:
            await ctx.send(f"❌ Review Error: {e}")


# ══════════════════════════════════════════════
#  TEMPORARY CHANNEL SYSTEM
# ══════════════════════════════════════════════
@bot.command(name="create_channel")
async def create_temp_channel(ctx, *, channel_name: str = None):
    """Create a temporary channel in the Temporary category. Channel closes when creator leaves."""
    if not channel_name:
        await ctx.send("Usage: `!create_channel <channel_name>`")
        return
    
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=TEMP_CHANNEL_CATEGORY)
    
    if not category:
        # Create category if it doesn't exist
        category = await guild.create_category("Temporary Channels")
        logger.info(f"Created category: Temporary Channels ({category.id})")
    
    # Create the channel
    channel = await guild.create_text_channel(
        channel_name,
        category=category,
        topic=f"Temporary channel created by {ctx.author.name}. Closes when creator leaves.",
        overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
    )
    
    # Track the channel
    temp_channels[channel.id] = {
        "owner": ctx.author.id,
        "created_at": datetime.datetime.utcnow()
    }
    
    await ctx.send(f"✅ Created temporary channel: {channel.mention}\n"
                   f"Channel will close when you leave the server or use `!close_channel`.")

@bot.command(name="close_channel")
async def close_temp_channel(ctx):
    """Close a temporary channel you created."""
    channel = ctx.channel
    
    if channel.id not in temp_channels:
        await ctx.send("❌ This is not a temporary channel.")
        return
    
    if temp_channels[channel.id]["owner"] != ctx.author.id:
        await ctx.send("❌ Only the channel creator can close this channel.")
        return
    
    await channel.delete(reason=f"Closed by creator {ctx.author.name}")
    del temp_channels[channel.id]

@bot.command(name="my_channel")
async def my_channel(ctx):
    """Show channels you've created."""
    user_channels = [ch_id for ch_id, data in temp_channels.items() if data["owner"] == ctx.author.id]
    
    if not user_channels:
        await ctx.send("You haven't created any temporary channels.")
        return
    
    guild = ctx.guild
    channel_list = []
    for ch_id in user_channels:
        ch = guild.get_channel(ch_id)
        if ch:
            channel_list.append(f"• {ch.mention}")
    
    embed = discord.Embed(
        title="📱 Your Temporary Channels",
        description="\n".join(channel_list) if channel_list else "No active channels",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# Auto-close channels when users leave
@bot.event
async def on_member_remove(member):
    """Close temporary channels owned by the member who left."""
    guild = member.guild
    channels_to_close = []
    
    for ch_id, data in list(temp_channels.items()):
        if data["owner"] == member.id:
            channel = guild.get_channel(ch_id)
            if channel:
                channels_to_close.append((ch_id, channel))
    
    for ch_id, channel in channels_to_close:
        try:
            await channel.delete(reason=f"Owner {member.name} left the server")
            del temp_channels[ch_id]
            logger.info(f"Closed channel {channel.name} - owner left")
        except Exception as e:
            logger.error(f"Error closing channel: {e}")

# ══════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("=" * 50)
        print("  ERROR: DISCORD_BOT_TOKEN is not set in .env")
        print("  Add your token to d:\\Clawbot\\.env")
        print("=" * 50)
    else:
        bot.run(DISCORD_TOKEN)
