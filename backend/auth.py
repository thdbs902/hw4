"""Accounts: password hashing, signed session cookies, register/login/logout/me.

Password storage (users.password_hash):
- Existing users (from the given DB): pbkdf2_sha256$<salt>$<hex digest>, 120,000 iterations
  (the count isn't stored in the hash; it was confirmed against the test user).
- New users: pbkdf2_sha256$600000$<salt>$<hex digest> (OWASP 2023 iteration count,
  stored in the hash so it can be raised later without breaking old accounts).
Both use a random per-user salt; plain-text passwords are never stored or logged.
"""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

ALGORITHM = "pbkdf2_sha256"
LEGACY_ITERATIONS = 120_000
ITERATIONS = 600_000

SESSION_COOKIE = "cc_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # one week
# Signs session cookies. Set SESSION_SECRET in .env to keep sessions across restarts;
# otherwise a random one is generated and everyone is logged out when the server restarts.
SESSION_SECRET = (os.getenv("SESSION_SECRET") or secrets.token_hex(32)).encode()

MAX_FAILED_LOGINS = 5
FAILED_WINDOW = 15 * 60  # seconds
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------- password hashing ----------


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{ALGORITHM}${ITERATIONS}${salt}${_pbkdf2(password, salt, ITERATIONS)}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) == 4:  # new format with iteration count
        algorithm, iterations, salt, digest = parts
        iterations = int(iterations)
    elif len(parts) == 3:  # format used by the users already in the database
        algorithm, salt, digest = parts
        iterations = LEGACY_ITERATIONS
    else:
        return False
    if algorithm != ALGORITHM:
        return False
    return hmac.compare_digest(_pbkdf2(password, salt, iterations), digest)


# Used when the email doesn't exist so a failed login takes the same time either way.
_DUMMY_HASH = hash_password(secrets.token_hex(16))


# ---------- session cookie (signed, no DB table needed) ----------


def _sign(payload: str) -> str:
    return hmac.new(SESSION_SECRET, payload.encode(), hashlib.sha256).hexdigest()


def make_session(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_MAX_AGE}"
    return f"{payload}.{_sign(payload)}"


def read_session(token: str | None) -> int | None:
    if not token:
        return None
    try:
        user_id, expires, signature = token.split(".")
        if not hmac.compare_digest(_sign(f"{user_id}.{expires}"), signature):
            return None
        if int(expires) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None


def set_session_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        make_session(user_id),
        max_age=SESSION_MAX_AGE,
        httponly=True,  # JavaScript (and injected scripts) can't read it
        samesite="lax",
        secure=False,  # local http dev; set True behind HTTPS
    )


# ---------- simple brute-force protection ----------

_failed: dict[str, deque[float]] = defaultdict(deque)


def _too_many_failures(key: str) -> bool:
    attempts = _failed[key]
    while attempts and attempts[0] < time.time() - FAILED_WINDOW:
        attempts.popleft()
    return len(attempts) >= MAX_FAILED_LOGINS


# ---------- API ----------


class RegisterIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    """Public user info; never includes the password hash."""

    id: int
    first_name: str
    last_name: str
    name: str
    email: str


def _user_out(row: sqlite3.Row) -> UserOut:
    first = row["first_name"] or row["name"].split(" ")[0]
    last = row["last_name"] or " ".join(row["name"].split(" ")[1:])
    return UserOut(id=row["id"], first_name=first, last_name=last, name=row["name"], email=row["email"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_current_user(db_path: str, token: str | None) -> UserOut | None:
    user_id = read_session(token)
    if user_id is None:
        return None
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _user_out(row) if row else None


def build_router(db_path: str) -> APIRouter:
    def connect() -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
    def register(body: RegisterIn, response: Response) -> UserOut:
        email = _normalize_email(body.email)
        first, last = body.first_name.strip(), body.last_name.strip()
        if not EMAIL_RE.match(email):
            raise HTTPException(422, "Please enter a valid email address.")
        if not first or not last:
            raise HTTPException(422, "Please enter your first and last name.")
        if body.password != body.confirm_password:
            raise HTTPException(422, "Passwords do not match.")

        with connect() as conn:
            try:
                cur = conn.execute(
                    "INSERT INTO users (name, email, password_hash, first_name, last_name) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (f"{first} {last}", email, hash_password(body.password), first, last),
                )
            except sqlite3.IntegrityError:
                raise HTTPException(409, "An account with this email already exists.")
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()

        set_session_cookie(response, row["id"])
        return _user_out(row)

    @router.post("/login", response_model=UserOut)
    def login(body: LoginIn, request: Request, response: Response) -> UserOut:
        email = _normalize_email(body.email)
        key = f"{request.client.host if request.client else '?'}|{email}"
        if _too_many_failures(key):
            raise HTTPException(429, "Too many failed attempts. Please wait a few minutes and try again.")

        with connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        ok = verify_password(body.password, row["password_hash"] if row else _DUMMY_HASH)
        if not row or not ok:
            _failed[key].append(time.time())
            # Same message whether the email or the password was wrong.
            raise HTTPException(401, "Incorrect email or password.")

        _failed.pop(key, None)
        set_session_cookie(response, row["id"])
        return _user_out(row)

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    def logout(response: Response) -> None:
        response.delete_cookie(SESSION_COOKIE)

    @router.get("/me", response_model=UserOut | None)
    def me(cc_session: str | None = Cookie(default=None)) -> UserOut | None:
        return get_current_user(db_path, cc_session)

    return router
