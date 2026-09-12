"""
Staywise email utilities.

Emails are sent through the Resend HTTPS API instead of SMTP.

This works on Render Free because it uses HTTPS rather than
outbound SMTP ports 25/465/587.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import resend
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_FROM_NAME,
    RESEND_API_KEY,
)

BRAND_COLOR = "#15734f"
BRAND_DARK = "#0f2a22"


def _money(value: float) -> str:
    return f"₹{value:,.2f}"


def _date_label(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%a, %d %b %Y")
    except (ValueError, TypeError):
        return value


def _row(
    label: str,
    value: str,
    *,
    strong: bool = False,
    top_border: bool = False,
) -> str:
    border = "border-top:1px solid #e7e9e5;" if top_border else ""
    weight = "font-weight:600;" if strong else ""

    return (
        f"<tr>"
        f'<td style="padding:10px 0;{border}color:#5b645c;font-size:14px">'
        f"{label}"
        f"</td>"
        f'<td style="padding:10px 0;{border}{weight}'
        f'text-align:right;font-size:14px;color:{BRAND_DARK}">'
        f"{value}"
        f"</td>"
        f"</tr>"
    )


def _send_email(
    *,
    to_email: str,
    to_name: str,
    subject: str,
    text_body: str,
    html_body: str,
    email_type: str,
    reference: str,
) -> None:
    """
    Send one email through Resend.

    This function deliberately catches exceptions so a failed email
    does not break a successful booking or refund operation.
    """

    if not EMAIL_ENABLED:
        print(
            f"[email] Email is not configured. "
            f"Skipped {email_type} email for {reference} to {to_email}."
        )
        return

    try:
        resend.api_key = RESEND_API_KEY

        params: resend.Emails.SendParams = {
            "from": f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }

        result = resend.Emails.send(params)

        print(
            f"[email] Sent {email_type} email for {reference} "
            f"to {to_email}. Resend response: {result}"
        )

    except Exception as exc:
        print(
            f"[email] Failed to send {email_type} email "
            f"for {reference} to {to_email}: {exc}"
        )


# ==========================================================================
# BOOKING CONFIRMATION EMAIL
# ==========================================================================


def _build_confirmation_email(
    booking: dict[str, Any],
    hotel: dict[str, Any],
    room: dict[str, Any],
    guest_name: str,
    guest_email: str,
) -> tuple[str, str, str]:

    booking_id = booking["id"]

    room_name = room.get("name", "Room")
    hotel_name = hotel.get("name", "Staywise")
    hotel_address = hotel.get("address", "")

    check_in = _date_label(booking.get("checkIn", ""))
    check_out = _date_label(booking.get("checkOut", ""))

    guests = booking.get("guests", 1)
    room_count = booking.get("numberOfRooms", 1)
    nights = booking.get("numberOfNights", "")

    subject = (
        f"Booking confirmed: "
        f"{hotel_name} — {booking_id}"
    )

    text_body = (
        f"Hi {guest_name},\n\n"

        f"Your payment went through and your stay at "
        f"{hotel_name} is confirmed.\n\n"

        f"Booking reference: {booking_id}\n"
        f"Room: {room_name}\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n"
        f"Guests: {guests}\n"
        f"Rooms booked: {room_count}\n"
        f"Nights: {nights}\n\n"

        f"Room rate: "
        f"{_money(float(booking.get('pricePerNight', 0)))} / night\n"

        f"Taxes & fees: "
        f"{_money(float(booking.get('taxes', 0)))}\n"

        f"Total paid: "
        f"{_money(float(booking.get('totalAmount', 0)))}\n"

        f"Payment reference: "
        f"{booking.get('razorpayPaymentId', '-')}\n\n"

        f"Property address: {hotel_address}\n\n"

        f"You can view or manage this booking any time "
        f"from your Staywise account.\n\n"

        f"Thanks for booking with Staywise.\n"
    )

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="
    margin:0;
    padding:0;
    background:#f3f4f1;
    font-family:-apple-system,BlinkMacSystemFont,
    'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
">

<table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="background:#f3f4f1;padding:32px 16px;"
>
<tr>
<td align="center">

<table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        max-width:560px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        border:1px solid #e7e9e5;
    "
>

<tr>
<td style="
    background:{BRAND_COLOR};
    padding:28px 32px;
">
    <p style="
        margin:0;
        color:#eafff3;
        font-size:13px;
        letter-spacing:.06em;
        text-transform:uppercase;
    ">
        Staywise
    </p>

    <h1 style="
        margin:8px 0 0;
        color:#ffffff;
        font-size:22px;
    ">
        Your booking is confirmed
    </h1>
</td>
</tr>

<tr>
<td style="padding:28px 32px 4px;">

<p style="
    margin:0 0 8px;
    color:{BRAND_DARK};
    font-size:15px;
">
Hi {guest_name},
</p>

<p style="
    margin:0;
    color:#5b645c;
    font-size:14px;
    line-height:1.55;
">
Payment was received and your stay at
<b>{hotel_name}</b> is booked.
</p>

</td>
</tr>

<tr>
<td style="padding:20px 32px 4px;">

<table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        background:#f7f8f5;
        border-radius:10px;
        padding:16px;
    "
>
<tr>
<td>

<p style="
    margin:0;
    font-size:16px;
    font-weight:700;
    color:{BRAND_DARK};
">
{hotel_name}
</p>

<p style="
    margin:4px 0 0;
    font-size:13px;
    color:#5b645c;
">
{hotel_address}
</p>

<p style="
    margin:8px 0 0;
    font-size:12px;
    color:#8a9086;
">
Booking reference
</p>

<p style="
    margin:2px 0 0;
    font-size:14px;
    font-weight:600;
    color:{BRAND_DARK};
">
{booking_id}
</p>

</td>
</tr>
</table>

</td>
</tr>

<tr>
<td style="padding:16px 32px 0;">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="border-collapse:collapse;"
>

{_row("Room", room_name)}
{_row("Check-in", check_in)}
{_row("Check-out", check_out)}
{_row("Guests", str(guests))}
{_row("Rooms booked", str(room_count))}
{_row("Nights", str(nights))}

</table>

</td>
</tr>

<tr>
<td style="padding:8px 32px 0;">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="border-collapse:collapse;"
>

{_row(
    "Room rate",
    f"{_money(float(booking.get('pricePerNight', 0)))} / night",
    top_border=True
)}

{_row(
    "Taxes &amp; fees",
    _money(float(booking.get("taxes", 0)))
)}

{_row(
    "Total paid",
    _money(float(booking.get("totalAmount", 0))),
    strong=True,
    top_border=True
)}

</table>

</td>
</tr>

<tr>
<td style="padding:12px 32px 0;">

<p style="
    margin:0;
    font-size:12px;
    color:#8a9086;
">
Paid via Razorpay ·
Payment ID {booking.get("razorpayPaymentId", "-")}
</p>

</td>
</tr>

<tr>
<td style="padding:20px 32px 28px;">

<p style="
    margin:0;
    font-size:14px;
    color:#5b645c;
">
You can view and manage this booking from
your Staywise account.
</p>

</td>
</tr>

<tr>
<td style="
    padding:20px 32px 28px;
    border-top:1px solid #e7e9e5;
">

<p style="
    margin:0;
    font-size:12px;
    color:#8a9086;
">
Staywise · Automated booking confirmation.
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    return subject, text_body, html_body


def send_booking_confirmation_email(
    booking: dict[str, Any],
    hotel: dict[str, Any],
    room: dict[str, Any],
    guest_name: str,
    guest_email: str,
) -> None:

    booking_id = booking.get("id", "?")

    try:
        subject, text_body, html_body = _build_confirmation_email(
            booking,
            hotel,
            room,
            guest_name,
            guest_email,
        )

        _send_email(
            to_email=guest_email,
            to_name=guest_name,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            email_type="booking confirmation",
            reference=booking_id,
        )

    except Exception as exc:
        print(
            f"[email] Could not build/send confirmation "
            f"email for {booking_id}: {exc}"
        )


# ==========================================================================
# CANCELLATION + REFUND EMAIL
# ==========================================================================


def _build_cancellation_email(
    booking: dict[str, Any],
    hotel: dict[str, Any],
    room: dict[str, Any],
    guest_name: str,
    guest_email: str,
) -> tuple[str, str, str]:

    booking_id = booking["id"]

    hotel_name = hotel.get("name", "Staywise")
    room_name = room.get("name", "Room")

    total = float(
        booking.get("totalAmount", 0)
    )

    fee = float(
        booking.get(
            "refundFeeAmount",
            round(total * 0.15, 2),
        )
    )

    refund = float(
        booking.get(
            "refundAmount",
            round(total - fee, 2),
        )
    )

    status = booking.get(
        "refundStatus",
        "not_applicable",
    )

    refund_status = (
        "Refund initiated"
        if status == "processed"
        else "No refund applicable"
    )

    subject = (
        f"Booking cancelled & refund: "
        f"{hotel_name} — {booking_id}"
    )

    text_body = (
        f"Hi {guest_name},\n\n"

        f"Your booking at {hotel_name} "
        f"has been cancelled.\n\n"

        f"Booking reference: {booking_id}\n"
        f"Room: {room_name}\n"
        f"Check-in: {_date_label(booking.get('checkIn', ''))}\n"
        f"Check-out: {_date_label(booking.get('checkOut', ''))}\n\n"

        f"REFUND CALCULATION\n"
        f"------------------\n"
        f"Original amount paid: {_money(total)}\n"
        f"Cancellation charge (15%): {_money(fee)}\n"
        f"Refund amount (85%): {_money(refund)}\n\n"

        f"Refund status: {refund_status}\n"
        f"Refund reference: "
        f"{booking.get('razorpayRefundId', '-')}\n\n"

        f"The refund is processed through Razorpay "
        f"and may take several working days to appear, "
        f"depending on your bank/payment method.\n\n"

        f"Thanks,\n"
        f"Staywise\n"
    )

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="
    margin:0;
    padding:0;
    background:#f3f4f1;
    font-family:-apple-system,BlinkMacSystemFont,
    'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
">

<table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="background:#f3f4f1;padding:32px 16px;"
>
<tr>
<td align="center">

<table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        max-width:560px;
        background:#ffffff;
        border-radius:14px;
        overflow:hidden;
        border:1px solid #e7e9e5;
    "
>

<tr>
<td style="
    background:{BRAND_COLOR};
    padding:28px 32px;
">

<p style="
    margin:0;
    color:#eafff3;
    font-size:13px;
    letter-spacing:.06em;
    text-transform:uppercase;
">
Staywise
</p>

<h1 style="
    margin:8px 0 0;
    color:#ffffff;
    font-size:22px;
">
Booking cancelled &amp; refund
</h1>

</td>
</tr>

<tr>
<td style="padding:28px 32px 8px;">

<p style="
    margin:0 0 8px;
    color:{BRAND_DARK};
    font-size:15px;
">
Hi {guest_name},
</p>

<p style="
    margin:0;
    color:#5b645c;
    font-size:14px;
    line-height:1.55;
">
Your booking at
<b>{hotel_name}</b>
has been cancelled successfully.
</p>

</td>
</tr>

<tr>
<td style="padding:20px 32px 4px;">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        background:#f7f8f5;
        border-radius:10px;
        padding:16px;
    "
>

<tr>
<td>

<p style="
    margin:0;
    font-weight:700;
    color:{BRAND_DARK};
">
Booking {booking_id}
</p>

<p style="
    margin:5px 0 0;
    color:#5b645c;
    font-size:13px;
">
{room_name}
·
{_date_label(booking.get("checkIn", ""))}
—
{_date_label(booking.get("checkOut", ""))}
</p>

</td>
</tr>

</table>

</td>
</tr>

<tr>
<td style="padding:16px 32px 0;">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="border-collapse:collapse;"
>

{_row(
    "Original amount paid",
    _money(total),
    top_border=True
)}

{_row(
    "Cancellation charge (15%)",
    _money(fee)
)}

{_row(
    "Refund amount (85%)",
    _money(refund),
    strong=True,
    top_border=True
)}

</table>

</td>
</tr>

<tr>
<td style="padding:16px 32px 8px;">

<p style="
    margin:0;
    color:{BRAND_DARK};
    font-weight:700;
">
{refund_status}
</p>

<p style="
    margin:6px 0 0;
    color:#8a9086;
    font-size:12px;
">
Refund reference:
{booking.get("razorpayRefundId", "-")}
</p>

<p style="
    margin:6px 0 0;
    color:#8a9086;
    font-size:12px;
">
Refunds can take several working days
to reach your account.
</p>

</td>
</tr>

<tr>
<td style="
    padding:20px 32px 28px;
    border-top:1px solid #e7e9e5;
">

<p style="
    margin:0;
    font-size:12px;
    color:#8a9086;
">
Staywise · Automated cancellation and refund notice.
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    return subject, text_body, html_body


def send_cancellation_refund_email(
    booking: dict[str, Any],
    hotel: dict[str, Any],
    room: dict[str, Any],
    guest_name: str,
    guest_email: str,
) -> None:

    booking_id = booking.get("id", "?")

    try:
        subject, text_body, html_body = _build_cancellation_email(
            booking,
            hotel,
            room,
            guest_name,
            guest_email,
        )

        _send_email(
            to_email=guest_email,
            to_name=guest_name,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            email_type="cancellation/refund",
            reference=booking_id,
        )

    except Exception as exc:
        print(
            f"[email] Could not build/send cancellation/refund "
            f"email for {booking_id}: {exc}"
        )
