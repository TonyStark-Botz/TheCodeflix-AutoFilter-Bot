
import logging
import asyncio
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI2, DATABASE_NAME2, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI2)
db = client[DATABASE_NAME2]
instance = Instance.from_db(db)


async def get_db_size():
    stats = await db.command("dbstats")
    size_in_bytes = stats["dataSize"]
    return size_in_bytes


languages = [" Hin ", "Hindi", "हिन्दी", " Eng ", "English", " Tam ", "Tamil", "தமிழ்", " Tel ", "తెలుగు", "Telugu", " Mal ", "മലയാളം", "Malayalam", " Kan ", "ಕನ್ನಡ", "Kannada", " Guj ", "ગુજરાતી", "Gujrati", " Mar ", "मराठी", "Marathi", "Beng", "বাংলা", "Bangla", "Bengali", "Korean", "Japanese", "Chinese", "Punjabi", "Odia", "Assamese", "Bhojpuri", "Spanish", "French", "German", "Russian", "Portuguese", "Arabic", "Fan dub", "Hindi Clean"]


# List of video qualities — 240p and 360p excluded (not indexed)
qualities = ["480p", "576p", "720p", "900p", "1080p", "1440p",
             "2160p", "2880p", "3072p", "4320p", "5760p", "8640p"]

# Dictionary to map short names to full names
language_map = {
    " Hin ": "Hindi",
    "Hindi": "Hindi",
    "हिन्दी": "Hindi",
    " Eng ": "English",
    "English": "English",
    " Tam ": "Tamil",
    "Tamil": "Tamil",
    "தமிழ்": "Tamil",
    " Tel ": "Telugu",
    "తెలుగు": "Telugu",
    "Telugu": "Telugu",
    " Mal ": "Malayalam",
    "മലയാളം": "Malayalam",
    "Malayalam": "Malayalam",
    " Kan ": "Kannada",
    "ಕನ್ನಡ": "Kannada",
    "Kannada": "Kannada",
    " Guj ": "Gujrati",
    "ગુજરાતી": "Gujrati",
    "Gujrati": "Gujrati",
    " Mar ": "Marathi",
    "मराठी": "Marathi",
    "Marathi": "Marathi",
    "Beng": "Bengali",
    "বাংলা": "Bengali",
    "Bangla": "Bengali",
    "Bengali": "Bengali",
    "Korean": "Korean",
    " Jap ": "Japanese",
}

# Pre-compiled blacklist regex — split across lines to avoid tool truncation
_BLACKLIST_RE = re.compile(
    r"(mkv|movies|movie|x264| piro |x265|Kbps|mwkOTT|AAC|SMM|x264-PAHE"
    r"|mp4|MP4|MP3|Mp4|telegram|Bollywood|Hollywood|Tollywood|Download"
    r"|subtitles|film|dubbed|latest|ClipmateMovies|mkvCinemas|PrimeFix"
    r"|www_SkymoviesHD_email|www|Latest_Movies_Reborn|Netflix_Villa_Original"
    r"|FilmOne_Movies|Miteshpatelnewmovies|MoviesClubXyz|Skymovies"
    r"|File_Movies_Uploaded|Tg-@New_Movies_OnTG|Tg_@New_Movies_OnTG"
    r"|Moonknight_media|Bob_files|Desire|CineVood|Bisal|Miteshpatelnew"
    r"|Mallu_Movies|TheMoviesBoss|cineasteseries|Links|Mallu"
    r"|@MR_Linkz|Linkz|@Sons_of_TamilRockers|@VideoMemesTamil|@TM_LMO"
    r"|@Vip_LinkzZ|@Tamil_LinkzZ|@mwkOTT|@C_V|@Mallu_Movies"
    r"|TamilRockers|Tamilblasters|@lubokvideo|@NithinMovies|Linkzz|Bolly4u"
    r"|Jesseverse|TeamSeries|@Mj_Linkz|@SY_MS|@ulluweb_Series|@Einthusan"
    r"|@RayFilms4U|@IMDbFilms4U|@HindiOldMovies|@HollywoodBay|@hdhindicinemas"
    r"|@Hollywood_WebHub|MoviesVerse|A2MOVIES|@CE_LinkS|@mallukingz"
    r"|@MEDIA_KING|@MoviePlayTk|@MOVIEHUNT|@E4E_ROCKERS|@MOVIEZMOB"
    r"|@pluscinemas|@QualityCinemaZ|@universalpicturez|@uteam|TamilMV"
    r"|@mfmixhindi|@mwkseries|@FBM|@vivimaxx|@IM|@Cinemagramz"
    r"|Toonsouthindia|POPCORN_FILMS|@UCParadiso|@ensembly|@nkmhdpro1"
    r"|worldfree4|@bb_movie|@Links2U|@QualiStuff|@Hindi_UltraHD_Movies"
    r"|@Moviesmasaaly|@KannadaWarriors|@Mxoriginals|@udanpadam|@Star_rockers"
    r"|@Ml_Movies|@SimplyCinema|www_TamilBlasters_uk|@khatrimaza|@MCArchives"
    r"|@Movieslkwww|@HindiHDCinemaa|Filmy4wap_xyz|@InfotainmentMedia2"
    r"|FILMCOMPANY|@CinematicsUnited|@ALBCINEMASALL|@Kande76|@MKMovieking"
    r"|@SoumenBot|@FrediesChannel|@MMXE|@Massmoviess|@popcorn_cinemas"
    r"|@tamilrockers_in|@TROFFICIAL|@Bollywoodcinemas|@desimovies_TelegramHindi"
    r"|@CC_Series|KatmovieHD|@geniehd|@HindiRockers|@CelluloidCineClub"
    r"|@Mlwapcinemas|@kickass_torrents|@fullyfilmie|@paravamedia|@southindianm"
    r"|@H265_Movies|@t_m_Golmaal|Downloadhub\.us|mobile_mm|TbestMovies4"
    r"|movieworldkdY|Akatsuki_Media|Tvserieshome|@WMR_Terminator"
    r"|@HindiHDMovies_Netflix|@desimovies|@RickyChannel)",
    flags=re.IGNORECASE
)


