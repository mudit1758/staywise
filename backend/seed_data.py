"""
Populates MongoDB with demo accounts and demo hotels so the app is usable
immediately after `pip install` + `npm install`, with no manual data entry.

Run directly to (re)seed on demand:

    python seed_data.py

It is also called automatically on API startup when the `hotels`
collection is empty, so a first-time `uvicorn main:app` already has data.
"""
from __future__ import annotations

from typing import Any

from db import bookings_col, hotels_col, init_indexes, users_col
from security import make_id, password_hash


def photo(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&q=85"


def _demo_users() -> list[dict[str, Any]]:
    return [
        {"_id": "user-demo-guest", "name": "Aarav Mehta", "email": "guest@staywise.test", "phone": "+91 98765 43210", "role": "guest", "passwordHash": password_hash("demo1234")},
        {"_id": "user-demo-owner", "name": "Maya Kapoor", "email": "owner@staywise.test", "phone": "+91 98765 12345", "role": "owner", "passwordHash": password_hash("demo1234")},
    ]


def _demo_hotels() -> list[dict[str, Any]]:
    return [
        {
            "_id": "hotel-amber-house", "ownerId": "user-demo-owner", "name": "Amber House",
            "propertyType": "Boutique hotel", "description": "A sunlit hideaway where old-world character meets easy, modern comfort. Walk to the riverfront, then return to a quiet courtyard and thoughtful service.",
            "city": "Jaipur", "country": "India", "address": "12 Civil Lines, Jaipur, Rajasthan 302006",
            "image": photo("photo-1564501049412-61c2a3083791"),
            "images": [photo("photo-1564501049412-61c2a3083791"), photo("photo-1584132967334-10e028bd69f7"), photo("photo-1600607687920-4e2a09cf159d")],
            "amenities": ["WiFi", "Breakfast", "Pool", "Restaurant", "Air conditioning"], "rating": 4.9, "reviews": 182,
            "policies": {"checkIn": "2:00 PM", "checkOut": "11:00 AM", "cancellation": "Free cancellation up to 48 hours before arrival"},
            "nearby": ["City Palace", "Hawa Mahal", "Jantar Mantar"], "rooms": [
                {"id": "room-amber-signature", "hotelId": "hotel-amber-house", "name": "The Signature Room", "type": "Double", "description": "A calm room with old-city light.", "maxGuests": 2, "beds": 1, "pricePerNight": 145, "totalRooms": 4, "amenities": ["King bed", "Rain shower"], "image": photo("photo-1590490360182-c33d57733427")},
                {"id": "room-amber-suite", "hotelId": "hotel-amber-house", "name": "Courtyard Suite", "type": "Suite", "description": "More room to settle in, with a private terrace.", "maxGuests": 3, "beds": 2, "pricePerNight": 220, "totalRooms": 2, "amenities": ["Terrace", "Sofa bed"], "image": photo("photo-1566073771259-6a8506099945")},
            ],
        },
        {
            "_id": "hotel-cedar-stories", "ownerId": "user-demo-owner", "name": "Cedar Stories",
            "propertyType": "Cabin", "description": "A cedar cabin tucked into green hills, made for long breakfasts, wool socks, and the kind of quiet that resets a week.",
            "city": "Manali", "country": "India", "address": "Old Manali, Himachal Pradesh 175131",
            "image": photo("photo-1449158743715-0a90ebb6d2d8"), "images": [photo("photo-1449158743715-0a90ebb6d2d8"), photo("photo-1510798831971-661eb04b3739"), photo("photo-1505693416388-ac5ce068fe85")],
            "amenities": ["WiFi", "Fireplace", "Mountain view", "Kitchen"], "rating": 4.8, "reviews": 96,
            "policies": {"checkIn": "3:00 PM", "checkOut": "11:00 AM", "cancellation": "Free cancellation up to 72 hours before arrival"},
            "nearby": ["Hidimba Temple", "Mall Road", "Solang Valley"], "rooms": [
                {"id": "room-cedar-loft", "hotelId": "hotel-cedar-stories", "name": "The Loft", "type": "Double", "description": "A warm loft under the cedar roof.", "maxGuests": 2, "beds": 1, "pricePerNight": 120, "totalRooms": 3, "amenities": ["Wood stove", "Valley view"], "image": photo("photo-1520250497591-112f2f40a3f4")},
            ],
        },
        {
            "_id": "hotel-tide-house", "ownerId": "user-demo-owner", "name": "Tide House",
            "propertyType": "Villa", "description": "An easy, salt-air villa where the garden leads straight to the sea and every room makes a little more sense with the windows open.",
            "city": "Goa", "country": "India", "address": "Ozran Beach Road, Goa 403509",
            "image": photo("photo-1602002418082-a4443e081dd1"), "images": [photo("photo-1602002418082-a4443e081dd1"), photo("photo-1600607688969-a5bfcd646154"), photo("photo-1540541338287-41700207dee6")],
            "amenities": ["WiFi", "Pool", "Beach access", "Breakfast"], "rating": 4.7, "reviews": 74,
            "policies": {"checkIn": "1:00 PM", "checkOut": "10:00 AM", "cancellation": "Flexible cancellation available"},
            "nearby": ["Ozran Beach", "Anjuna Market", "Vagator Fort"], "rooms": [
                {"id": "room-tide-garden", "hotelId": "hotel-tide-house", "name": "Garden Room", "type": "Double", "description": "A breezy room with a garden door.", "maxGuests": 2, "beds": 1, "pricePerNight": 180, "totalRooms": 5, "amenities": ["Garden access", "Breakfast"], "image": photo("photo-1566665797739-1674de7a421a")},
                {"id": "room-tide-pool", "hotelId": "hotel-tide-house", "name": "Pool Villa", "type": "Suite", "description": "A private pool and an afternoon with nowhere else to be.", "maxGuests": 4, "beds": 2, "pricePerNight": 310, "totalRooms": 2, "amenities": ["Private pool", "Kitchen"], "image": photo("photo-1600607687939-ce8a6c25118c")},
            ],
        },
    ]


def seed(force: bool = False) -> None:
    init_indexes()
    if force:
        users_col.delete_many({})
        hotels_col.delete_many({})
        bookings_col.delete_many({})

    if users_col.count_documents({}) == 0:
        users_col.insert_many(_demo_users())
        print("[seed] Inserted demo users (guest@staywise.test / owner@staywise.test, password: demo1234)")

    if hotels_col.count_documents({}) == 0:
        hotels_col.insert_many(_demo_hotels())
        print("[seed] Inserted demo hotels")


if __name__ == "__main__":
    seed(force="--force" in __import__("sys").argv)
    print("[seed] Done.")
