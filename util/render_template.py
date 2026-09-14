#Thanks @Lazydeveloperr helping this journey 

import jinja2
from info import *
from lazybot import LazyPrincessBot
from util.human_readable import humanbytes
from util.file_properties import get_file_ids
from util.exceptions import InvalidHash
import urllib.parse
import logging
import aiohttp


async def render_page(id, secure_hash, src=None):
    file = await LazyPrincessBot.get_messages(int(BIN_CHANNEL), int(id))
    file_data = await get_file_ids(LazyPrincessBot, int(BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    file_name = file_data.file_name or f"media-{id}"
    safe_name = urllib.parse.quote_plus(file_name)
    src = f"{URL.rstrip('/')}/{id}/{safe_name}?hash={secure_hash}"

    tag = file_data.mime_type.split("/")[0].strip() if file_data.mime_type else "document"
    file_size = humanbytes(file_data.file_size)
    if tag in ["video", "audio"]:
        template_file = "util/req.html"
    else:
        template_file = "util/dl.html"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(src) as response:
                    content_length = response.headers.get("Content-Length")
                    if content_length and content_length.isdigit():
                        file_size = humanbytes(int(content_length))
        except Exception as exc:
            logging.warning("Failed to fetch content length for %s: %s", id, exc)

    with open(template_file, "r", encoding="utf-8") as template_file_h:
        template = jinja2.Template(template_file_h.read())

    display_name = file_name.replace("_", " ")

    return template.render(
        file_name=display_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
    )