@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


async def save_file(media):
    """Save file in database"""

    # Extracting necessary fields
    file_id, file_ref = unpack_new_file_id(media.file_id)

    # Initial cleaning of file_name
    file_name = str(media.file_name)

    # Remove blacklist words and patterns
    file_name = _BLACKLIST_RE.sub('', file_name)
    file_name = re.sub(r'@[\w]+|[._\(\)\[\]]', ' ', file_name)
    file_name = re.sub(r"'", '', file_name)
    file_name = re.sub(r'\s+', ' ', file_name).strip()

    # Initialize sets to store found languages and qualities
    found_languages = set()
    found_qualities = set()

    # Clean up file_name from unnecessary characters and spaces initially
    file_name = re.sub(r'[@._\(\)\[\]+\s]+', ' ', file_name)
    file_name += ' '

    # Process the caption if it exists
    if media.caption:
        caption_text = media.caption
        caption_text = re.sub(r'@[\w]+|[._\(\)\[\]]', ' ', caption_text, flags=re.IGNORECASE)
        caption_text = re.sub(r't\.me/\w+', ' ', caption_text, flags=re.IGNORECASE)
        caption_text = re.sub(r'(http[s]?://\S+|www\.\S+)', ' ', caption_text, flags=re.IGNORECASE)
        caption_text = re.sub(r'\s+', ' ', caption_text).strip()
        caption_text += ' '
    else:
        caption_text = None

    # Search and extract languages from caption text and file name
    for lang in languages:
        if (caption_text and re.search(re.escape(lang), caption_text, flags=re.IGNORECASE)) or \
           re.search(re.escape(lang), file_name, flags=re.IGNORECASE):
            full_name = language_map.get(lang, lang)
            found_languages.add(full_name)
            file_name = re.sub(re.escape(lang), ' ', file_name, flags=re.IGNORECASE).strip()
            file_name = re.sub(re.escape(full_name), ' ', file_name, flags=re.IGNORECASE).strip()

    # Search and extract qualities from caption text and file name
    for quality in qualities:
        if (caption_text and re.search(re.escape(quality), caption_text, flags=re.IGNORECASE)) or \
           re.search(re.escape(quality), file_name, flags=re.IGNORECASE):
            found_qualities.add(quality)
            file_name = re.sub(re.escape(quality), ' ', file_name, flags=re.IGNORECASE).strip()

    # Clean up any extra spaces in the file name
    file_name = re.sub(r'\s+', ' ', file_name).strip()

    # Append found languages to the file_name
    if found_languages:
        file_name += " ll "
        file_name += "🔊 :- " + ', '.join(found_languages)

    # Append found qualities to the file_name
    if found_qualities:
        file_name += " ll "
        file_name += "📽️ :- " + ', '.join(found_qualities)

    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name if media.file_name else caption_text,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        print(f"🚫Error occurred while saving file in database :- {file_name}")
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(f'{getattr(media, "file_name", "NO_FILE")} is already saved in database')
            print(f"Found Duplicate❌ File :- {file_name}")
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            print(f"File Saved✅ to Database :- {file_name}")
            return True, 1


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset) — count and fetch run in parallel."""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    # Build cursor first (sync), then run count + fetch in parallel
    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)

    total_results, files = await asyncio.gather(
        Media.count_documents(filter),
        cursor.to_list(length=max_results)
    )

    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''

    return files, next_offset, total_results


async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, total) — count and fetch run in parallel."""
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    files = await cursor.to_list(length=total_results)

    return files, total_results


async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
