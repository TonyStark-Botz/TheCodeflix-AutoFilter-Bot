  # 🚀 TheCodeFlix AutoFilter Bot

  [![Python version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://python.org)
  [![MongoDB](https://img.shields.io/badge/MongoDB-Optimized-green.svg?logo=mongodb)](https://mongodb.com)
  [![Pyrogram](https://img.shields.io/badge/Pyrogram-v2.3-orange.svg?logo=telegram)](https://github.com/pyrogram/pyrogram)
  [![TheCodeFlix](https://img.shields.io/badge/Join-TheCodeFlix-FF1493.svg?logo=telegram)](https://t.me/TheCodeFlix)

  <p align="center">
    <b>A high-performance, fully customizable Telegram Movie & File AutoFilter Bot.</b><br>
    <i>Integrated with Web Streaming, File Hosting, Shorteners, and Advanced MongoDB Caching.</i>
  </p>
</div>

---

## 🌟 Key Features
*   **⚡ Ultra-Fast Search Engine**: Highly optimized regex caching and MongoDB text indexing for instantaneous file retrieval.
*   **🌐 Web Streaming & Direct Downloads**: Built-in `aiohttp` web server to stream or download videos directly outside of Telegram.
*   **🔗 Smart URL Shorteners**: Monetize your traffic by easily linking popular URL shorteners (e.g., EarnPro, Shareus).
*   **🔍 Inline & PM Search**: Users can search for files directly in the bot's PM or use it inline in other chats.
*   **📊 Comprehensive Dashboard & Broadcast**: Native broadcast capabilities and detailed statistics for admins.
*   **📝 Spelling Checks**: Intelligent typo-correction and IMDb-integrated movie suggestions.
*   **🎨 Custom UI & Webpages**: Fully tailored HTML pages (`util/req.html`, `util/dl.html`) featuring modern gradients and **TheCodeFlix** branding.
*   **🛡️ Multi-Client Support**: Load balance your bot traffic efficiently using Lazybot client structures.
*   **🔒 Channel & Group Security**: Mandatory Force Subscribe capabilities to restrict bot usage to channel members only.

---

## 🤖 Bot Commands

### 👤 For @BotFather (Public Commands)
*Copy and paste this list directly into `@BotFather` -> `Edit Bot` -> `Edit Commands`. Do **not** add admin commands here.*

```text
start - Check if bot is alive
id - Get your Telegram ID & Group ID
plan - Check available premium plans
myplan - Check your active premium plan
request - Request a movie or file
settings - Customize bot settings
font - Generate stylish fonts
connect - Connect a group to the bot
disconnect - Disconnect your group
connections - View connected groups
shortlink - Connect your own shortener
shortlink_info - Check your current shortener details
setshortlinkon - Enable shortlink for your group
setshortlinkoff - Disable shortlink for your group
set_tutorial - Set tutorial video for your shortlink
remove_tutorial - Remove custom tutorial video
filter - Add a manual filter
filters - View all manual filters
del - Delete a manual filter
delall - Delete all manual filters
```

### 👑 Owner & Admin Commands (Hidden)
*These commands are strictly restricted to the bot admins configured in the `ADMINS` environment variable. Do not add them to BotFather to prevent standard users from seeing them.*

* **Database & File Management:** `/channel`, `/delete`, `/deleteall`, `/deletefiles`, `/setskip`, `/set_template`
* **Premium & Users:** `/add_premium`, `/remove_premium`, `/premium_users`, `/ban`, `/unban`
* **Global Filters:** `/gfilter`, `/gfilters`, `/delg`, `/delallg`
* **System & Broadcast:** `/stats`, `/broadcast`, `/grp_broadcast`, `/logs`, `/clear_logs`, `/restart`

---

## ⚙️ Essential Environment Variables (Secrets)
The bot requires these secrets to function correctly. Some can be configured in your environment or hosting provider.

| Variable | Description | Required | Default |
| --- | --- | --- | --- |
| `BOT_TOKEN` | Your Telegram Bot Token from @BotFather | Yes | - |
| `API_ID` | Telegram API ID from my.telegram.org | Yes | - |
| `API_HASH` | Telegram API Hash from my.telegram.org | Yes | - |
| `DATABASE_URI` | MongoDB Connection String URI | Yes | - |
| `DATABASE_NAME` | Name of your MongoDB Database | Yes | - |
| `LOG_CHANNEL` | Channel ID for bot logs (starting with `-100`) | Yes | - |
| `ADMINS` | List of Admin User IDs (separated by space) | Yes | - |
| `AUTH_USERS` | Username/ID of users allowed to use inline search | No | Empty (Public) |
| `AUTH_CHANNEL` | ID of channel for Force-Subscribe (bot must be admin) | No | Empty |
| `CHANNELS` | List of channel IDs to index files from | No | Empty |
| `PICS` | Telegraph links of pictures for start message | No | Empty |

*(See `info.py` for a complete list of optional configuration variables like shortener APIs, welcome images, and tutorial links).*

---

## 🚀 Deployment Methods

### 1. Deploy to Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### 2. Local / VPS Deployment

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) | [MongoDB Database](https://www.mongodb.com/) | FFmpeg (optional)

```bash
# 1. Clone the repository
git clone https://github.com/TheCodeflix/AutoFilterBot.git
cd AutoFilterBot

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables
# Create a .env file or export the required variables in your terminal.

# 4. Run the bot locally
python3 bot.py
```
*The bot will start the Telegram client and bind the web server on Port `3000`/`5000` simultaneously.*

**Running on VPS / Production (PM2):**
```bash
npm install -g pm2
pm2 start bot.py --interpreter python3 --name "CodeFlixBot"
pm2 save
```

---

## 📂 Project Architecture
*   `bot.py` - Main entry point, starts the bot and web server.
*   `info.py` - Configuration loading from environment variables.
*   `lazybot/` - Bot client initialization and multi-client processing.
*   `plugins/` - Bot command handlers, route setups, inline searches, and auto-filters.
*   `database/` - MongoDB database models (filters, users, chats).
*   `server/` - Web streaming exceptions and server utilities.
*   `util/` - HTML templates (`req.html`, `dl.html`) and helper functions.
*   `Script.py` - Bot text templates, captions, and localized strings.
*   `utils.py` - Core utilities for time formatting, hashing, and link generation.

---

## 🤝 Community & Support
Need help setting up or want to request new features? Join our communities:

*   **GitHub**: [github.com/TheCodeflix](https://github.com/TheCodeflix)
*   **Telegram Updates**: [@LiveCraftBots](https://t.me/LiveCraftBots)
*   **TheCodeFlix TG**: [@TheCodeFlix](https://t.me/TheCodeFlix)
*   **TG Adult Community**: [@MyStudy_Hub](https://t.me/MyStudy_Hub)

---

<div align="center">
  <b>Made with ❤️ by TheCodeFlix</b><br>
  <i>Clean. Fast. Powerful.</i>
</div>
