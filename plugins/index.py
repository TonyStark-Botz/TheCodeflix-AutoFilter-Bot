import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()
semaphore = asyncio.Semaphore(60)  # Limit concurrent tasks
pending_index_requests = {}
active_index_request = None


def skip_summary(skip):
    return f"0-{skip - 1}" if skip else "none"


async def ask_for_skip(message, request):
    pending_index_requests[request["requester_id"]] = request
    await message.reply_text(
        "<b>How many messages should be skipped before indexing?</b>\n\n"
        "Send a number, or send <code>0</code> to skip nothing."
    )


async def show_index_confirmation(message, request):
    skip = request["skip"]
    text = (
        "<b>Confirm file indexing</b>\n\n"
        f"Chat ID: <code>{request['chat_id']}</code>\n"
        f"Source username: @{request['chat_username']}\n"
        f"Requested by: @{request['requester_username']}\n"
        f"Last message ID: <code>{request['last_msg_id']}</code>\n"
        f"Skipped message IDs: <code>{skip_summary(skip)}</code>\n"
        f"Skip count: <code>{skip}</code>"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"indexconfirm#{request['requester_id']}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"indexcancel#{request['requester_id']}")],
    ])
    await message.reply_text(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    if query.data.startswith('indexconfirm#'):
        requester_id = int(query.data.split('#', 1)[1])
        if query.from_user.id != requester_id and query.from_user.id not in ADMINS:
            return await query.answer("You are not allowed to confirm this request.", show_alert=True)
        request = pending_index_requests.get(requester_id)
        if not request:
            return await query.answer("This indexing request has expired.", show_alert=True)
        if lock.locked():
            return await query.answer('Wait until previous process complete.', show_alert=True)
        pending_index_requests.pop(requester_id, None)
        global active_index_request
        active_index_request = requester_id
        await query.answer('Indexing started.')
        await query.message.edit(
            "Starting Indexing",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
        )
        await index_files_to_db(request["last_msg_id"], request["chat_id"], query.message, bot, request["skip"])
        active_index_request = None
        return
    if query.data.startswith('indexcancel#'):
        requester_id = int(query.data.split('#', 1)[1])
        if query.from_user.id != requester_id and query.from_user.id not in ADMINS:
            return await query.answer("You are not allowed to cancel this request.", show_alert=True)
        pending_index_requests.pop(requester_id, None)
        await query.answer('Indexing cancelled.')
        await query.message.edit('Indexing cancelled.')
        return
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if query.from_user.id not in ADMINS:
        return await query.answer("Only admins can approve indexing requests.", show_alert=True)
    if raju == 'reject':
        pending_index_requests.pop(int(from_user), None)
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been declined by our moderators.',
                               reply_to_message_id=int(lst_msg_id))
        return

    request = pending_index_requests.get(int(from_user))
    if not request:
        return await query.answer('This indexing request has expired.', show_alert=True)
    await query.answer('Accepted. Asking for skip number.')
    await bot.send_message(
        int(from_user),
        "<b>Your indexing request was accepted.</b>\n\n"
        "How many messages should be skipped before indexing?\n"
        "Send a number, or send <code>0</code> to skip nothing."
    )


@Client.on_message(filters.private & filters.text & filters.incoming)
async def receive_index_skip(bot, message):
    pending = pending_index_requests.get(message.from_user.id)
    if not pending or not pending.get("awaiting_skip"):
        return
    try:
        skip = int(message.text.strip())
        if skip < 0:
            raise ValueError
    except (ValueError, AttributeError):
        return await message.reply_text("Send a non-negative number, or send <code>0</code> to skip nothing.")
    pending["skip"] = skip
    pending["awaiting_skip"] = False
    await show_index_confirmation(message, pending)


@Client.on_message((filters.forwarded | (filters.regex(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming)
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        chat_info = await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That I am An Admin In The Channel, if channel is private')
    if k.empty:
        return await message.reply('This may be a group and I am not an admin of the group.')

    request = {
        "chat_id": chat_id,
        "last_msg_id": last_msg_id,
        "requester_id": message.from_user.id,
        "requester_username": message.from_user.username or "No username",
        "chat_username": getattr(chat_info, "username", None) or "No username",
        "skip": 0,
        "awaiting_skip": True,
    }
    if message.from_user.id in ADMINS:
        return await ask_for_skip(message, request)

    if type(chat_id) is int:
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('Make sure I am an admin in the chat and have permission to invite users.')
    else:
        link = f"@{message.forward_from_chat.username}"
    buttons = [
        [
            InlineKeyboardButton('Accept Index',
                                 callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')
        ],
        [
            InlineKeyboardButton('Reject Index',
                                 callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(LOG_CHANNEL,
                           f'#IndexRequest\n\nBy : {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/Username: <code> {chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\nInviteLink: {link}',
                           reply_markup=reply_markup)
    await message.reply('Thank you for the contribution. Wait for my moderators to verify the files.')


async def index_files_to_db(lst_msg_id, chat, msg, bot, skip):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = skip
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, skip):
                if temp.CANCEL:
                    await msg.edit(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code> (Unsupported Media - `{unsupported}`)\nErrors Occurred: <code>{errors}</code>")
                    break
                current += 1
                if current % 150 == 0:
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    try:
                        await msg.edit_text(
                            text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code> (Unsupported Media - `{unsupported}`)\nErrors Occurred: <code>{errors}</code>",
                            reply_markup=reply)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.AUDIO, enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:  # Excluding videos
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                async with semaphore:  # Limiting concurrent tasks
                    aynav, vnay = await save_file(media)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(f'Succesfully saved <code>{total_files}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')
            
