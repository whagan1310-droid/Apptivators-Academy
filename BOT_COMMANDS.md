# 🤖 Bot Command Reference

## Bot Overview

| Bot | Type | Prefix | Purpose |
|-----|------|--------|---------|
| **StrikeSource_Clawbot** | Custom Admin | `!` (empty) | Server management, onboarding, administration |
| **S.A.M.P.I.RT** | Custom Security | `!!` | Security, threat detection, moderation |
| **SonicForge** | Music | `!sonic_` | Audio/Music streaming |
| **SyncFlux** | Media | `!sync_` | YouTube/Colab link synchronization |

---

## 🦾 StrikeSource_Clawbot

**Prefix:** `!` (empty prefix - just type the command)
**Type:** Custom Server Bot (Admin Controlled)
**Commands:** Administrator & Server Management

### Administrator Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!post_rules` | Admin | Post rules embed to #rules channel | `!post_rules` |
| `!welcome` | Admin | Send welcome message | `!welcome` |
| `!build_server` | Admin | Create server structure from SERVER_STRUCTURE | `!build_server` |
| `!initialize_onboarding` | Admin | Set up onboarding carousel buttons | `!initialize_onboarding` |
| `!list_members` | Admin | List all server members with roles | `!list_members` |
| `!list_channels` | Admin | List all channels and categories | `!list_channels` |
| `!purge_text` | Admin | Delete recent messages in channel | `!purge_text` |
| `!deploy_plan` | Admin | Push build plan files to GitHub | `!deploy_plan` |
| `!addfile <path> <content>` | Admin | Add file to GitHub repo | `!addfile README.md Hello World` |

### Moderation Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!strike @user [reason]` | Mod+ | Issue a strike to a member | `!strike @user Spamming` |

### Application Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!apply_collaborator` | Everyone | Submit collaborator application | `!apply_collaborator` |
| `!submit_repo <url>` | Everyone | Share a GitHub repository | `!submit_repo https://github.com/...` |
| `!apply_sentinel` | Everyone | Open Silent Sentinel exam modal | `!apply_sentinel` |
| `!setup_sentinel_gateway` | Admin | Create Silent Sentinel gateway message | `!setup_sentinel_gateway` |

### AI Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!ask <question>` | Everyone | Ask AI a question (Google Gemini) | `!ask How do I set up Python?` |
| `!review` | Admin | Review recent bot activity | `!review` |

### Logging Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!logs` | Admin | Sync and display recent logs | `!logs` |

---

## 🛡️ S.A.M.P.I.RT (Security Bot)

**Prefix:** `!!`
**Type:** Custom Server Bot (Admin Controlled)
**Commands:** Security & Threat Detection

### Status & Scanning Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!!status` | Everyone | Show security status & threat level | `!!status` |
| `!!scan_channel [#channel]` | Mod+ | Scan channel for threats | `!!scan_channel` or `!!scan_channel #general` |
| `!!scan_user @user` | Mod+ | Scan user security profile | `!!scan_user @suspicious_user` |
| `!!query <user_id>` | Admin | Query user by ID for records | `!!query 123456789012345678` |

### Moderation Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!!freeze @user` | Mod+ | Freeze user (restrict permissions) | `!!freeze @troublemaker` |
| `!!unfreeze @user` | Mod+ | Unfreeze user | `!!unfreeze @user` |
| `!!tempban @user [reason]` | Admin | Temporarily ban user (1 year) | `!!tempban @user Repeated violations` |
| `!!ban @user [reason]` | Admin | Permanently ban user | `!!ban @user Malicious activity` |
| `!!unban <user_id>` | Admin | Unban user by ID | `!!unban 123456789012345678` |

### Link Management Commands

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!!sharelink <url> [description]` | Mod+ | Share a safe link | `!!sharelink https://github.com/... My cool project` |
| `!!list_links [limit]` | Everyone | List shared links (default 10) | `!!list_links 20` |
| `!!my_links` | Everyone | Show your shared links | `!!my_links` |

---

## 🎵 SonicForge (Music Bot)

**Prefix:** `!sonic_`
**Type:** Slash Commands Available
**Commands:** Audio & Music Streaming

### Slash Commands (Recommended)

| Slash Command | Permission | Description | Example |
|---------------|------------|-------------|---------|
| `/forge` | Everyone | Search and play music | `/forge search: lofi beats` |
| `/playlist` | Everyone | Show current playlist | `/playlist limit: 10` |
| `/skip` | DJ+ | Skip current track | `/skip` |
| `/pause` | DJ+ | Pause/resume playback | `/pause` |
| `/queue_clear` | DJ+ | Clear the queue | `/queue_clear` |
| `/now_playing` | Everyone | Show current track | `/now_playing` |
| `/volume <level>` | Admin | Set volume (0-100) | `/volume level: 50` |

