from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

from config import JWT_ALGORITHM, JWT_EXPIRE_DAYS, SESSION_SECRET
from db import users_col


def make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def password_hash(value: str) -> str:
    return bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode()


def password_matches(value: str, hashed: str) -> bool:
    return bcrypt.checkpw(value.encode(), hashed.encode())


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {"id": user["_id"], "name": user["name"], "email": user["email"], "phone": user.get("phone", ""), "role": user["role"]}


def token_for(user: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": user["_id"], "role": user["role"], "iat": now, "exp": now + timedelta(days=JWT_EXPIRE_DAYS)},
        SESSION_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def user_by_email(email: str) -> dict[str, Any] | None:
    return users_col.find_one({"email": email.strip().lower()})


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    try:
        payload = jwt.decode(authorization[7:], SESSION_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(401, "Invalid session") from exc
    user = users_col.find_one({"_id": payload.get("sub")})
    if not user:
        raise HTTPException(401, "Session expired")
    return user


def require_owner(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user["role"] != "owner":
        raise HTTPException(403, "Owner access required")
    return user
