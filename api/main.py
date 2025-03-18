import email
import imaplib
import re
import random
import os
import logging
import random
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl
from instagrapi import Client
from typing import List
from instagrapi.exceptions import LoginRequired
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()

# Retrieve credentials from environment variables
USERNAME = os.environ.get("INSTAGRAM_USERNAME")
PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
CHALLENGE_EMAIL = os.environ.get("CHALLENGE_EMAIL")
CHALLENGE_PASSWORD = os.environ.get("CHALLENGE_PASSWORD")
CODE = str(os.environ.get("CODE_2FA"))
SETTINGS_PATH = "ig_settings.json"

# List your free proxies here.
proxies = [
    # "http://eibylrxi:qq84p9fff1v5@38.154.227.167:5868"
]

app = FastAPI()
cl = Client()

def rotate_proxy(client: Client):
    """Selects a random proxy from the list and sets it on the client."""
    if(proxies):
        chosen_proxy = random.choice(proxies)
        cl.set_proxy(chosen_proxy)
        logger.info(f"Using proxy: {chosen_proxy}")

def get_code_from_email(username):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(CHALLENGE_EMAIL, CHALLENGE_PASSWORD)
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = payload.get_payload(decode=True).decode()
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
    return False

def get_code_from_sms(username):
    while True:
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit():
            return code
    return None

def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False

def change_password_handler(username):
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 10))
    logger.info(f"your new password is: {password}")
    return password


# Attempt to load session settings to reuse cookies and device info
def first_time():
    try:
        cl.load_settings(SETTINGS_PATH)
        logger.info("Loaded session settings.")
    except FileNotFoundError:
        logger.info("No saved session settings found, proceeding with login.")

    # Log in to Instagram
    try:
        if CODE:
            cl.login(USERNAME, PASSWORD, verification_code=CODE)
        else:
            cl.login(USERNAME, PASSWORD)
        logger.info("Login successful.")
    except Exception as e:
        logger.error(f"Error during login: {e}")
        exit(1)

    # Save session settings for future use to avoid repeated logins
    cl.dump_settings(SETTINGS_PATH)
    logger.info("Session settings saved.")


def login_user():
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """

    session = cl.load_settings(SETTINGS_PATH)

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.challenge_code_handler = challenge_code_handler
            cl.change_password_handler = change_password_handler
            cl.login(USERNAME, PASSWORD)
            rotate_proxy(cl)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(USERNAME, PASSWORD)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")


try:
    cl.load_settings(SETTINGS_PATH)
except FileNotFoundError:
    first_time()
login_user()


# Define a model for the media data to be returned by the API
class Media(BaseModel):
    id: int
    url: HttpUrl
    caption: str
    media_type: int           # 1 = image, 2 = video, etc.
    taken_at: datetime        # Converted from a Unix timestamp
    like_count: int
    comment_count: int
    video_url: Optional[HttpUrl] = None  # Only applicable for video posts


@app.get("/posts", response_model=List[Media])
def get_post(username: str = Query(..., description="Instagram username to fetch posts from")):
    try:
        # Convert the provided username to a user ID
        user_info = cl.user_info_by_username_v1(username).model_dump()
        # print(f"{target_user_id}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {e}")

    try:
        # adds a random delay between 1 and 3 seconds after each request
        cl.delay_range = [1, 3]
        # Fetch the latest posts (adjust the amount as needed)
        medias = cl.user_medias_v1(user_info["pk"], amount=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {e}")

    # Process the media data to match our Media model
    posts = []
    for media in medias:
        # Determine the URL: try media_url first, then thumbnail_url
        url = None
        if hasattr(media, "media_url") and media.media_url:
            url = str(media.media_url)
        elif hasattr(media, "thumbnail_url") and media.thumbnail_url:
            url = str(media.thumbnail_url)
        # If no valid URL, skip this media item
        if not url or url.lower() == "none":
            continue

        # Convert taken_at: if it's an integer, convert from Unix timestamp; otherwise, use as-is
        taken_at = datetime.fromtimestamp(media.taken_at) if isinstance(media.taken_at, int) else media.taken_at

        posts.append(Media(
            id=media.pk,
            # Use media_url if available, otherwise fallback to thumbnail_url
            url=str(media.media_url) if hasattr(media, "media_url") and media.media_url else str(media.thumbnail_url),
            caption=media.caption_text or "",
            media_type=media.media_type,
            taken_at = taken_at,
            like_count=media.like_count,
            comment_count=media.comment_count,
            video_url=str(media.video_url) if hasattr(media, "video_url") and media.video_url else None,
        ))
    return posts


# New model for detailed story information
class Story(BaseModel):
    id: int
    url: HttpUrl
    media_type: int
    taken_at: datetime
    expiring_at: Optional[datetime] = None  # When the story will expire


@app.get("/stories", response_model=List[Story])
def get_stories(username: str = Query(..., description="Instagram username to fetch stories from")):
    try:
        user_info = cl.user_info_by_username_v1(username).model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {e}")

    try:
        # Retrieve the user's stories using instagrapi's user_stories method.
        cl.delay_range = [1, 3]
        stories = cl.user_stories(user_info["pk"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stories: {e}")

    output = []
    for story in stories:
        url = None
        if hasattr(story, "media_url") and story.media_url:
            url = str(story.media_url)
        elif hasattr(story, "thumbnail_url") and story.thumbnail_url:
            url = str(story.thumbnail_url)
        if not url or url.lower() == "none":
            continue

        taken_at = datetime.fromtimestamp(story.taken_at) if isinstance(story.taken_at, int) else story.taken_at
        expiring_at = None
        if hasattr(story, "expiring_at") and story.expiring_at:
            expiring_at = (datetime.fromtimestamp(story.expiring_at)
                           if isinstance(story.expiring_at, int) else story.expiring_at)
        output.append(Story(
            id=story.pk,
            url=url,
            media_type=story.media_type,
            taken_at=taken_at,
            expiring_at=expiring_at,
        ))
    output.reverse()
    return output
