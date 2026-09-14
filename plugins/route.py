###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###

from aiohttp import web
import re
import math
import logging
import secrets
import time
import mimetypes
from urllib.parse import quote
from aiohttp.http_exceptions import BadStatusLine
from lazybot import multi_clients, work_loads, LazyPrincessBot
from util.exceptions import FIleNotFound, InvalidHash
from util import StartTime, __version__
from util.custom_dl import ByteStreamer
from util.time_format import get_readable_time
from util.render_template import render_page
from info import *


routes = web.RouteTableDef()


def parse_stream_path(path, request):
    match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
    if match:
        return int(match.group(2)), match.group(1)

    id_match = re.search(r"(\d+)(?:/\S+)?", path)
    secure_hash = request.rel_url.query.get("hash")
    if not id_match or not secure_hash:
        raise web.HTTPBadRequest(text="Invalid streaming URL")
    return int(id_match.group(1)), secure_hash

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("BenFilterBot")


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        id, secure_hash = parse_stream_path(path, request)
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError) as e:
        logging.error(f"Error in stream_handler: {e}")
        raise web.HTTPInternalServerError(text=str(e))
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        id, secure_hash = parse_stream_path(path, request)
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError) as e:
        logging.error(f"Error in media stream_handler: {e}")
        raise web.HTTPInternalServerError(text=str(e))
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range")
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if len(multi_clients) > 1:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        range_match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
        if not range_match or (not range_match.group(1) and not range_match.group(2)):
            return web.Response(
                status=416,
                text="416: Range not satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        range_start, range_end = range_match.groups()
        if range_start:
            from_bytes = int(range_start)
            until_bytes = int(range_end) if range_end else file_size - 1
        else:
            suffix_length = int(range_end)
            from_bytes = max(file_size - suffix_length, 0)
            until_bytes = file_size - 1
    else:
        from_bytes = 0
        until_bytes = file_size - 1

    if (
        file_size <= 0
        or from_bytes < 0
        or from_bytes >= file_size
        or until_bytes < from_bytes
    ):
        return web.Response(
            status=416,
            text="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = ((until_bytes - offset) // chunk_size) + 1
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_name)[0]
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    mime_type = mime_type or "application/octet-stream"
    headers = {
        "Content-Type": mime_type,
        "Content-Length": str(req_length),
        "Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(file_name)}",
        "Accept-Ranges": "bytes",
    }
    if range_header:
        headers["Content-Range"] = f"bytes {from_bytes}-{until_bytes}/{file_size}"

    response = web.StreamResponse(
        status=206 if range_header else 200,
        headers=headers,
    )
    await response.prepare(request)
    try:
        async for chunk in body:
            await response.write(chunk)
    finally:
        await response.write_eof()
    return response

