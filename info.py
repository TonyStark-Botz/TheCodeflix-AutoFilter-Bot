###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###

import re
import os
from os import environ
from Script import script 

id_pattern = re.compile(r'^.\d+$')


def env_bool(name, default):
    value = environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"true", "yes", "1", "enable", "y", "on"}


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# ============================================================
# Bot Information
# ============================================================
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '00'))
API_HASH = environ.get('API_HASH', '00')
BOT_TOKEN = environ.get('BOT_TOKEN', "00")
# Bot & Forwarding Links
BOT_USERNAME = environ.get('BOT_USERNAME', 'All_Movie_Finder_Bot')
MEDIATOR_BOT = environ.get('MEDIATOR_BOT', 'Pikashow_Movies_Bot')
# Cross-bot redirect: when VERIFY=False, file requests are sent to this other bot's PM, Leave empty ('') to disable cross-bot redirect
CROSS_BOT_USERNAME = environ.get('CROSS_BOT_USERNAME', '')

# ============================================================
# User & Admin Management
# ============================================================
# Administrators and owner profile
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8526412924').split()]
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/TonyStark_Botz')
OWNERID = environ.get('OWNERID', '')
OWNERID = int(OWNERID) if OWNERID and id_pattern.search(OWNERID) else ADMINS[0]
if OWNERID not in ADMINS:
    ADMINS.append(OWNERID)
# PM Search toggle (True = users can search in PM, False = purana group-redirect behavior)
PM_SEARCH = environ.get('PM_SEARCH', 'True').lower() in ('true', '1', 'yes', 'on')
# Authorized Users
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
# Database Channels
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002439854017').split()]

# ============================================================
# Premium And Referral Settings
# ============================================================
# Premium User List
PREMIUM_USER = [int(user) if id_pattern.search(user) else user for user in environ.get('PREMIUM_USER', '').split()]
# Referral System
REFERAL_COUNT = int(environ.get('REFERAL_COUNT', '7')) # number of referral count
REFERAL_PREMEIUM_TIME = environ.get('REFERAL_PREMEIUM_TIME', '7day')
REFERAL_REWARD_LABEL = environ.get('REFERAL_REWARD_LABEL', '7 days')
# Premium Media & Images
QR_CODE = (environ.get('QR_CODE', 'https://i.ibb.co/WWz5mVnn/photo-2026-01-07-02-31-49-7592456191582666768.jpg'))
UPI_ID = environ.get('UPI_ID', 'kanus-network@axl')
LIMITED_SUPPORT_LNK = environ.get('LIMITED_SUPPORT_LNK', 'https://t.me/Kanus_Network_Bot')
SUBSCRIPTION = (environ.get('SUBSCRIPTION', 'https://graph.org/file/35323f5f7bb90113b4337.jpg'))

# ============================================================
# Force Subscription System
# ============================================================
# Force Join Settings
JOINREQ_MSG = env_bool('JOINREQ_MSG', False)
ASKFSUBINGRP = env_bool('ASKFSUBINGRP', False)
# Primary Auth Channel
auth_channel = environ.get('AUTH_CHANNEL', '-1002090374492')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
# Secondary Auth Channel
second_auth_channel = environ.get('SECOND_AUTH_CHANNEL', '-1002634993647')
SECOND_AUTH_CHANNEL = int(second_auth_channel) if second_auth_channel and id_pattern.search(second_auth_channel) else None
# Third Auth Channel
third_auth_channel = environ.get('THIRD_AUTH_CHANNEL', '-1002682132745')
THIRD_AUTH_CHANNEL = int(third_auth_channel) if third_auth_channel and id_pattern.search(third_auth_channel) else None
# Auth Groups
auth_grp = environ.get('AUTH_GROUP', '')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# ============================================================
# Logging & Monitoring System
# ============================================================
# Main Log Channels
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002321570567'))
LOG_CHANNEL_V = int(environ.get('LOG_CHANNEL', '-1002321570567'))
LOG_CHANNEL_RQ = int(environ.get('LOG_CHANNEL', '-1002321570567'))
LOG_CHANNEL_NRM = int(environ.get('LOG_CHANNEL', '-1002321570567'))
# Specialized Log Channels
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-1002450886765'))
LOG_CHANNEL_SESSIONS_FILES = int(environ.get('LOG_CHANNEL_SESSIONS_FILES', '-1002450886765'))
PM_MSG_LOG_CHANNEL = int(environ.get('PM_MSG_LOG_CHANNEL', '1002412021360'))
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', '-1002450886765'))
# Channel Management
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-1002412021360').split()]

# ============================================================
# Support, Request And Movies Update System
# ============================================================
# Support Channels
support_chat_id = environ.get('SUPPORT_CHAT_ID', '-1002626806582')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
# Support Links
DISCLAIMER_LNK = environ.get('DISCLAIMER_LNK', 'https://graph.org/Movies-Bot-Disclaimer-03-30')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/Movies_4_Download')
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/MovieSearchGroupHD')
SUPPORT_CHAT_LNK = environ.get('SUPPORT_CHAT_LNK', 'https://t.me/TheCodeflixSupport')
# Movies request channel
reqst_channel = environ.get('REQST_CHANNEL_ID', '-1002321570567')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
# New Movie Update Channel
SEND_MV_LOGS = env_bool('SEND_MV_LOGS', True)
MV_UPDATE_CHANNEL = int(environ.get('MV_UPDATE_CHANNEL', '-1002412021360'))

