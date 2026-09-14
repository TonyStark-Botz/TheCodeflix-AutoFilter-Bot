###============================================================###
## Rx Bot — Verification Analytics (/verification command)
## Source: Cinewood Verification.py, Rx branding के साथ
###============================================================###
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.verify_db import vr_db
from info import ADMINS
from datetime import datetime


def _vr_buttons(today, yesterday, this_week, this_month, last_month, this_year, last_year):
    return [
        [InlineKeyboardButton("ᴛᴏᴅᴀʏ", callback_data='vrrfrs#tud'),
         InlineKeyboardButton(f"{today}", callback_data='vrrfrs#tud')],
        [InlineKeyboardButton("ʏᴇsᴛᴇʀᴅᴀʏ", callback_data='vrrfrs#yes'),
         InlineKeyboardButton(f"{yesterday}", callback_data='vrrfrs#yes')],
        [InlineKeyboardButton("ᴛʜɪs ᴡᴇᴇᴋ", callback_data='vrrfrs#week'),
         InlineKeyboardButton(f"{this_week}", callback_data='vrrfrs#week')],
        [InlineKeyboardButton("ᴛʜɪs ᴍᴏɴᴛʜ", callback_data='vrrfrs#mont'),
         InlineKeyboardButton(f"{this_month}", callback_data='vrrfrs#mont')],
        [InlineKeyboardButton("ʟᴀsᴛ ᴍᴏɴᴛʜ", callback_data='vrrfrs#lmont'),
         InlineKeyboardButton(f"{last_month}", callback_data='vrrfrs#lmont')],
        [InlineKeyboardButton("ᴛʜɪs ʏᴇᴀʀ", callback_data='vrrfrs#tyear'),
         InlineKeyboardButton(f"{this_year}", callback_data='vrrfrs#tyear')],
        [InlineKeyboardButton("ʟᴀsᴛ ʏᴇᴀʀ", callback_data='vrrfrs#lyear'),
         InlineKeyboardButton(f"{last_year}", callback_data='vrrfrs#lyear')],
        [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇsʜ", callback_data='vrrfrs#vrrfrs')],
    ]


async def _get_counts():
    today = await vr_db.get_vr_count("today")
    yesterday = await vr_db.get_vr_count("yesterday")
    this_week = await vr_db.get_vr_count("this_week")
    this_month = await vr_db.get_vr_count("this_month")
    last_month = await vr_db.get_vr_count("last_month")
    this_year = await vr_db.get_vr_count("year", year=datetime.now().year)
    last_year = await vr_db.get_vr_count("year", year=datetime.now().year - 1)
    return today, yesterday, this_week, this_month, last_month, this_year, last_year


@Client.on_message(filters.command("verification") & filters.private & filters.user(ADMINS))
async def vrfs(client, message):
    counts = await _get_counts()
    await message.reply_text(
        "✅ **#verification**\n\nTᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴜsᴇʀs",
        reply_markup=InlineKeyboardMarkup(_vr_buttons(*counts)))


@Client.on_callback_query(filters.regex(r"^vrrfrs"))
async def vr_ref(client, query):
    ident, set_type = query.data.split("#")

    alerts = {
        "tud": "verified users from today",
        "yes": "verified users from yesterday",
        "week": "verified users from this week",
        "mont": "verified users from this month",
        "lmont": "verified users from last month",
        "tyear": "verified users from this year",
        "lyear": "verified users from last year",
    }
    if set_type in alerts:
        return await query.answer(alerts[set_type], show_alert=True)

    # Refresh the data
    counts = await _get_counts()
    try:
        await query.message.edit(
            "✅ **#verification**\n\nTᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴜsᴇʀs",
            reply_markup=InlineKeyboardMarkup(_vr_buttons(*counts)))
    except MessageNotModified:
        pass
    await query.answer("Rᴇꜰʀᴇsʜɪɴɢ_ᴅᴀᴛᴀ ✅......")
