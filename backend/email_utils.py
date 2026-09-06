"""
Sends the "booking confirmed" email after a Razorpay payment is verified.

If SMTP credentials are not configured (see backend/.env.example), this
module does not fail the booking -- it logs the email to the console
instead, so the rest of the app keeps working in a fresh local checkout.
"""
from __future__ import annotations

import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

from config import (
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)

BRAND_COLOR = "#15734f"
BRAND_DARK = "#0f2a22"


def _money(value: float) -> str:
    return f"₹{value:,.2f}"


def _date_label(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%a, %d %b %Y")
    except ValueError:
        return value


def _row(label: str, value: str, *, strong: bool = False, top_border: bool = False) -> str:
    border = "border-top:1px solid #e7e9e5;" if top_border else ""
    weight = "font-weight:600;" if strong else ""
    return (
        f'<tr>'
        f'<td style="padding:10px 0;{border}color:#5b645c;font-size:14px">{label}</td>'
        f'<td style="padding:10px 0;{border}{weight}text-align:right;font-size:14px;color:{BRAND_DARK}">{value}</td>'
        f"</tr>"
    )


def _build_message(booking: dict[str, Any], hotel: dict[str, Any], room: dict[str, Any], guest_name: str, guest_email: str) -> MIMEMultipart:
    booking_id = booking["id"]
    room_name = room.get("name", "Room")
    hotel_name = hotel.get("name", "Staywise")
    hotel_address = hotel.get("address", "")
    check_in = _date_label(booking["checkIn"])
    check_out = _date_label(booking["checkOut"])
    guests = booking["guests"]
    room_count = booking.get("numberOfRooms", 1)
    nights = booking.get("numberOfNights", "")
    subject = f"Booking confirmed: {hotel_name} — {booking_id}"

    text_body = (
        f"Hi {guest_name},\n\n"
        f"Your payment went through and your stay at {hotel_name} is confirmed.\n\n"
        f"Booking reference: {booking_id}\n"
        f"Room: {room_name}\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n"
        f"Guests: {guests}\n"
        f"Rooms booked: {room_count}\n"
        f"Nights: {nights}\n"
        f"Room rate: {_money(booking['pricePerNight'])} / night\n"
        f"Taxes & fees: {_money(booking['taxes'])}\n"
        f"Total paid: {_money(booking['totalAmount'])}\n"
        f"Payment reference: {booking.get('razorpayPaymentId', '-')}\n\n"
        f"Property address: {hotel_address}\n\n"
        f"You can view or manage this booking any time from your Staywise account.\n\n"
        f"Thanks for booking with Staywise.\n"
    )

    html_body = f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background:#f3f4f1;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f1;padding:32px 16px;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e7e9e5;">

          <!-- Header -->
          <tr>
            <td style="background:{BRAND_COLOR};padding:28px 32px;">
              <p style="margin:0;color:#eafff3;font-size:13px;letter-spacing:.06em;text-transform:uppercase;">Staywise</p>
              <h1 style="margin:8px 0 0;color:#ffffff;font-size:22px;line-height:1.3;">Your booking is confirmed</h1>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:28px 32px 4px;">
              <p style="margin:0 0 8px;color:{BRAND_DARK};font-size:15px;">Hi {guest_name},</p>
              <p style="margin:0;color:#5b645c;font-size:14px;line-height:1.55;">
                Payment was received and your stay at <b>{hotel_name}</b> is booked. Here's your confirmation for the records.
              </p>
            </td>
          </tr>

          <!-- Hotel card -->
          <tr>
            <td style="padding:20px 32px 4px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f7f8f5;border-radius:10px;padding:16px;">
                <tr><td style="padding:0 4px;">
                  <p style="margin:0;font-size:16px;font-weight:700;color:{BRAND_DARK};">{hotel_name}</p>
                  <p style="margin:4px 0 0;font-size:13px;color:#5b645c;">{hotel_address}</p>
                  <p style="margin:8px 0 0;font-size:12px;color:#8a9086;letter-spacing:.04em;text-transform:uppercase;">Booking reference</p>
                  <p style="margin:2px 0 0;font-size:14px;font-weight:600;color:{BRAND_DARK};">{booking_id}</p>
                </td></tr>
              </table>
            </td>
          </tr>

          <!-- Stay details -->
          <tr>
            <td style="padding:16px 32px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                {_row("Room", room_name)}
                {_row("Check-in", check_in)}
                {_row("Check-out", check_out)}
                {_row("Guests", str(guests))}
                {_row("Rooms booked", str(room_count))}
                {_row("Nights", str(nights))}
              </table>
            </td>
          </tr>

          <!-- Payment summary -->
          <tr>
            <td style="padding:8px 32px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                {_row("Room rate", f"{_money(booking['pricePerNight'])} / night", top_border=True)}
                {_row("Taxes &amp; fees", _money(booking['taxes']))}
                {_row("Total paid", _money(booking['totalAmount']), strong=True, top_border=True)}
              </table>
            </td>
          </tr>

          <!-- Payment reference -->
          <tr>
            <td style="padding:12px 32px 0;">
              <p style="margin:0;font-size:12px;color:#8a9086;">
                Paid via Razorpay &middot; Payment ID {booking.get('razorpayPaymentId', '-')}
              </p>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding:24px 32px 28px;">
              <a href="#" style="display:inline-block;background:{BRAND_COLOR};color:#ffffff;text-decoration:none;font-size:14px;font-weight:600;padding:12px 22px;border-radius:8px;">
                View booking in your account
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px 28px;border-top:1px solid #e7e9e5;">
              <p style="margin:0 0 6px;font-size:12px;color:#8a9086;">
                Questions about this booking? Reply to this email and we'll help you out.
              </p>
              <p style="margin:0;font-size:12px;color:#b3b8ad;">
                Staywise · This is an automated confirmation, sent because a booking on your account was paid for.
              </p>
            </td>
          </tr>

        </table>
      </td></tr>
    </table>
  </body>
</html>
"""

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((EMAIL_FROM_NAME, EMAIL_FROM))
    message["To"] = formataddr((guest_name, guest_email))
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))
    return message


def send_booking_confirmation_email(booking: dict[str, Any], hotel: dict[str, Any], room: dict[str, Any], guest_name: str, guest_email: str) -> None:
    booking_id = booking.get("id", "?")

    try:
        message = _build_message(booking, hotel, room, guest_name, guest_email)
    except Exception as exc:  # noqa: BLE001 — a malformed email must never crash a background task
        print(f"[email] Could not build confirmation email for booking {booking_id}: {exc}")
        return

    if not EMAIL_ENABLED:
        print(
            "[email] SMTP not configured — skipping real send. "
            f"Would have emailed booking confirmation for {booking_id} to {guest_email}."
        )
        return

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [guest_email], message.as_string())
        print(f"[email] Sent booking confirmation for {booking_id} to {guest_email}.")
    except Exception as exc:  # noqa: BLE001 — a failed email must never break a paid booking
        print(f"[email] Failed to send confirmation for {booking_id} to {guest_email}: {exc}")

def send_cancellation_refund_email(
    booking: dict[str, Any],
    hotel: dict[str, Any],
    room: dict[str, Any],
    guest_name: str,
    guest_email: str,
) -> None:
    """
    Send cancellation + refund details to the guest.
    """

    booking_id = booking.get("id", "?")

    hotel_name = hotel.get("name", "Staywise")
    hotel_address = hotel.get("address", "")
    room_name = room.get("name", "Room")

    check_in = _date_label(booking.get("checkIn", ""))
    check_out = _date_label(booking.get("checkOut", ""))

    total_amount = float(booking.get("totalAmount", 0))
    cancellation_fee = float(booking.get("refundFeeAmount", 0))
    refund_amount = float(booking.get("refundAmount", 0))
    fee_percent = float(booking.get("refundPolicyPercent", 15))
    refund_percent = float(booking.get("refundPercent", 85))

    refund_status = booking.get("refundStatus", "processed")
    refund_id = booking.get("razorpayRefundId", "-")

    subject = f"Booking cancelled & refund: {hotel_name} — {booking_id}"

    text_body = (
        f"Hi {guest_name},\n\n"
        f"Your booking at {hotel_name} has been cancelled successfully.\n\n"

        f"BOOKING DETAILS\n"
        f"Booking reference: {booking_id}\n"
        f"Room: {room_name}\n"
        f"Check-in: {check_in}\n"
        f"Check-out: {check_out}\n\n"

        f"REFUND CALCULATION\n"
        f"Total amount paid: {_money(total_amount)}\n"
        f"Cancellation charge ({fee_percent:.0f}%): {_money(cancellation_fee)}\n"
        f"Refund ({refund_percent:.0f}%): {_money(refund_amount)}\n\n"

        f"Refund status: {refund_status}\n"
        f"Refund reference: {refund_id}\n\n"

        f"Property address: {hotel_address}\n\n"

        f"The cancellation charge is {fee_percent:.0f}% of the total amount paid. "
        f"The remaining {refund_percent:.0f}% has been submitted as your refund.\n\n"

        f"Please allow the payment provider/bank's normal processing time for "
        f"the refunded amount to appear in your account.\n\n"

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
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
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
              <td style="background:#15734f;padding:28px 32px;">
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
              <td style="padding:28px 32px 10px;">

                <p style="
                  margin:0 0 8px;
                  color:#0f2a22;
                  font-size:15px;
                ">
                  Hi {guest_name},
                </p>

                <p style="
                  margin:0;
                  color:#5b645c;
                  font-size:14px;
                  line-height:1.6;
                ">
                  Your booking at <b>{hotel_name}</b> has been cancelled successfully.
                  Below is the complete refund calculation.
                </p>

              </td>
            </tr>

            <tr>
              <td style="padding:18px 32px;">

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
                        color:#0f2a22;
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
                        margin:10px 0 0;
                        font-size:12px;
                        color:#8a9086;
                      ">
                        Booking reference
                      </p>

                      <p style="
                        margin:2px 0 0;
                        font-size:14px;
                        font-weight:600;
                        color:#0f2a22;
                      ">
                        {booking_id}
                      </p>
                    </td>
                  </tr>

                </table>

              </td>
            </tr>

            <tr>
              <td style="padding:0 32px;">

                <table
                  role="presentation"
                  width="100%"
                  cellpadding="0"
                  cellspacing="0"
                  style="border-collapse:collapse;"
                >

                  {_row("Room", room_name)}
                  {_row("Check-in", check_in)}
                  {_row("Check-out", check_out)}

                </table>

              </td>
            </tr>

            <tr>
              <td style="padding:20px 32px;">

                <h3 style="
                  margin:0 0 10px;
                  color:#0f2a22;
                  font-size:16px;
                ">
                  Refund calculation
                </h3>

                <table
                  role="presentation"
                  width="100%"
                  cellpadding="0"
                  cellspacing="0"
                  style="border-collapse:collapse;"
                >

                  {_row(
                      "Total amount paid",
                      _money(total_amount),
                      strong=True
                  )}

                  {_row(
                      f"Cancellation charge ({fee_percent:.0f}%)",
                      f"- {_money(cancellation_fee)}"
                  )}

                  {_row(
                      f"Refund ({refund_percent:.0f}%)",
                      _money(refund_amount),
                      strong=True,
                      top_border=True
                  )}

                </table>

              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 20px;">

                <div style="
                  padding:16px;
                  border-radius:10px;
                  background:#eaf7ef;
                  color:#245b3b;
                  font-size:13px;
                  line-height:1.6;
                ">

                  <b>Refund status:</b> {refund_status}<br />

                  <b>Refund reference:</b> {refund_id}

                </div>

              </td>
            </tr>

            <tr>
              <td style="
                padding:20px 32px;
                border-top:1px solid #e7e9e5;
              ">

                <p style="
                  margin:0;
                  color:#5b645c;
                  font-size:13px;
                  line-height:1.6;
                ">
                  A {fee_percent:.0f}% cancellation charge is retained from the
                  total amount paid. The remaining {refund_percent:.0f}% has been
                  submitted for refund.
                </p>

                <p style="
                  margin:12px 0 0;
                  color:#8a9086;
                  font-size:12px;
                  line-height:1.6;
                ">
                  Please allow the normal payment-provider/bank processing time
                  for the refund to appear in your account.
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
                  color:#b3b8ad;
                  font-size:12px;
                ">
                  Staywise · This is an automated cancellation and refund email.
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

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((EMAIL_FROM_NAME, EMAIL_FROM))
    message["To"] = formataddr((guest_name, guest_email))

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    if not EMAIL_ENABLED:
        print(
            "[email] SMTP not configured — skipping real send. "
            f"Would have emailed cancellation/refund for "
            f"{booking_id} to {guest_email}."
        )
        return

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:

            if SMTP_USE_TLS:
                server.starttls()

            server.login(SMTP_USER, SMTP_PASSWORD)

            server.sendmail(
                EMAIL_FROM,
                [guest_email],
                message.as_string(),
            )

        print(
            f"[email] Sent cancellation/refund email "
            f"for {booking_id} to {guest_email}."
        )

    except Exception as exc:
        print(
            f"[email] Failed to send cancellation/refund email "
            f"for {booking_id}: {exc}"
        )