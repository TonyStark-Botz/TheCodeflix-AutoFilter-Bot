###============================================================###
## Rx Bot — Redeem / Gift Codes (MongoDB persist)
## Source: Cinewood Deendayal/Redeem.py — in-memory dict की जगह MongoDB
###============================================================###
from datetime import timedelta, datetime
import string
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS, PREMIUM_LOGS
from utils import get_seconds, temp


def generate_code(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


@Client.on_message(filters.command("addgiftcode") & filters.user(ADMINS))
async def add_redeem_code(client, message):
    if len(message.command) == 3:
        try:
            time_str = message.command[1]
            num_codes = int(message.command[2])
        except ValueError:
            await message.reply_text("Please provide a valid number of codes to generate.")
            return

        codes = []
        for _ in range(num_codes):
            code = generate_code()
            await db.add_redeem_code(code, time_str)  # MongoDB persist (restart-proof)
            codes.append(code)

        codes_text = '\n'.join(f"➔ <code>/redeem {code}</code>" for code in codes)
        text = f"""
<b>🎉 <u>Rx Gɪꜰᴛᴄᴏᴅᴇ Gᴇɴᴇʀᴀᴛᴇᴅ ✅</u></b>

<b> <u>Tᴏᴛᴀʟ ᴄᴏᴅᴇ:</u></b> {num_codes}

{codes_text}

<b>⏳ <u>Duration:</u></b> {time_str}

🌟<u>𝗥𝗲𝗱𝗲𝗲𝗺 𝗖𝗼𝗱𝗲 𝗜𝗻𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻</u>🌟

<b> <u>Click on the code above</u> to copy it instantly!</b>
<b> <u>Send the copied code to the bot</u>\n to unlock your premium features!</b>

<b>🚀 Enjoy your premium access! 🔥</b>
"""
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔑 Redeem Now 🔥", url=f"https://t.me/{temp.U_NAME}")]])
        await message.reply_text(text, reply_markup=keyboard)
    else:
        await message.reply_text("<b>♻ Usage:\n\n➩ <code>/addgiftcode 1min 1</code>,\n➩ <code>/addgiftcode 1hour 10</code>,\n➩ <code>/addgiftcode 1day 5</code></b>")


@Client.on_message(filters.command("redeem"))
async def redeem_code(client, message):
    user_id = message.from_user.id
    if len(message.command) == 2:
        code = message.command[1]
        data = await db.get_redeem_code(code)

        if data:
            time_str = data.get("time")
            try:
                user = await client.get_users(user_id)
                seconds = await get_seconds(time_str)
                if seconds <= 0:
                    await message.reply_text("Invalid time format in redeem code.")
                    return

                user_data = await db.get_user(user_id)
                current_expiry = user_data.get("expiry_time") if user_data else None
                now = datetime.now()

                if current_expiry and current_expiry > now:
                    expiry_str_in_ist = current_expiry.strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")
                    await message.reply_text(
                        f"🚫 <b>Yᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ!</b>\n\n"
                        f"⏳ <b>Cᴜʀʀᴇɴᴛ Pʀᴇᴍɪᴜᴍ Exᴘɪʀʏ:</b> {expiry_str_in_ist}\n\n"
                        f"<i>Yᴏᴜ ᴄᴀɴɴᴏᴛ ʀᴇᴅᴇᴇᴍ ᴀɴᴏᴛʜᴇʀ ᴄᴏᴅᴇ ᴜɴᴛɪʟ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴇxᴘɪʀᴇs.</i>",
                        disable_web_page_preview=True)
                    return

                expiry_time = now + timedelta(seconds=seconds)
                await db.update_user({"id": user_id, "expiry_time": expiry_time})
                await db.mark_redeem_code_used(code)  # code one-time use

                expiry_str_in_ist = expiry_time.strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")
                await message.reply_text(
                    f"🎉 <b>ɴᴏᴡ ꜰᴇᴇʟ ᴘʀᴏᴜᴅ ᴏꜰ ʏᴏᴜʀꜱᴇʟꜰ 😎 ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴀɴ Rx ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ 😉</b>\n\n"
                    f"😎 <b>User:</b> {user.mention}\n"
                    f"⚡ <b>User ID:</b> <code>{user_id}</code>\n"
                    f"⏳ <b>Premium Access Duration:</b> <code>{time_str}</code>\n"
                    f"⌛️ <b>Expiry Date:</b> {expiry_str_in_ist}",
                    disable_web_page_preview=True)
                await client.send_message(
                    PREMIUM_LOGS,
                    text=f"#Redeem_Premium 🔓\n\n"
                         f"😎 <b>User:</b> {user.mention}\n"
                         f"⚡ <b>User ID:</b> <code>{user_id}</code>\n"
                         f"⏳ <b>Duration:</b> <code>{time_str}</code>\n"
                         f"⌛️ <b>Expiry Date:</b> {expiry_str_in_ist}",
                    disable_web_page_preview=True)
            except Exception as e:
                await message.reply_text(f"An error occurred while redeeming the code: {e}")
        else:
            await message.reply_text("Invalid Redeem Code or Expired.")
    else:
        await message.reply_text("Usage: <code>/redeem CODE</code>")