### Prefix Commands (Alternative)

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!sonic_forge <search>` | Everyone | Search and play music | `!sonic_forge lofi hip hop` |
| `!sonic_playlist [limit]` | Everyone | Show playlist | `!sonic_playlist 15` |
| `!sonic_skip` | DJ+ | Skip track | `!sonic_skip` |
| `!sonic_pause` | DJ+ | Pause/resume | `!sonic_pause` |
| `!sonic_queue_clear` | DJ+ | Clear queue | `!sonic_queue_clear` |
| `!sonic_now_playing` | Everyone | Current track info | `!sonic_now_playing` |
| `!sonic_volume <level>` | Admin | Set volume | `!sonic_volume 75` |

---

## 📡 SyncFlux (Media Sync Bot)

**Prefix:** `!sync_`
**Type:** Slash Commands Available
**Commands:** YouTube & Colab Link Synchronization

### Slash Commands (Recommended)

| Slash Command | Permission | Description | Example |
|---------------|------------|-------------|---------|
| `/sync` | Mod+ | Sync a YouTube/Colab link | `/sync url: https://youtube.com/...` |
| `/flux_status` | Everyone | Show sync status | `/flux_status` |
| `/youtube [limit]` | Everyone | List synced YouTube links | `/youtube limit: 15` |
| `/colab [limit]` | Everyone | List synced Colab links | `/colab limit: 10` |
| `/my_syncs` | Everyone | Show your synced links | `/my_syncs` |
| `/clear_media <type>` | Admin | Clear media links (all/youtube/colab) | `/clear_media type: youtube` |

### Prefix Commands (Alternative)

| Command | Permission | Description | Example |
|---------|------------|-------------|---------|
| `!sync_sync <url> [description]` | Mod+ | Sync a link | `!sync_sync https://youtube.com/... Tutorial` |
| `!sync_flux_status` | Everyone | Show status | `!sync_flux_status` |
| `!sync_youtube [limit]` | Everyone | List YouTube links | `!sync_youtube 20` |
| `!sync_colab [limit]` | Everyone | List Colab links | `!sync_colab 15` |
| `!sync_my_syncs` | Everyone | Your synced links | `!sync_my_syncs` |
| `!sync_clear_media <type>` | Admin | Clear media | `!sync_clear_media all` |

---

## 🔘 Button Interactions (All Bots)

### StrikeSource_Clawbot Buttons

| Button | Location | Action |
|--------|----------|--------|
| `Level 1-5` | #roles | Assigns skill level role |
| `I AGREE` | #call-to-arms | Records member agreement |
| `🦾 Apply Here` | #become-staff | Opens Silent Sentinel exam modal |
| `Lvl 3-5 (Mod/Sr/Lead)` | Staff review | Assigns moderator role |

### S.A.M.P.I.RT Buttons

| Button | Location | Action |
|--------|----------|--------|
| Approve/Reject | Staff channel | Review shared links |

---

## 📝 Quick Reference Cards

### For Administrators
```
!build_server          - Create server structure
!initialize_onboarding - Setup onboarding buttons
!setup_sentinel_gateway - Create Silent Sentinel gateway
!deploy_plan           - Push to GitHub
!!query <user_id>      - Deep user lookup
```

### For Moderators
```
!strike @user [reason] - Issue strike
!!freeze @user         - Freeze account
!!scan_channel         - Check for threats
!sonic_volume 50       - Set music volume
```

### For Everyone
```
!apply_sentinel        - Apply for moderator
!ask <question>        - Ask AI
!!status               - Security status
!sonic_forge <search>  - Play music
!sync_youtube          - List YouTube links
```

---

## 🔗 Bot Token Locations

| Bot | Token File | Variable |
|-----|-------------|----------|
| StrikeSource_Clawbot | `.env` | `DISCORD_BOT_TOKEN` |
| S.A.M.P.I.RT | `S.A.M.P.I.RT/.env` | `DISCORD_BOT_TOKEN` |
| SonicForge | `SonicForge/.env` | `SONIC_FORGE_TOKEN` |
| SyncFlux | `SyncFlux/.env` | `SYNC_FLUX_TOKEN` |

---

*Last Updated: 2026-03-16*