# ============================================================
# MongoDB Database Configuration
# ============================================================
# Primary Database
DATABASE_URI = environ.get('DATABASE_URI', "") #pikashow
DATABASE_NAME = environ.get('DATABASE_NAME', "pika1")
# Secondary Database (File Storage)
DATABASE_URI2 = environ.get('DATABASE_URI2', DATABASE_URI) #kanhaiya
DATABASE_NAME2 = environ.get('DATABASE_NAME2', "pika2")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'tgfiles')

# ============================================================
# Link Shortener System
# ============================================================
# Verification Settings
VERIFY = env_bool('VERIFY', False)
MIDVERIFY = env_bool('MIDVERIFY', False)
IS_SHORTLINK = env_bool('IS_SHORTLINK', False)

# First Shortlink Provider
SHORTLINK_URL = environ.get('FIRST_SHORTLINK_URL', 'vplink.in')
SHORTLINK_API = environ.get('FIRST_SHORTLINK_API', '8585479c122feb4c124dbad84240f316e5b6de21')
VERIFY_TUTORIAL = environ.get('FIRST_VERIFY_TUTORIAL', 'https://t.me/Movies_4_Download/633')
# Second Shortlink Provider
SECOND_SHORTLINK_URL = environ.get('SECOND_SHORTLINK_URL', 'arolinks.com')
SECOND_SHORTLINK_API = environ.get('SECOND_SHORTLINK_API', '29251e8ff879cb7a6e05355377c42df84f9050e0')
SECOND_VERIFY_TUTORIAL = environ.get('SECOND_VERIFY_TUTORIAL', 'https://t.me/Movies_4_Download/633')
# Third Shortlink Provider
THIRD_SHORTLINK_URL = environ.get('THIRD_SHORTLINK_URL', 'vplink.in')
THIRD_SHORTLINK_API = environ.get('THIRD_SHORTLINK_API', '1349b288c4e18748db3e359c49e0a8d721d0be82')
THIRD_VERIFY_TUTORIAL = environ.get('THIRD_VERIFY_TUTORIAL', 'https://t.me/Movies_4_Download/633')

# Stream Shortlink Provider
IS_SREAM_SHORTLINK = env_bool('IS_SREAM_SHORTLINK', False)
STREAM_SITE = (environ.get('STREAM_SITE', ''))
STREAM_API = (environ.get('STREAM_API', ''))
STREAMHTO = (environ.get('STREAMHTO', 'https://t.me/Movies_4_Download/633'))

# ============================================================
# Media & Template Configuration
# ============================================================
# Image Assets
PICS = (environ.get('PICS' , 'https://i.ibb.co/qFYr2VJd/photo-2026-02-13-04-29-28-7606202294543056912.jpg')).split()
NOR_IMG = environ.get("NOR_IMG", "https://te.legra.ph/file/a27dc8fe434e6b846b0f8.jpg")
MELCOW_VID = environ.get("MELCOW_VID", "https://i.ibb.co/2YNN9MD2/photo-2025-03-31-08-17-12-7487884823235657744.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://te.legra.ph/file/15c1ad448dfe472a5cbb8.jpg")
# Caption Templates
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
# IMDB Template
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")


# ============================================================
# Bot Settings
# ============================================================
# Alert Messages
MSG_ALRT = environ.get('MSG_ALRT', 'Hello My Dear Friends ❤️')
# Tutorial & Verification Links
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/Movies_4_Download/633')
IS_TUTORIAL = env_bool('IS_TUTORIAL', True)
# Time & Cache Settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
# Filter & Search Settings
USE_CAPTION_FILTER = env_bool('USE_CAPTION_FILTER', False)
AUTO_FFILTER = is_enabled((environ.get('AUTO_FFILTER', "True")), True)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
NO_RESULTS_MSG = env_bool('NO_RESULTS_MSG', True)
# Button & Display Settings
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), True)
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
MAX_B_TN = environ.get("MAX_B_TN", "10")
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
# IMDB & Information Settings
IMDB = is_enabled((environ.get('IMDB', "False")), False)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
# User & Content Management
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((environ.get('PROTECT_CONTENT', "False")), False)
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)

# ============================================================
# Search Filter Categories
# ============================================================
# Language Filters — full names only, no short codes, must be even count for button pairs
LANGUAGES = [
    "hindi", "english",
    "tamil", "telugu",
    "malayalam", "kannada",
    "bengali", "marathi",
    "gujrati", "punjabi",
    "bhojpuri", "odia"
]
# Season Filters
SEASONS = ["season 1" , "season 2" , "season 3" , "season 4", "season 5" , "season 6" , "season 7" , "season 8" , "season 9" , "season 10"]
# Episode Filters
EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40"]
# Quality Filters — includes all resolutions that ia_filterdb.py detects and stores
QUALITIES = ["480p", "576p", "720p", "1080p", "1440p", "2160p"]
# Year Filters
YEARS = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"]

# ============================================================
# Streaming Configuration
# ============================================================
# Server Settings
ON_HEROKU = False
PORT = environ.get("PORT", "8080")
URL = environ.get("URL", "https://whole-doti-pikashow-movies-bots-f5b9ff94.koyeb.app/")
# Binary Channel
BIN_CHANNEL = environ.get("BIN_CHANNEL", "-1002412021360")
if len(BIN_CHANNEL) == 0:
    print('Error - BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)

# ============================================================
# Configuration Log String
# ============================================================
LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###