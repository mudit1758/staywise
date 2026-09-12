"""
Central configuration. Everything is read from environment variables
(loaded from a local .env file if present) so no secrets ever live in code.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# --- MongoDB -----------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "staywise")

# --- Auth ----------------------------------------------------------------
SESSION_SECRET = os.getenv("SESSION_SECRET", "staywise-development-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

# --- CORS / client -------------------------------------------------------
CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")

# --- Razorpay (TEST MODE) -------------------------------------------------
# Get these from the Razorpay Dashboard -> Settings -> API Keys, while the
# dashboard's "Test / Live" toggle (top-right) is set to Test.
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_CURRENCY = os.getenv("RAZORPAY_CURRENCY", "INR")

# --- Refund policy ----------------------------------------------------------
# Guest cancellation:
# 15% is retained as cancellation charge.
# 85% is refunded to the guest.
REFUND_FEE_PERCENT = float(os.getenv("REFUND_FEE_PERCENT", "15"))

if REFUND_FEE_PERCENT < 0 or REFUND_FEE_PERCENT > 100:
    raise ValueError("REFUND_FEE_PERCENT must be between 0 and 100")

REFUND_PERCENT = 100 - REFUND_FEE_PERCENT

# --- Outgoing email (booking confirmations) -------------------------------
# --- Outgoing email -------------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Staywise")

EMAIL_ENABLED = bool(RESEND_API_KEY and EMAIL_FROM)

EMAIL_ENABLED = bool(RESEND_API_KEY and EMAIL_FROM)
RAZORPAY_ENABLED = bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)
