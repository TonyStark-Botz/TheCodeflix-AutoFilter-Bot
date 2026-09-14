###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###

from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT_LNK
from Script import script
from utils import temp
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message(filters.private & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous. Please use /connect <group_id> in PM")
    try:
        cmd, group_id = message.text.split(" ", 1)
        group_id = int(group_id.strip())
    except:
        await message.reply_text(
            "<b>Enter in correct format!</b>\n\n"
            "<code>/connect groupid</code>\n\n"
            "<i>Get your Group id by adding this bot to your group and use <code>/id</code></i>",
            quote=True
        )
        return

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and userid not in ADMINS
        ):
            await message.reply_text("You should be an admin in the given group!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, make sure I'm present in your group!",
            quote=True,
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title
            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"Successfully connected to **{title}**\nNow manage your group from my PM!",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            else:
                await message.reply_text(
                    "You're already connected to this chat!",
                    quote=True
                )
        else:
            await message.reply_text("Add me as an admin in the group first.", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Some error occurred! Try again later.', quote=True)


@Client.on_message(filters.group & filters.command('connect'))
async def group_connect(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>Anonymous admins cannot use this command.</b>")

    group_id = message.chat.id
    owner_id = await db.get_group_owner(group_id)

    if owner_id is None:
        return await message.reply(
            "<b>⚠️ This group is not registered in our database yet.\n"
            "Please remove and re-add the bot to register it properly.</b>"
        )

    if userid != owner_id:
        return await message.reply(script.NOT_OWNER_MSG)

    # Groups are auto-verified now, just connect user to PM for management
    await add_connection(str(group_id), str(userid))
    await message.reply(script.AUTO_VERIFIED_CONNECT_MSG)


@Client.on_message(filters.private & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous.")

    await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)


@Client.on_message(filters.group & filters.command('disconnect'))
async def deleteconnection_group(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return

    group_id = message.chat.id
    st = await client.get_chat_member(group_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        return

    delcon = await delete_connection(str(userid), str(group_id))
    if delcon:
        await message.reply_text("Successfully disconnected from this chat", quote=True)
    else:
        await message.reply_text("This chat isn't connected to me!\nDo /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title

            # Check verification and disabled status for display label
            is_verified = await db.check_group_verification(int(groupid))
            chat_status = await db.get_chat(int(groupid))
            is_disabled = chat_status.get('is_disabled', False) if chat_status else False

            if is_verified and not is_disabled:
                status_label = " - ✅ ACTIVE"
            else:
                status_label = " - ❌ INACTIVE"

            # Keep if_active for CONNECT/DISCONNECT callback logic
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{status_label}", callback_data=f"opnsetgrp#{groupid}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "Your connected group details:\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )


@Client.on_callback_query(filters.regex(r"^verify_grp:(-?\d+)$"))
async def verify_group_callback(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("⛔ You are not authorized!", show_alert=True)

    group_id = int(callback_query.data.split(":")[1])

    is_already_verified = await db.check_group_verification(group_id)
    if is_already_verified:
        return await callback_query.answer("✅ Group is already verified!", show_alert=True)

    success = await db.verify_group(group_id)
    if not success:
        return await callback_query.answer(
            "❌ Group not found in database. Owner must remove and re-add the bot first.",
            show_alert=True
        )

    owner_id = await db.get_group_owner(group_id)

    try:
        chat_info = await client.get_chat(group_id)
        group_title = chat_info.title
    except:
        group_title = str(group_id)

    if owner_id:
        await add_connection(str(group_id), str(owner_id))
        try:
            await client.send_message(
                chat_id=owner_id,
                text=script.GROUP_VERIFIED_PM_MSG.format(group_title, group_id)
            )
        except Exception as e:
            logger.warning(f"Could not send verified PM to owner {owner_id}: {e}")

    await callback_query.answer("✅ Group verified successfully!", show_alert=True)
    await callback_query.message.edit_text(
        callback_query.message.text + "\n\n<b>✅ VERIFIED</b>"
    )


@Client.on_callback_query(filters.regex(r"^disable_grp:(-?\d+)$"))
async def disable_group_callback(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("⛔ You are not authorized!", show_alert=True)

    group_id = int(callback_query.data.split(":")[1])

    cha_t = await db.get_chat(group_id)
    if cha_t and cha_t.get('is_disabled'):
        return await callback_query.answer("❎ Group is already disabled!", show_alert=True)

    reason = "Disabled via verification review"
    await db.disable_chat(group_id, reason)

    if group_id not in temp.BANNED_CHATS:
        temp.BANNED_CHATS.append(group_id)

    try:
        group_title = (await client.get_chat(group_id)).title
    except:
        group_title = str(group_id)

    try:
        buttons = [[InlineKeyboardButton('Support', url=SUPPORT_CHAT_LNK)]]
        await client.send_message(
            chat_id=group_id,
            text=f'<b>Hello Friends,\nMy admin has decided not to allow this bot in this group. '
                 f'If you want to know more, contact our support group.</b>\n'
                 f'Reason: <code>{reason}</code>',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await client.leave_chat(group_id)
    except Exception as e:
        logger.warning(f"Could not send message or leave group {group_id}: {e}")

    await callback_query.answer("❎ Group disabled and bot left!", show_alert=True)
    
    # Edit the original message to show disabled status - replace ANY status with disabled
    try:
        from pyrogram import enums as pyrogram_enums
        # Use .text.html to get the HTML-formatted text with tags intact
        original_html = callback_query.message.text.html
        lines = original_html.split('\n')
        found = False
        for i, line in enumerate(lines):
            if '⚡' in line and 'Status' in line:
                lines[i] = "⚡ <b>Status  :</b> #Group_Disabled ⭕"
                found = True
                break
        
        if found:
            updated_text = '\n'.join(lines)
            await callback_query.message.edit_text(updated_text, parse_mode=pyrogram_enums.ParseMode.HTML, disable_web_page_preview=True)
            logger.info(f"✅ Group {group_id} status updated to disabled")
        else:
            logger.warning(f"⚠️ Status line not found in message for group {group_id}")
    except Exception as e:
        logger.error(f"❌ Failed to edit message for group {group_id}: {e}")

###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###
