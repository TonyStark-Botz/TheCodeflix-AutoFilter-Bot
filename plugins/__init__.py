###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###

import asyncio
import logging
from datetime import datetime
from aiohttp import web
from .route import routes
from database.users_chats_db import db
from info import PREMIUM_LOGS

logger = logging.getLogger(__name__)


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app


async def check_expired_premium(bot):
    """Rx Premium — expired premium access हर 60s में check करके remove करता है."""
    while True:
        await asyncio.sleep(60)
        try:
            expired = await db.get_expired(datetime.now())
            for user in expired:
                user_id = user["id"]
                await db.remove_premium_access(user_id)
                try:
                    u = await bot.get_users(user_id)
                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=f"<b><i>Hᴇʏ Tʜᴇʀᴇ 𓆩♡𓆪 {u.mention} 👀 👋</i>\n\n<u>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ᴇxᴘɪʀᴇᴅ ❗\nᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇ.</u>\n\n🎁 ɢᴇᴛ 𝟭𝟬% ᴏғғ ᴏɴ ʏᴏᴜʀ ɴᴇxᴛ ᴘʀᴇᴍɪᴜᴍ ᴘᴜʀᴄʜᴀsᴇ ᴡʜᴇɴ ʏᴏᴜ ʀᴇɴᴇᴡ ᴡɪᴛʜɪɴ 𝟭 ᴅᴀʏ (𝟮𝟰 ʜᴏᴜʀs).\n\nɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛᴀᴋᴇ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ /plans ꜰᴏʀ ᴛʜᴇ ᴅᴇᴛᴀɪʟs ᴏꜰ ᴛʜᴇ ᴘʟᴀɴs.</b>")
                    except Exception:
                        pass
                    await bot.send_message(
                        PREMIUM_LOGS,
                        text=f"<b>#PREMIUM_EXPIRED\n\nUsᴇʀ : {u.mention}\nUsᴇʀ Iᴅ : <code>{user_id}</code></b>")
                except Exception:
                    pass
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.exception("check_expired_premium error: %s", e)
