from fastapi import FastAPI, HTTPException, Query
from instagrapi import Client
import time
import os
import sqlite3
import threading
import logging
import random
import requests
from typing import Dict
from dotenv import load_dotenv
from instagrapi.mixins.challenge import ChallengeChoice

# Load environment variables
load_dotenv()
# Define base directory for app data (logs, DB, sessions)
BASE_DIR = "app-data"
os.makedirs(BASE_DIR, exist_ok=True)

# Paths
LOG_PATH = os.path.join(BASE_DIR, "myapp.log")
DB_PATH = os.path.join(BASE_DIR, "accounts.db")
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO)

app = FastAPI()
COOLDOWN = 3600
lock = threading.Lock()

ACCOUNTS = [
    {"username": os.getenv("INSTA1_USER"), "password": os.getenv(
        "INSTA1_PASS"), "otp_url": os.getenv("INSTA1_OTP_URL")},
    {"username": os.getenv("INSTA2_USER"), "password": os.getenv(
        "INSTA2_PASS"), "otp_url": os.getenv("INSTA2_OTP_URL")},
    {"username": os.getenv("INSTA3_USER"), "password": os.getenv(
        "INSTA3_PASS"), "otp_url": os.getenv("INSTA3_OTP_URL")},
    {"username": os.getenv("INSTA4_USER"), "password": os.getenv(
        "INSTA4_PASS"), "otp_url": os.getenv("INSTA4_OTP_URL")},
    {"username": os.getenv("INSTA5_USER"), "password": os.getenv(
        "INSTA5_PASS"), "otp_url": os.getenv("INSTA5_OTP_URL")},
    {"username": os.getenv("INSTA6_USER"), "password": os.getenv(
        "INSTA6_PASS"), "otp_url": os.getenv("INSTA6_OTP_URL")},
    {"username": os.getenv("INSTA7_USER"), "password": os.getenv(
        "INSTA7_PASS"), "otp_url": os.getenv("INSTA7_OTP_URL")},
    {"username": os.getenv("INSTA8_USER"), "password": os.getenv(
        "INSTA8_PASS"), "otp_url": os.getenv("INSTA8_OTP_URL")},
    {"username": os.getenv("INSTA9_USER"), "password": os.getenv(
        "INSTA9_PASS"), "otp_url": os.getenv("INSTA9_OTP_URL")},
    {"username": os.getenv("INSTA10_USER"), "password": os.getenv(
        "INSTA10_PASS"), "otp_url": os.getenv("INSTA10_OTP_URL")},
    {"username": os.getenv("INSTA11_USER"), "password": os.getenv(
        "INSTA11_PASS"), "otp_url": os.getenv("INSTA11_OTP_URL")},
    {"username": os.getenv("INSTA12_USER"), "password": os.getenv(
        "INSTA12_PASS"), "otp_url": os.getenv("INSTA12_OTP_URL")},
    {"username": os.getenv("INSTA13_USER"), "password": os.getenv(
        "INSTA13_PASS"), "otp_url": os.getenv("INSTA13_OTP_URL")},
    {"username": os.getenv("INSTA14_USER"), "password": os.getenv(
        "INSTA14_PASS"), "otp_url": os.getenv("INSTA14_OTP_URL")},
    {"username": os.getenv("INSTA15_USER"), "password": os.getenv(
        "INSTA15_PASS"), "otp_url": os.getenv("INSTA15_OTP_URL")},
    {"username": os.getenv("INSTA16_USER"), "password": os.getenv(
        "INSTA16_PASS"), "otp_url": os.getenv("INSTA16_OTP_URL")},
    {"username": os.getenv("INSTA17_USER"), "password": os.getenv(
        "INSTA17_PASS"), "otp_url": os.getenv("INSTA17_OTP_URL")},
    {"username": os.getenv("INSTA18_USER"), "password": os.getenv(
        "INSTA18_PASS"), "otp_url": os.getenv("INSTA18_OTP_URL")},
    {"username": os.getenv("INSTA19_USER"), "password": os.getenv(
        "INSTA19_PASS"), "otp_url": os.getenv("INSTA19_OTP_URL")},
    {"username": os.getenv("INSTA20_USER"), "password": os.getenv(
        "INSTA20_PASS"), "otp_url": os.getenv("INSTA20_OTP_URL")},
    {"username": os.getenv("INSTA21_USER"), "password": os.getenv(
        "INSTA21_PASS"), "otp_url": os.getenv("INSTA21_OTP_URL")},
    {"username": os.getenv("INSTA22_USER"), "password": os.getenv(
        "INSTA22_PASS"), "otp_url": os.getenv("INSTA22_OTP_URL")},
    {"username": os.getenv("INSTA23_USER"), "password": os.getenv(
        "INSTA23_PASS"), "otp_url": os.getenv("INSTA23_OTP_URL")},
    {"username": os.getenv("INSTA24_USER"), "password": os.getenv(
        "INSTA24_PASS"), "otp_url": os.getenv("INSTA24_OTP_URL")},
    {"username": os.getenv("INSTA25_USER"), "password": os.getenv(
        "INSTA25_PASS"), "otp_url": os.getenv("INSTA25_OTP_URL")},
    {"username": os.getenv("INSTA26_USER"), "password": os.getenv(
        "INSTA26_PASS"), "otp_url": os.getenv("INSTA26_OTP_URL")},
    {"username": os.getenv("INSTA27_USER"), "password": os.getenv(
        "INSTA27_PASS"), "otp_url": os.getenv("INSTA27_OTP_URL")},
    {"username": os.getenv("INSTA28_USER"), "password": os.getenv(
        "INSTA28_PASS"), "otp_url": os.getenv("INSTA28_OTP_URL")},
    {"username": os.getenv("INSTA29_USER"), "password": os.getenv(
        "INSTA29_PASS"), "otp_url": os.getenv("INSTA29_OTP_URL")},
    {"username": os.getenv("INSTA30_USER"), "password": os.getenv(
        "INSTA30_PASS"), "otp_url": os.getenv("INSTA30_OTP_URL")},
    {"username": os.getenv("INSTA31_USER"), "password": os.getenv(
        "INSTA31_PASS"), "otp_url": os.getenv("INSTA31_OTP_URL")},
    {"username": os.getenv("INSTA32_USER"), "password": os.getenv(
        "INSTA32_PASS"), "otp_url": os.getenv("INSTA32_OTP_URL")},
    {"username": os.getenv("INSTA33_USER"), "password": os.getenv(
        "INSTA33_PASS"), "otp_url": os.getenv("INSTA33_OTP_URL")},
    {"username": os.getenv("INSTA34_USER"), "password": os.getenv(
        "INSTA34_PASS"), "otp_url": os.getenv("INSTA34_OTP_URL")},
    {"username": os.getenv("INSTA35_USER"), "password": os.getenv(
        "INSTA35_PASS"), "otp_url": os.getenv("INSTA35_OTP_URL")},
    {"username": os.getenv("INSTA36_USER"), "password": os.getenv(
        "INSTA36_PASS"), "otp_url": os.getenv("INSTA36_OTP_URL")},
    {"username": os.getenv("INSTA37_USER"), "password": os.getenv(
        "INSTA37_PASS"), "otp_url": os.getenv("INSTA37_OTP_URL")},
    {"username": os.getenv("INSTA38_USER"), "password": os.getenv(
        "INSTA38_PASS"), "otp_url": os.getenv("INSTA38_OTP_URL")},
    {"username": os.getenv("INSTA39_USER"), "password": os.getenv(
        "INSTA39_PASS"), "otp_url": os.getenv("INSTA39_OTP_URL")},
    {"username": os.getenv("INSTA40_USER"), "password": os.getenv(
        "INSTA40_PASS"), "otp_url": os.getenv("INSTA40_OTP_URL")},
    {"username": os.getenv("INSTA41_USER"), "password": os.getenv(
        "INSTA41_PASS"), "otp_url": os.getenv("INSTA41_OTP_URL")},
    {"username": os.getenv("INSTA42_USER"), "password": os.getenv(
        "INSTA42_PASS"), "otp_url": os.getenv("INSTA42_OTP_URL")},
    {"username": os.getenv("INSTA43_USER"), "password": os.getenv(
        "INSTA43_PASS"), "otp_url": os.getenv("INSTA43_OTP_URL")},
    {"username": os.getenv("INSTA44_USER"), "password": os.getenv(
        "INSTA44_PASS"), "otp_url": os.getenv("INSTA44_OTP_URL")},
    {"username": os.getenv("INSTA45_USER"), "password": os.getenv(
        "INSTA45_PASS"), "otp_url": os.getenv("INSTA45_OTP_URL")},
    {"username": os.getenv("INSTA46_USER"), "password": os.getenv(
        "INSTA46_PASS"), "otp_url": os.getenv("INSTA46_OTP_URL")},
    {"username": os.getenv("INSTA47_USER"), "password": os.getenv(
        "INSTA47_PASS"), "otp_url": os.getenv("INSTA47_OTP_URL")},
    {"username": os.getenv("INSTA48_USER"), "password": os.getenv(
        "INSTA48_PASS"), "otp_url": os.getenv("INSTA48_OTP_URL")},
    {"username": os.getenv("INSTA49_USER"), "password": os.getenv(
        "INSTA49_PASS"), "otp_url": os.getenv("INSTA49_OTP_URL")},
    {"username": os.getenv("INSTA50_USER"), "password": os.getenv(
        "INSTA50_PASS"), "otp_url": os.getenv("INSTA50_OTP_URL")},
    {"username": os.getenv("INSTA51_USER"), "password": os.getenv(
        "INSTA51_PASS"), "otp_url": os.getenv("INSTA51_OTP_URL")},
    {"username": os.getenv("INSTA52_USER"), "password": os.getenv(
        "INSTA52_PASS"), "otp_url": os.getenv("INSTA52_OTP_URL")},
    {"username": os.getenv("INSTA53_USER"), "password": os.getenv(
        "INSTA53_PASS"), "otp_url": os.getenv("INSTA53_OTP_URL")},
    {"username": os.getenv("INSTA54_USER"), "password": os.getenv(
        "INSTA54_PASS"), "otp_url": os.getenv("INSTA54_OTP_URL")},
    {"username": os.getenv("INSTA55_USER"), "password": os.getenv(
        "INSTA55_PASS"), "otp_url": os.getenv("INSTA55_OTP_URL")},
    {"username": os.getenv("INSTA56_USER"), "password": os.getenv(
        "INSTA56_PASS"), "otp_url": os.getenv("INSTA56_OTP_URL")},
    {"username": os.getenv("INSTA57_USER"), "password": os.getenv(
        "INSTA57_PASS"), "otp_url": os.getenv("INSTA57_OTP_URL")},
    {"username": os.getenv("INSTA58_USER"), "password": os.getenv(
        "INSTA58_PASS"), "otp_url": os.getenv("INSTA58_OTP_URL")},
    {"username": os.getenv("INSTA59_USER"), "password": os.getenv(
        "INSTA59_PASS"), "otp_url": os.getenv("INSTA59_OTP_URL")},
    {"username": os.getenv("INSTA60_USER"), "password": os.getenv(
        "INSTA60_PASS"), "otp_url": os.getenv("INSTA60_OTP_URL")},
    {"username": os.getenv("INSTA61_USER"), "password": os.getenv(
        "INSTA61_PASS"), "otp_url": os.getenv("INSTA61_OTP_URL")},
    {"username": os.getenv("INSTA62_USER"), "password": os.getenv(
        "INSTA62_PASS"), "otp_url": os.getenv("INSTA62_OTP_URL")},
    {"username": os.getenv("INSTA63_USER"), "password": os.getenv(
        "INSTA63_PASS"), "otp_url": os.getenv("INSTA63_OTP_URL")},
    {"username": os.getenv("INSTA64_USER"), "password": os.getenv(
        "INSTA64_PASS"), "otp_url": os.getenv("INSTA64_OTP_URL")},
    {"username": os.getenv("INSTA65_USER"), "password": os.getenv(
        "INSTA65_PASS"), "otp_url": os.getenv("INSTA65_OTP_URL")},
    {"username": os.getenv("INSTA66_USER"), "password": os.getenv(
        "INSTA66_PASS"), "otp_url": os.getenv("INSTA66_OTP_URL")},
    {"username": os.getenv("INSTA67_USER"), "password": os.getenv(
        "INSTA67_PASS"), "otp_url": os.getenv("INSTA67_OTP_URL")},
    {"username": os.getenv("INSTA68_USER"), "password": os.getenv(
        "INSTA68_PASS"), "otp_url": os.getenv("INSTA68_OTP_URL")},
    {"username": os.getenv("INSTA69_USER"), "password": os.getenv(
        "INSTA69_PASS"), "otp_url": os.getenv("INSTA69_OTP_URL")},
    {"username": os.getenv("INSTA70_USER"), "password": os.getenv(
        "INSTA70_PASS"), "otp_url": os.getenv("INSTA70_OTP_URL")},
    {"username": os.getenv("INSTA71_USER"), "password": os.getenv(
        "INSTA71_PASS"), "otp_url": os.getenv("INSTA71_OTP_URL")},
    {"username": os.getenv("INSTA72_USER"), "password": os.getenv(
        "INSTA72_PASS"), "otp_url": os.getenv("INSTA72_OTP_URL")},
    {"username": os.getenv("INSTA73_USER"), "password": os.getenv(
        "INSTA73_PASS"), "otp_url": os.getenv("INSTA73_OTP_URL")},
    {"username": os.getenv("INSTA74_USER"), "password": os.getenv(
        "INSTA74_PASS"), "otp_url": os.getenv("INSTA74_OTP_URL")},
    {"username": os.getenv("INSTA75_USER"), "password": os.getenv(
        "INSTA75_PASS"), "otp_url": os.getenv("INSTA75_OTP_URL")},
    {"username": os.getenv("INSTA76_USER"), "password": os.getenv(
        "INSTA76_PASS"), "otp_url": os.getenv("INSTA76_OTP_URL")},
    {"username": os.getenv("INSTA77_USER"), "password": os.getenv(
        "INSTA77_PASS"), "otp_url": os.getenv("INSTA77_OTP_URL")},
    {"username": os.getenv("INSTA78_USER"), "password": os.getenv(
        "INSTA78_PASS"), "otp_url": os.getenv("INSTA78_OTP_URL")},
    {"username": os.getenv("INSTA79_USER"), "password": os.getenv(
        "INSTA79_PASS"), "otp_url": os.getenv("INSTA79_OTP_URL")},
    {"username": os.getenv("INSTA80_USER"), "password": os.getenv(
        "INSTA80_PASS"), "otp_url": os.getenv("INSTA80_OTP_URL")},
    {"username": os.getenv("INSTA81_USER"), "password": os.getenv(
        "INSTA81_PASS"), "otp_url": os.getenv("INSTA81_OTP_URL")},
    {"username": os.getenv("INSTA82_USER"), "password": os.getenv(
        "INSTA82_PASS"), "otp_url": os.getenv("INSTA82_OTP_URL")},
    {"username": os.getenv("INSTA83_USER"), "password": os.getenv(
        "INSTA83_PASS"), "otp_url": os.getenv("INSTA83_OTP_URL")},
    {"username": os.getenv("INSTA84_USER"), "password": os.getenv(
        "INSTA84_PASS"), "otp_url": os.getenv("INSTA84_OTP_URL")},
    {"username": os.getenv("INSTA85_USER"), "password": os.getenv(
        "INSTA85_PASS"), "otp_url": os.getenv("INSTA85_OTP_URL")},
    {"username": os.getenv("INSTA86_USER"), "password": os.getenv(
        "INSTA86_PASS"), "otp_url": os.getenv("INSTA86_OTP_URL")},
    {"username": os.getenv("INSTA87_USER"), "password": os.getenv(
        "INSTA87_PASS"), "otp_url": os.getenv("INSTA87_OTP_URL")},
    {"username": os.getenv("INSTA88_USER"), "password": os.getenv(
        "INSTA88_PASS"), "otp_url": os.getenv("INSTA88_OTP_URL")},
    {"username": os.getenv("INSTA89_USER"), "password": os.getenv(
        "INSTA89_PASS"), "otp_url": os.getenv("INSTA89_OTP_URL")},
    {"username": os.getenv("INSTA90_USER"), "password": os.getenv(
        "INSTA90_PASS"), "otp_url": os.getenv("INSTA90_OTP_URL")},
    {"username": os.getenv("INSTA91_USER"), "password": os.getenv(
        "INSTA91_PASS"), "otp_url": os.getenv("INSTA91_OTP_URL")},
    {"username": os.getenv("INSTA92_USER"), "password": os.getenv(
        "INSTA92_PASS"), "otp_url": os.getenv("INSTA92_OTP_URL")},
    {"username": os.getenv("INSTA93_USER"), "password": os.getenv(
        "INSTA93_PASS"), "otp_url": os.getenv("INSTA93_OTP_URL")},
    {"username": os.getenv("INSTA94_USER"), "password": os.getenv(
        "INSTA94_PASS"), "otp_url": os.getenv("INSTA94_OTP_URL")},
    {"username": os.getenv("INSTA95_USER"), "password": os.getenv(
        "INSTA95_PASS"), "otp_url": os.getenv("INSTA95_OTP_URL")},
    {"username": os.getenv("INSTA96_USER"), "password": os.getenv(
        "INSTA96_PASS"), "otp_url": os.getenv("INSTA96_OTP_URL")},
    {"username": os.getenv("INSTA97_USER"), "password": os.getenv(
        "INSTA97_PASS"), "otp_url": os.getenv("INSTA97_OTP_URL")},
    {"username": os.getenv("INSTA98_USER"), "password": os.getenv(
        "INSTA98_PASS"), "otp_url": os.getenv("INSTA98_OTP_URL")},
    {"username": os.getenv("INSTA99_USER"), "password": os.getenv(
        "INSTA99_PASS"), "otp_url": os.getenv("INSTA99_OTP_URL")},
    {"username": os.getenv("INSTA100_USER"), "password": os.getenv(
        "INSTA100_PASS"), "otp_url": os.getenv("INSTA100_OTP_URL")},
]


