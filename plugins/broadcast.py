import datetime, time, asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, RPCError
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Tracks which admin has requested cancellation: {admin_id: True/False}
broadcast_cancel = {}


def cancel_btn():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚫 Cancel Broadcast", callback_data="cancel_broadcast")]]
    )


@Client.on_callback_query(filters.regex("^cancel_broadcast$") & filters.user(ADMINS))
async def cancel_broadcast_cb(bot, query):
    broadcast_cancel[query.from_user.id] = True
    await query.answer("Broadcast cancel ho raha hai... rukiye ⏳", show_alert=True)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    BATCH_SIZE = 100
    SEMAPHORE_LIMIT = 50
    BATCH_DELAY = 2
    admin_id = message.from_user.id

    if not message.reply_to_message:
        return await message.reply_text("⚠️ Broadcast karne ke liye kisi message ko reply karke /broadcast command do.")
    b_msg = message.reply_to_message

    broadcast_cancel[admin_id] = False

    try:
        users = await db.get_all_users()
        sts = await message.reply_text(
            "Broadcasting your messages...",
            reply_markup=cancel_btn()
        )
        start_time = time.time()

        total_users = await db.total_users_count()
        done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

        sem = asyncio.Semaphore(SEMAPHORE_LIMIT)

        async def send_message(user):
            nonlocal success, blocked, deleted, failed, done
            async with sem:
                if "id" not in user:
                    failed += 1
                    done += 1
                    return
                user_id = int(user["id"])
                try:
                    pti, sh = await broadcast_messages(user_id, b_msg)
                    if pti:
                        success += 1
                    elif sh == "Blocked":
                        blocked += 1
                    elif sh == "Deleted":
                        deleted += 1
                    elif sh == "Error":
                        failed += 1
                except Exception as e:
                    print(f"Unexpected error for user {user_id}: {e}")
                    failed += 1
                finally:
                    done += 1

        batch_tasks = []
        batch_count = 0
        cancelled = False

        async for user in users:
            if broadcast_cancel.get(admin_id):
                cancelled = True
                break

            batch_tasks.append(send_message(user))
            batch_count += 1

            if batch_count >= BATCH_SIZE:
                await asyncio.gather(*batch_tasks)
                batch_tasks = []
                batch_count = 0

                if broadcast_cancel.get(admin_id):
                    cancelled = True
                    break

                await sts.edit(
                    f"Broadcast in progress ⌛:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done}/{total_users}\n"
                    f"Success: {success}\n"
                    f"Blocked: {blocked}\n"
                    f"Deleted: {deleted}\n"
                    f"Failed: {failed}",
                    reply_markup=cancel_btn()
                )
                await asyncio.sleep(BATCH_DELAY)

        if batch_tasks and not cancelled:
            await asyncio.gather(*batch_tasks)

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

        if cancelled:
            await sts.edit(
                f"Broadcast Cancelled ❌:\n\n"
                f"Time Taken: {time_taken}\n"
                f"Total Users: {total_users}\n"
                f"Completed: {done}/{total_users}\n"
                f"Success: {success}\n"
                f"Blocked: {blocked}\n"
                f"Deleted: {deleted}\n"
                f"Failed: {failed}"
            )
        else:
            await sts.edit(
                f"Broadcast Completed ✅:\n\n"
                f"Time Taken: {time_taken}\n"
                f"Total Users: {total_users}\n"
                f"Completed: {done}/{total_users}\n"
                f"Success: {success}\n"
                f"Blocked: {blocked}\n"
                f"Deleted: {deleted}\n"
                f"Failed: {failed}"
            )
    except Exception as e:
        print(f"Broadcasting error: {e}")
    finally:
        broadcast_cancel.pop(admin_id, None)


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    admin_id = message.from_user.id

    if not message.reply_to_message:
        return await message.reply_text("⚠️ Broadcast karne ke liye kisi message ko reply karke /grp_broadcast command do.")
    b_msg = message.reply_to_message

    broadcast_cancel[admin_id] = False

    groups = await db.get_all_chats()
    sts = await message.reply_text(
        "Broadcasting your messages To Groups...",
        reply_markup=cancel_btn()
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done, failed, success = 0, 0, 0
    cancelled = False

    async for group in groups:
        if broadcast_cancel.get(admin_id):
            cancelled = True
            break

        pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Error":
            failed += 1
        done += 1

        if not done % 20:
            await sts.edit(
                f"Broadcast in progress ⌛:\n\n"
                f"Total Groups: {total_groups}\n"
                f"Completed: {done}/{total_groups}\n"
                f"Success: {success}\n"
                f"Failed: {failed}",
                reply_markup=cancel_btn()
            )

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    if cancelled:
        await sts.edit(
            f"Broadcast Cancelled ❌:\n\n"
            f"Time Taken: {time_taken}\n"
            f"Total Groups: {total_groups}\n"
            f"Completed: {done}/{total_groups}\n"
            f"Success: {success}\n"
            f"Failed: {failed}"
        )
    else:
        await sts.edit(
            f"Broadcast Completed ✅:\n\n"
            f"Time Taken: {time_taken}\n"
            f"Total Groups: {total_groups}\n"
            f"Completed: {done}/{total_groups}\n"
            f"Success: {success}\n"
            f"Failed: {failed}"
        )

    broadcast_cancel.pop(admin_id, None)
