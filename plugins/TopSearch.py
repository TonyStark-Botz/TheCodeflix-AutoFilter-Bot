###============================================================###
## Rx Bot — Top Search Analytics (/topsearch, /clearsearch — OWNERID only)
###============================================================###
from pyrogram import Client, filters
from database.config_db import ts_db
from info import OWNERID


@Client.on_message(filters.command("topsearch") & filters.user(OWNERID))
async def top_search(client, message):
    msg = await message.reply_text("<i>📊 Fetching top searches...</i>")
    try:
        results = await ts_db.get_top_searches(limit=30)
        if not results:
            return await msg.edit_text("अभी तक कोई search track नहीं हुई।")
        lines = ["🏆 <b>𝐓𝐎𝐏 𝟑𝟎 𝐒𝐄𝐀𝐑𝐂𝐇𝐄𝐒</b>\n"]
        for i, r in enumerate(results, 1):
            text = r.get("_id", "?")
            count = r.get("count", 0)
            lines.append(f"<b>{i:>2}.</b> {text} <code>({count})</code>")
        lines.append("\n♻ <code>/clearsearch</code> से data reset करें।")
        await msg.edit_text("\n".join(lines), disable_web_page_preview=True)
    except Exception as e:
        await msg.edit_text(f"Error: {e}")


@Client.on_message(filters.command("clearsearch") & filters.user(OWNERID))
async def clear_search(client, message):
    await ts_db.clear_searches()
    await message.reply_text("✅ <b>Top search analytics cleared.</b>")