def get_otp(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()
    # Support both formats: nested under 'data' or at root
    if "totp" in json_data:
        otp = json_data["totp"]
    else:
        otp = json_data.get("data", {}).get("totp")
    if otp is None:
        raise KeyError("OTP not found in the response.")
    return otp


def get_code_from_sms(username):
    while True:
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit() and len(code) == 6:
            return code


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return None
    return False


def change_password_handler(username):
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 10))
    logger.info(f"Generated new password for {username}: {password}")
    return password


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                otp_url TEXT,
                last_used REAL DEFAULT 0
            )
        """)
        for acc in ACCOUNTS:
            if acc["username"] and acc["password"]:
                conn.execute("""
                    INSERT OR IGNORE INTO accounts (username, password, otp_url) VALUES (?, ?, ?)
                """, (acc["username"], acc["password"], acc["otp_url"]))


init_db()

clients: Dict[str, Client] = {}


def get_available_account():
    now = time.time()
    with lock, sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT username, password, otp_url FROM accounts WHERE ? - last_used >= ? ORDER BY last_used ASC LIMIT 1",
            (now, COOLDOWN)
        ).fetchone()
        if row:
            username, password, otp_url = row
            conn.execute(
                "UPDATE accounts SET last_used = ? WHERE username = ?", (now, username))
            return {"username": username, "password": password, "otp_url": otp_url}
    return None


def get_client_for(acc):
    username = acc["username"]
    if username in clients:
        return clients[username]
    cl = Client()
    cl.challenge_code_handler = challenge_code_handler
    cl.change_password_handler = change_password_handler
    session_path = os.path.join(SESSION_DIR, f"{username}_session.json")
    otp = get_otp(acc["otp_url"]) if acc["otp_url"] else None
    if os.path.exists(session_path):
        cl.load_settings(session_path)
    cl.login(username, acc["password"], verification_code=otp)
    cl.dump_settings(session_path)
    clients[username] = cl
    return cl


def fetch_updates(cl, username):
    uid = cl.user_id_from_username(username)
    posts = cl.user_medias(uid, 10)
    stories = cl.user_stories(uid)
    return [p.dict() for p in posts], [s.dict() for s in stories]


@app.on_event("startup")
async def on_startup():
    init_db()
    logger.info("Initialized accounts database")
    # Preload all clients to warm sessions
    with sqlite3.connect(DB_PATH) as conn:
        for row in conn.execute("SELECT username, password, otp_url FROM accounts").fetchall():
            acc = {"username": row[0], "password": row[1], "otp_url": row[2]}
            try:
                get_client_for(acc)
                logger.info(f"Preloaded client for {acc['username']}")
            except Exception as e:
                logger.error(f"Failed to preload client for {acc['username']}: {e}")


@app.get("/media_info")
async def media_info(
    media_pk: int = Query(None, description="Instagram media PK"),
    media_url: str = Query(
        None, description="Instagram post URL, e.g. https://instagram.com/p/..."),
):
    if not media_pk and not media_url:
        raise HTTPException(
            status_code=400, detail="Provide either media_pk or media_url")

    # Skip cooldown checks: directly use any client (round-robin)
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT username, password, otp_url FROM accounts ORDER BY last_used ASC LIMIT 1").fetchone()
        if not row:
            raise HTTPException(
                status_code=500, detail="No accounts available")
        acc = {"username": row[0], "password": row[1], "otp_url": row[2]}

    cl = get_client_for(acc)

    try:
        if media_url and not media_pk:
            media_pk = cl.media_pk_from_url(media_url)
        media_info = cl.media_info(media_pk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"media_info error: {e}")

    return {
        "account": acc["username"],
        "media_pk": media_pk,
        "media_info": media_info.dict()
    }


@app.get("/check_posts")
async def check_posts(
    target_username: str = Query(..., description="Target Instagram username"),
    limit: int = Query(10, description="Number of posts to fetch")
):
    acc = get_available_account()
    if not acc:
        raise HTTPException(
            status_code=429, detail="All accounts are on cooldown.")
    cl = get_client_for(acc)
    try:
        uid = cl.user_id_from_username(target_username)
        posts = cl.user_medias(uid, limit)
        posts = [p.dict() for p in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"account": acc["username"], "target": target_username, "posts": posts}


@app.get("/check_stories")
async def check_stories(
    target_username: str = Query(..., description="Target Instagram username"),
    limit: int = Query(10, description="Number of stories to fetch")
):
    acc = get_available_account()
    if not acc:
        raise HTTPException(
            status_code=429, detail="All accounts are on cooldown.")
    cl = get_client_for(acc)
    try:
        uid = cl.user_id_from_username(target_username)
        stories = cl.user_stories(uid)
        stories = [s.dict() for s in stories][:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"account": acc["username"], "target": target_username, "stories": stories}
