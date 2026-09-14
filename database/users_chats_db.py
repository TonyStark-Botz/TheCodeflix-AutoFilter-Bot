###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###

import re
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio
from info import DATABASE_NAME, CUSTOM_FILE_CAPTION, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, IS_SHORTLINK, TUTORIAL, IS_TUTORIAL, PM_SEARCH
import datetime
import pytz
import time


# Async motor client for referral system (no more blocking sync calls)
_referal_client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
_referal_db = _referal_client["referal_user"]

async def referal_add_user(user_id, ref_user_id):
    user_col = _referal_db[str(user_id)]
    user = {'_id': ref_user_id}
    try:
        await user_col.insert_one(user)
        return True
    except DuplicateKeyError:
        return False


async def get_referal_all_users(user_id):
    user_col = _referal_db[str(user_id)]
    return user_col.find()

async def get_referal_users_count(user_id):
    user_col = _referal_db[str(user_id)]
    count = await user_col.count_documents({})
    return count


async def delete_all_referal_users(user_id):
    user_col = _referal_db[str(user_id)]
    await user_col.delete_many({})

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.join_request = self.db.join_requests

    async def add_join_request(self, user_id, chat_id):
        join_request_data = {
            "user_id": user_id,
            "chat_id": chat_id
        }

        await self.join_request.insert_one(join_request_data)

    async def check_join_request(self, user_id, chat_id):
        result = await self.join_request.find_one({"user_id": user_id, "chat_id": chat_id}) 
        if result:
            return True
        else:
            return False

    async def delete_all_join_requests(self):
        result = await self.join_request.delete_many({})


    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )


    def new_group(self, id, title, owner_id=None):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
            is_verified=False,
            owner_id=owner_id,
            verified_date=None,
        )

    
    async def update_verification(self, id, date, time):
        status = {
            'date': str(date),
            'time': str(time)
        }
        await self.col.update_one({'id': int(id)}, {'$set': {'verification_status': status}})

    async def get_verified(self, id):
        default = {
            'date': "1999-12-31",
            'time': "23:59:59"
        }
        user = await self.col.find_one({'id': int(id)})
        if user:
            return user.get("verification_status", default)
        return default
    
    
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    


    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def add_group_with_owner(self, group_id, group_title, owner_id):
        try:
            group = self.new_group(group_id, group_title, owner_id=owner_id)
            await self.grp.insert_one(group)
            return True
        except DuplicateKeyError:
            return False

    async def verify_group(self, group_id):
        try:
            result = await self.grp.update_one(
                {'id': int(group_id)},
                {'$set': {'is_verified': True, 'verified_date': datetime.datetime.now()}}
            )
            return result.matched_count > 0
        except Exception:
            return False

    async def check_group_verification(self, group_id):
        chat = await self.grp.find_one({'id': int(group_id)})
        if chat:
            return chat.get('is_verified', False)
        return False

    async def get_group_owner(self, group_id):
        chat = await self.grp.find_one({'id': int(group_id)})
        if chat:
            return chat.get('owner_id', None)
        return None

    async def update_group_owner(self, group_id, owner_id):
        await self.grp.update_one(
            {'id': int(group_id)},
            {'$set': {'owner_id': owner_id}}
        )

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
    

    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'caption': CUSTOM_FILE_CAPTION,
            'shortlink': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': IS_SHORTLINK,
            'tutorial': TUTORIAL,
            'is_tutorial': IS_TUTORIAL            
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default
    

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    

    async def get_all_chats(self):
        return self.grp.find({})


    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']
        
    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False

    async def update_one(self, filter_query, update_data):
        try:
            result = await self.users.update_one(filter_query, update_data)
            return result.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    async def get_expired(self, current_time):
        expired_users = []
        if data := self.users.find({"expiry_time": {"$ne": None, "$lt": current_time}}):
            async for user in data:
                expired_users.append(user)
        return expired_users

    async def remove_premium_access(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )

    async def check_trial_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            return user_data.get("has_free_trial", False)
        return False

    async def give_free_trial(self, user_id):
        user_id = user_id
        seconds = 5*60         
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": user_id}, {"$set": user_data}, upsert=True)    
    
    async def check_remaining_uasge(self, userid):
        user_id = userid
        user_data = await self.get_user(user_id)        
        expiry_time = user_data.get("expiry_time")
        remaining_time = expiry_time - datetime.datetime.now()
        return remaining_time


    async def pm_search_status(self):
        config = await self.db.pm_search.find_one({'_id': 'status'})
        if config is not None:
            return bool(config.get('status', PM_SEARCH))
        return PM_SEARCH

    async def update_pm_search_status(self, status):
        await self.db.pm_search.update_one(
            {'_id': 'status'},
            {'$set': {'status': bool(status)}},
            upsert=True
        )

    async def add_redeem_code(self, code, time_str):
        await self.db.redeem_codes.insert_one({"code": code, "time": time_str, "used": False})

    async def get_redeem_code(self, code):
        return await self.db.redeem_codes.find_one({"code": code, "used": False})

    async def mark_redeem_code_used(self, code):
        await self.db.redeem_codes.update_one({"code": code}, {"$set": {"used": True}})

    async def all_premium_users(self):
        count = await self.users.count_documents({
        "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count
        


db = Database(DATABASE_URI, DATABASE_NAME)

###============================================================###
## 𝑮𝒊𝒕𝑯𝒖𝒃: https://github.com/TheCodeflix
## 𝑻𝒉𝒆 𝑪𝒐𝒅𝒆𝒇𝒍𝒊𝒙 𝑻𝑮: https://t.me/TheCodeflix
## 𝑻𝑮 𝑨𝒅𝒖𝒍𝒕 𝑪𝒐𝒎𝒎𝒖𝒏𝒊𝒕𝒚: https://t.me/MyStudy_Hub
## 𝑨𝒍𝒍 𝑻𝑮 𝑩𝒐𝒕'𝒔 𝑼𝒑𝒅𝒂𝒕𝒆𝒔: https://t.me/LiveCraftBots
###============================================================###
