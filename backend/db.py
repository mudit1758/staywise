"""
MongoDB connection. Uses PyMongo's synchronous client -- FastAPI runs
regular ``def`` route handlers in a worker thread pool automatically,
so blocking PyMongo calls do not block the event loop.
"""
from __future__ import annotations

from pymongo import ASCENDING, MongoClient
from pymongo.server_api import ServerApi

from config import DB_NAME, MONGO_URI

# `server_api` is harmless for a local/self-hosted MongoDB and is required
# by MongoDB Atlas connection strings that request the stable API.
client = MongoClient(MONGO_URI, server_api=ServerApi("1")) if "mongodb+srv" in MONGO_URI else MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
hotels_col = db["hotels"]
bookings_col = db["bookings"]


def init_indexes() -> None:
    users_col.create_index("email", unique=True)
    hotels_col.create_index("ownerId")
    hotels_col.create_index([("city", ASCENDING)])
    bookings_col.create_index("userId")
    bookings_col.create_index("hotelId")
    bookings_col.create_index([("roomId", ASCENDING), ("checkIn", ASCENDING), ("checkOut", ASCENDING)])
    bookings_col.create_index("razorpayOrderId")


def check_connection() -> bool:
    """Used at startup to fail fast with a clear message if Mongo is unreachable."""
    client.admin.command("ping")
    return True
