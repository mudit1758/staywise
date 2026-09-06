from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import payments
from config import (
    CLIENT_URL,
    EMAIL_ENABLED,
    RAZORPAY_ENABLED,
    RAZORPAY_KEY_ID,
    REFUND_FEE_PERCENT,
    REFUND_PERCENT,
)
from db import bookings_col, check_connection, hotels_col, users_col
from email_utils import (
    send_booking_confirmation_email,
    send_cancellation_refund_email,
)
from security import current_user, make_id, password_hash, password_matches, public_user, require_owner, token_for, user_by_email
from seed_data import seed

# --------------------------------------------------------------------------
# Request/response models
# --------------------------------------------------------------------------


class RegisterBody(BaseModel):
    name: str = Field(min_length=2)
    email: str
    phone: str = ""
    password: str = Field(min_length=6)
    role: str = "guest"


class LoginBody(BaseModel):
    email: str
    password: str
    role: str | None = None


class BookingBody(BaseModel):
    hotelId: str
    roomId: str
    checkIn: str
    checkOut: str
    guests: int = Field(ge=1)
    numberOfRooms: int = Field(default=1, ge=1)


class VerifyPaymentBody(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class StatusBody(BaseModel):
    status: str


class RoomBody(BaseModel):
    name: str
    type: str = "Double"
    description: str = ""
    maxGuests: int = Field(default=2, ge=1)
    beds: int = Field(default=1, ge=1)
    pricePerNight: float = Field(gt=0)
    totalRooms: int = Field(default=1, ge=1)
    amenities: list[str] = []
    image: str = ""


class HotelBody(BaseModel):
    name: str
    propertyType: str = "Boutique hotel"
    description: str = Field(min_length=20)
    city: str
    country: str
    address: str
    image: str = ""
    amenities: list[str] = []


# --------------------------------------------------------------------------
# App setup
# --------------------------------------------------------------------------

app = FastAPI(title="Staywise API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CLIENT_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    check_connection()  # fail fast with a clear error if MongoDB isn't reachable
    seed()  # inserts demo users/hotels only if the collections are empty


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def room_for(hotel: dict[str, Any], room_id: str) -> dict[str, Any] | None:
    return next((room for room in hotel.get("rooms", []) if room["id"] == room_id), None)


def dates_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return start_a < end_b and end_a > start_b


def available_rooms(room: dict[str, Any], check_in: date, check_out: date, exclude_id: str | None = None) -> int:
    clashing = bookings_col.find(
        {
            "roomId": room["id"],
            "_id": {"$ne": exclude_id} if exclude_id else {"$exists": True},
            "bookingStatus": {"$nin": ["cancelled", "rejected", "pending_payment"]},
        }
    )
    used = sum(
        item["numberOfRooms"]
        for item in clashing
        if dates_overlap(check_in, check_out, date.fromisoformat(item["checkIn"]), date.fromisoformat(item["checkOut"]))
    )
    return room["totalRooms"] - used


def hotel_summary(hotel: dict[str, Any]) -> dict[str, Any]:
    rooms = hotel.get("rooms", [])
    return {
        **{key: value for key, value in hotel.items() if key != "_id"},
        "id": hotel["_id"],
        "location": hotel["address"].split(",")[0],
        "priceFrom": min((room["pricePerNight"] for room in rooms), default=0),
    }


def booking_view(booking: dict[str, Any]) -> dict[str, Any]:
    hotel = hotels_col.find_one({"_id": booking["hotelId"]}) or {}
    room = room_for(hotel, booking["roomId"]) or {}
    guest = users_col.find_one({"_id": booking["userId"]}) or {}
    return {
        **{key: value for key, value in booking.items() if key != "_id"},
        "id": booking["_id"],
        "hotelName": hotel.get("name", ""),
        "hotelImage": hotel.get("image", ""),
        "roomName": room.get("name", "Room"),
        "guestName": guest.get("name", "Guest"),
        "guestEmail": guest.get("email", ""),
    }


# --------------------------------------------------------------------------
# Health / config
# --------------------------------------------------------------------------


@app.get("/api/healthz")
def health() -> dict[str, Any]:
    return {"status": "ok", "razorpayConfigured": RAZORPAY_ENABLED, "emailConfigured": EMAIL_ENABLED}

@app.get("/api/refund-policy")
def refund_policy() -> dict[str, Any]:
    return {
        "cancellationFeePercent": REFUND_FEE_PERCENT,
        "refundPercent": REFUND_PERCENT,
        "description": (
            f"Guest cancellations are charged a "
            f"{REFUND_FEE_PERCENT:g}% cancellation fee. "
            f"The remaining {REFUND_PERCENT:g}% of the total amount paid "
            f"is refunded."
        ),
        "calculation": (
            f"Cancellation charge = Total paid × "
            f"{REFUND_FEE_PERCENT:g}%"
        ),
        "refundCalculation": (
            f"Refund = Total paid × "
            f"{REFUND_PERCENT:g}%"
        ),
    }

# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------


@app.post("/api/auth/register", status_code=201)
def register(body: RegisterBody) -> dict[str, Any]:
    email = body.email.strip().lower()
    if user_by_email(email):
        raise HTTPException(400, "An account with that email already exists.")
    role = body.role if body.role in ("guest", "owner") else "guest"
    user = {
        "_id": make_id("user"),
        "name": body.name,
        "email": email,
        "phone": body.phone,
        "role": role,
        "passwordHash": password_hash(body.password),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    users_col.insert_one(user)
    return {"token": token_for(user), "user": public_user(user)}


@app.post("/api/auth/login")
def login(body: LoginBody) -> dict[str, Any]:
    user = user_by_email(body.email)
    if not user or (body.role and user["role"] != body.role) or not password_matches(body.password, user["passwordHash"]):
        raise HTTPException(401, "The email, password, or account type is incorrect.")
    return {"token": token_for(user), "user": public_user(user)}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return public_user(user)


# --------------------------------------------------------------------------
# Hotels
# --------------------------------------------------------------------------


@app.get("/api/hotels")
def list_hotels(
    destination: str | None = None,
    propertyType: str | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    sort: str = "recommended",
    checkIn: str | None = None,
    checkOut: str | None = None,
    guests: int = 1,
) -> list[dict[str, Any]]:
    result = []
    for hotel in hotels_col.find({}):
        summary = hotel_summary(hotel)
        haystack = f"{hotel['name']} {hotel['city']} {hotel['country']} {hotel['address']}".lower()
        if destination and destination.lower() not in haystack:
            continue
        if propertyType and hotel["propertyType"].lower() != propertyType.lower():
            continue
        if minPrice is not None and summary["priceFrom"] < minPrice:
            continue
        if maxPrice is not None and summary["priceFrom"] > maxPrice:
            continue
        if guests > 0 and not any(room["maxGuests"] >= guests for room in hotel.get("rooms", [])):
            continue
        if checkIn and checkOut:
            try:
                start, end = date.fromisoformat(checkIn), date.fromisoformat(checkOut)
                if not any(available_rooms(room, start, end) > 0 for room in hotel.get("rooms", [])):
                    continue
            except ValueError:
                raise HTTPException(400, "Dates must use YYYY-MM-DD")
        result.append({key: value for key, value in summary.items() if key != "rooms"})
    if sort == "price_low":
        result.sort(key=lambda item: item["priceFrom"])
    elif sort == "price_high":
        result.sort(key=lambda item: item["priceFrom"], reverse=True)
    elif sort == "rating":
        result.sort(key=lambda item: item["rating"], reverse=True)
    return result


@app.get("/api/hotels/{hotel_id}")
def get_hotel(hotel_id: str) -> dict[str, Any]:
    hotel = hotels_col.find_one({"_id": hotel_id})
    if not hotel:
        raise HTTPException(404, "Hotel not found")
    return hotel_summary(hotel)


# --------------------------------------------------------------------------
# Bookings
# --------------------------------------------------------------------------


@app.post("/api/bookings", status_code=201)
def create_booking(body: BookingBody, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    hotel = hotels_col.find_one({"_id": body.hotelId})
    if not hotel:
        raise HTTPException(404, "Hotel not found")
    room = room_for(hotel, body.roomId)
    if not room:
        raise HTTPException(404, "Room not found")
    try:
        check_in, check_out = date.fromisoformat(body.checkIn), date.fromisoformat(body.checkOut)
    except ValueError as exc:
        raise HTTPException(400, "Dates must use YYYY-MM-DD") from exc
    nights = (check_out - check_in).days
    if nights <= 0:
        raise HTTPException(400, "Check-out must be after check-in")
    if body.guests > room["maxGuests"]:
        raise HTTPException(400, "This room cannot fit that many guests")
    if available_rooms(room, check_in, check_out) < body.numberOfRooms:
        raise HTTPException(409, "Those dates are no longer available")
    subtotal = room["pricePerNight"] * nights * body.numberOfRooms
    total_amount = round(subtotal * 1.08, 2)

    booking = {
        "_id": make_id("booking"),
        "userId": user["_id"],
        "hotelId": hotel["_id"],
        "roomId": room["id"],
        "checkIn": body.checkIn,
        "checkOut": body.checkOut,
        "guests": body.guests,
        "numberOfRooms": body.numberOfRooms,
        "numberOfNights": nights,
        "pricePerNight": room["pricePerNight"],
        "taxes": round(subtotal * 0.08, 2),
        "totalAmount": total_amount,

        # Payment
        "paymentStatus": "pending",
        "bookingStatus": "pending_payment",
        "razorpayOrderId": None,
        "razorpayPaymentId": None,

        # Refund information
        "refundStatus": None,
        "refundPolicyPercent": REFUND_FEE_PERCENT,
        "refundPercent": REFUND_PERCENT,
        "refundFeeAmount": None,
        "refundAmount": None,
        "razorpayRefundId": None,
        "refundedAt": None,

        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    bookings_col.insert_one(booking)
    return booking_view(booking)


@app.get("/api/bookings")
def list_bookings(user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    return [booking_view(item) for item in bookings_col.find({"userId": user["_id"]})]


@app.post("/api/bookings/{booking_id}/create-order")
def create_order(booking_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    booking = bookings_col.find_one({"_id": booking_id, "userId": user["_id"]})
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking["paymentStatus"] == "paid":
        raise HTTPException(400, "This booking is already paid.")
    order = payments.create_order(booking_id, booking["totalAmount"])
    bookings_col.update_one({"_id": booking_id}, {"$set": {"razorpayOrderId": order["id"], "paymentStatus": "processing"}})
    return {
        "orderId": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "keyId": RAZORPAY_KEY_ID,
        "bookingId": booking_id,
        "hotelName": (hotels_col.find_one({"_id": booking["hotelId"]}) or {}).get("name", "Staywise"),
        "guestName": user["name"],
        "guestEmail": user["email"],
        "guestPhone": user.get("phone", ""),
    }


@app.post("/api/bookings/{booking_id}/verify-payment")
def verify_payment(booking_id: str, body: VerifyPaymentBody, background_tasks: BackgroundTasks, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    booking = bookings_col.find_one({"_id": booking_id, "userId": user["_id"]})
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.get("razorpayOrderId") != body.razorpay_order_id:
        raise HTTPException(400, "This payment does not match this booking.")

    if not payments.verify_signature(body.razorpay_order_id, body.razorpay_payment_id, body.razorpay_signature):
        bookings_col.update_one({"_id": booking_id}, {"$set": {"paymentStatus": "pending"}})
        raise HTTPException(400, "Payment verification failed. Please try again.")

    bookings_col.update_one(
        {"_id": booking_id},
        {
            "$set": {
                "paymentStatus": "paid",
                "bookingStatus": "confirmed",
                "razorpayPaymentId": body.razorpay_payment_id,
                "razorpaySignature": body.razorpay_signature,
            }
        },
    )
    booking = bookings_col.find_one({"_id": booking_id})
    hotel = hotels_col.find_one({"_id": booking["hotelId"]}) or {}
    room = room_for(hotel, booking["roomId"]) or {}
    view = booking_view(booking)
    background_tasks.add_task(send_booking_confirmation_email, view, hotel, room, user["name"], user["email"])
    return view


@app.post("/api/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    background_tasks: BackgroundTasks,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:

    # ---------------------------------------------------------
    # 1. Find booking belonging to the logged-in guest
    # ---------------------------------------------------------
    booking = bookings_col.find_one(
        {
            "_id": booking_id,
            "userId": user["_id"],
        }
    )

    if not booking:
        raise HTTPException(
            404,
            "Booking not found.",
        )

    # ---------------------------------------------------------
    # 2. Prevent duplicate cancellation/refund
    # ---------------------------------------------------------
    if booking.get("bookingStatus") == "cancelled":
        return booking_view(booking)

    # ---------------------------------------------------------
    # 3. Only active bookings can be cancelled
    # ---------------------------------------------------------
    if booking.get("bookingStatus") not in (
        "confirmed",
        "pending_payment",
    ):
        raise HTTPException(
            400,
            "Only active bookings can be cancelled.",
        )

    payment_status = booking.get("paymentStatus", "pending")

    # ---------------------------------------------------------
    # 4. If payment has NOT been completed
    # ---------------------------------------------------------
    if payment_status != "paid":

        bookings_col.update_one(
            {"_id": booking_id},
            {
                "$set": {
                    "bookingStatus": "cancelled",
                    "paymentStatus": payment_status,
                    "refundStatus": "not_applicable",
                    "cancelledAt": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            },
        )

        updated = bookings_col.find_one(
            {"_id": booking_id}
        )

        return booking_view(updated)

    # ---------------------------------------------------------
    # 5. Paid booking
    # ---------------------------------------------------------
    total_amount = round(
        float(booking.get("totalAmount", 0)),
        2,
    )

    # 15% cancellation fee
    cancellation_fee = round(
        total_amount * REFUND_FEE_PERCENT / 100,
        2,
    )

    # 85% refund
    refund_amount = round(
        total_amount - cancellation_fee,
        2,
    )

    # ---------------------------------------------------------
    # 6. Prevent accidental second refund
    # ---------------------------------------------------------
    if booking.get("razorpayRefundId"):
        raise HTTPException(
            409,
            "A refund has already been created for this booking.",
        )

    # ---------------------------------------------------------
    # 7. Create actual Razorpay refund
    # ---------------------------------------------------------
    refund = payments.refund_payment(
        booking.get("razorpayPaymentId"),
        refund_amount,
        booking_id,
    )

    refund_id = refund.get("id")

    # ---------------------------------------------------------
    # 8. Save cancellation + refund information
    # ---------------------------------------------------------
    bookings_col.update_one(
        {"_id": booking_id},
        {
            "$set": {
                "bookingStatus": "cancelled",
                "paymentStatus": "refunded",

                "refundStatus": "processed",

                "refundPolicyPercent": REFUND_FEE_PERCENT,
                "refundPercent": REFUND_PERCENT,

                "refundFeeAmount": cancellation_fee,
                "refundAmount": refund_amount,

                "razorpayRefundId": refund_id,

                "cancelledAt": datetime.now(
                    timezone.utc
                ).isoformat(),

                "refundedAt": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        },
    )

    # ---------------------------------------------------------
    # 9. Get updated booking and hotel/room details
    # ---------------------------------------------------------
    updated_booking = bookings_col.find_one(
        {"_id": booking_id}
    )

    hotel = hotels_col.find_one(
        {"_id": updated_booking["hotelId"]}
    ) or {}

    room = room_for(
        hotel,
        updated_booking["roomId"],
    ) or {}

    view = booking_view(updated_booking)

    # ---------------------------------------------------------
    # 10. Send cancellation/refund email
    # ---------------------------------------------------------
    background_tasks.add_task(
        send_cancellation_refund_email,
        view,
        hotel,
        room,
        user["name"],
        user["email"],
    )

    # ---------------------------------------------------------
    # 11. Return updated booking to frontend
    # ---------------------------------------------------------
    return view

# --------------------------------------------------------------------------
# Owner
# --------------------------------------------------------------------------


@app.get("/api/owner/dashboard")
def owner_dashboard(user: dict[str, Any] = Depends(require_owner)) -> dict[str, Any]:
    owner_hotel_ids = [hotel["_id"] for hotel in hotels_col.find({"ownerId": user["_id"]}, {"_id": 1})]
    owner_bookings = list(bookings_col.find({"hotelId": {"$in": owner_hotel_ids}}))
    confirmed = [item for item in owner_bookings if item["bookingStatus"] == "confirmed"]
    monthly = [
        {"month": month, "bookings": len([item for item in owner_bookings if item["createdAt"][5:7] == str(index + 1).zfill(2)])}
        for index, month in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
    ]
    return {
        "totalProperties": len(owner_hotel_ids),
        "totalBookings": len(owner_bookings),
        "pendingBookings": len([item for item in owner_bookings if item["bookingStatus"] == "pending_payment"]),
        "confirmedBookings": len(confirmed),
        "cancelledBookings": len([item for item in owner_bookings if item["bookingStatus"] == "cancelled"]),
        "totalRevenue": round(sum(item["totalAmount"] for item in confirmed), 2),
        "monthlyBookings": monthly,
    }


@app.get("/api/owner/bookings")
def owner_bookings(user: dict[str, Any] = Depends(require_owner)) -> list[dict[str, Any]]:
    owner_hotel_ids = [hotel["_id"] for hotel in hotels_col.find({"ownerId": user["_id"]}, {"_id": 1})]
    return [booking_view(item) for item in bookings_col.find({"hotelId": {"$in": owner_hotel_ids}})]


@app.put("/api/owner/bookings/{booking_id}/status")
def update_booking_status(booking_id: str, body: StatusBody, user: dict[str, Any] = Depends(require_owner)) -> dict[str, Any]:
    booking = bookings_col.find_one({"_id": booking_id})
    hotel = hotels_col.find_one({"_id": booking["hotelId"]}) if booking else None
    if not booking or not hotel or hotel.get("ownerId") != user["_id"]:
        raise HTTPException(404, "Booking not found")
    if body.status not in ("confirmed", "rejected", "completed", "cancelled"):
        raise HTTPException(400, "Unsupported booking status")
    bookings_col.update_one({"_id": booking_id}, {"$set": {"bookingStatus": body.status}})
    return booking_view(bookings_col.find_one({"_id": booking_id}))


@app.post("/api/owner/hotels", status_code=201)
def create_hotel(body: HotelBody, user: dict[str, Any] = Depends(require_owner)) -> dict[str, Any]:
    hotel = {
        "_id": make_id("hotel"),
        "ownerId": user["_id"],
        "name": body.name,
        "propertyType": body.propertyType,
        "description": body.description,
        "city": body.city,
        "country": body.country,
        "address": body.address,
        "image": body.image,
        "images": [body.image] if body.image else [],
        "amenities": body.amenities,
        "rating": 0,
        "reviews": 0,
        "policies": {"checkIn": "3:00 PM", "checkOut": "11:00 AM", "cancellation": "Flexible cancellation available"},
        "nearby": [],
        "rooms": [],
    }
    hotels_col.insert_one(hotel)
    return hotel_summary(hotel)


@app.put("/api/owner/hotels/{hotel_id}")
def update_hotel(hotel_id: str, body: HotelBody, user: dict[str, Any] = Depends(require_owner)) -> dict[str, Any]:
    hotel = hotels_col.find_one({"_id": hotel_id})
    if not hotel or hotel.get("ownerId") != user["_id"]:
        raise HTTPException(404, "Hotel not found")
    hotels_col.update_one({"_id": hotel_id}, {"$set": body.model_dump()})
    return hotel_summary(hotels_col.find_one({"_id": hotel_id}))


@app.post("/api/owner/hotels/{hotel_id}/rooms", status_code=201)
def create_room(hotel_id: str, body: RoomBody, user: dict[str, Any] = Depends(require_owner)) -> dict[str, Any]:
    hotel = hotels_col.find_one({"_id": hotel_id})
    if not hotel or hotel.get("ownerId") != user["_id"]:
        raise HTTPException(404, "Hotel not found")
    room = {"id": make_id("room"), "hotelId": hotel_id, **body.model_dump()}
    hotels_col.update_one({"_id": hotel_id}, {"$push": {"rooms": room}})
    return room
