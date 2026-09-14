###============================================================###
## Rx Bot — Top Search Analytics Database (async)
## Source: Cinewood config_db.py — Rx के लिए सरल $inc + aggregation design
###============================================================###
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI


class TopSearchDB:
    def __init__(self, uri):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client["rx_analytics"]
        self.col = self.db.top_searches

    async def track_search(self, text):
        text = (text or "").strip()
        if not text or text.startswith("/"):
            return
        await self.col.update_one({"text": text}, {"$inc": {"count": 1}}, upsert=True)

    async def get_top_searches(self, limit=30):
        pipeline = [
            {"$group": {"_id": "$text", "count": {"$sum": "$count"}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return await self.col.aggregate(pipeline).to_list(limit)

    async def clear_searches(self):
        await self.col.delete_many({})


ts_db = TopSearchDB(DATABASE_URI)
