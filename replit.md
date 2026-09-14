# LazyPrincessBot - Telegram Bot

## Overview
A Telegram bot built with Pyrogram that provides media searching, file streaming, and various utility features. It includes an aiohttp web server for file streaming capabilities.

## Project Architecture
- **bot.py** - Main entry point, starts the bot and web server
- **info.py** - Configuration from environment variables
- **lazybot/** - Bot client initialization and multi-client support
- **plugins/** - Bot command handlers and web routes
- **database/** - MongoDB database models (filters, users, chats)
- **server/** - Streaming server exceptions and routes
- **util/** - Utility functions (file streaming, templates, etc.)
- **Script.py** - Bot text templates and captions
- **utils.py** - Helper utilities

## Tech Stack
- **Language**: Python 3.10
- **Telegram Library**: Pyrogram / Pyrofork
- **Web Server**: aiohttp (port 5000)
- **Database**: MongoDB (external, via DATABASE_URI env var)
- **Media**: ffmpeg, yt-dlp

## Required Environment Variables (Secrets)
The bot requires these secrets to function:
- `BOT_TOKEN` - Telegram Bot Token from @BotFather
- `API_ID` - Telegram API ID from my.telegram.org
- `API_HASH` - Telegram API Hash from my.telegram.org
- `DATABASE_URI` - MongoDB connection string
- `DATABASE_URI2` - Secondary MongoDB connection string (optional)

## Running
The bot runs via `python bot.py` which starts both the Telegram bot and the aiohttp web server on port 5000.

## Recent Changes
- Configured for Replit environment (port 5000, added missing variables)
- Fixed CRLF line endings across Python files
- Added PING_INTERVAL, SLEEP_THRESHOLD, MULTI_CLIENT to info.py
- Cleaned up requirements.txt (removed duplicates, git dependencies)
