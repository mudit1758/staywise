"""
Thin wrapper around the Razorpay Python SDK, used in TEST MODE.

Nothing here trusts the frontend: the order is created server-side with the
authoritative amount already stored on the booking, and the payment
signature is verified server-side before a booking is ever marked paid.
"""
from __future__ import annotations

from typing import Any

import razorpay
from fastapi import HTTPException

from config import RAZORPAY_CURRENCY, RAZORPAY_ENABLED, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)) if RAZORPAY_ENABLED else None


def to_paise(rupee_amount: float) -> int:
    return int(round(rupee_amount * 100))


def create_order(booking_id: str, amount_in_rupees: float) -> dict[str, Any]:
    if not RAZORPAY_ENABLED or _client is None:
        raise HTTPException(
            503,
            "Razorpay isn't configured on the server yet. Add RAZORPAY_KEY_ID and "
            "RAZORPAY_KEY_SECRET (test keys) to backend/.env and restart the API.",
        )
    order = _client.order.create(
        {
            "amount": to_paise(amount_in_rupees),
            "currency": RAZORPAY_CURRENCY,
            "receipt": booking_id,
            "notes": {"bookingId": booking_id},
        }
    )
    return order


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    if not RAZORPAY_ENABLED or _client is None:
        raise HTTPException(503, "Razorpay isn't configured on the server yet.")
    try:
        _client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False

    
def refund_payment(
    payment_id: str,
    amount_in_rupees: float,
    booking_id: str,
) -> dict[str, Any]:
    """
    Create a partial Razorpay refund.

    amount_in_rupees is converted to paise because Razorpay
    expects the amount in the smallest currency unit.
    """

    if not RAZORPAY_ENABLED or _client is None:
        raise HTTPException(
            503,
            "Razorpay isn't configured on the server yet.",
        )

    if not payment_id:
        raise HTTPException(
            400,
            "This booking does not have a Razorpay payment reference.",
        )

    if amount_in_rupees <= 0:
        raise HTTPException(
            400,
            "Refund amount must be greater than zero.",
        )

    amount_paise = to_paise(amount_in_rupees)

    try:
        refund = _client.payment.refund(
            payment_id,
            {
                "amount": amount_paise,
                "receipt": f"refund_{booking_id}",
                "notes": {
                    "bookingId": booking_id,
                    "reason": "Guest cancellation",
                    "cancellationFeePercent": "15",
                },
            },
        )

        return refund

    except Exception as exc:
        raise HTTPException(
            502,
            f"Razorpay refund failed: {exc}",
        ) from exc