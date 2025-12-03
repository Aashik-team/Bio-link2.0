#𝐀𝐚𝐬𝐡𝐢𝐤 𝐓ᴇᴀᴍ
import re
import asyncio
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Biolink import Biolink as app
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, OTHER_LOGS, BOT_USERNAME
from Biolink.helper.auth import get_auth_users  # To fetch auth list

# ----------------- MongoDB Setup -----------------
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["BioFilterBot"]
bio_filter_collection = db["bio_filter"]

# ----------------- Regex Patterns -----------------
url_pattern = re.compile(r"(https?://|www\.)[^\s]+", re.IGNORECASE)
username_pattern = re.compile(r"@[\w]+", re.IGNORECASE)

# ----------------- Bio Filter Status -----------------
async def get_bio_filter_status():
    doc = await bio_filter_collection.find_one({"filter": "enabled"})
    return bool(doc and doc.get("status", False))

async def set_bio_filter_status(enabled: bool):
    await bio_filter_collection.update_one(
        {"filter": "enabled"},
        {"$set": {"status": enabled}},
        upsert=True
    )

# ----------------- Check Admin -----------------
async def is_admins(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# ----------------- Bio Filter Handler -----------------
@app.on_message(filters.group & filters.text & ~filters.command([""]))
async def check_bio(client, message):
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    # Admin check
    if await is_admins(client, chat_id, user.id):
        return

    # Auth check (Ignore if the user is authorized)
    data = await get_auth_users(chat_id)
    if user.id in data.get("auth_users", []):
        return

    # Filter status check
    if not await get_bio_filter_status():
        return

    try:
        user_chat = await client.get_chat(user.id)
        bio = getattr(user_chat, "bio", "") or ""
    except Exception as e:
        print(f"[get_chat ERROR] {e}")
        bio = ""

    # If bio contains link or username
    if bio and (re.search(url_pattern, bio) or re.search(username_pattern, bio)):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return

        mention = f"[{user.first_name}](tg://user?id={user.id})"
        username = f"@{user.username}" if user.username else "No username"
        group_name = message.chat.title

        log_text = f"""
**Bio Filter Log**
**Full Name:** {user.first_name} {user.last_name or ''}
**Username:** {username}
**User ID:** `{user.id}`
**Mention:** {mention}
**Group Name:** `{group_name}`
**Group Chat ID:** `{chat_id}`
**User Bio:** `{bio}`
**User Message:** `{message.text or 'Media Message'}`
**Bot Name:** @{BOT_USERNAME}
"""

        # Send log
        try:
            await client.send_message(
                OTHER_LOGS,
                log_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]]
                )
            )
        except Exception as e:
            print(f"[LOG SEND ERROR] {e}")

        # Warn user
        try:
            warn_msg = await message.reply_text(
                f"{mention}, please remove links or usernames from your bio!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close")]]),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            await asyncio.sleep(10)
            await warn_msg.delete()
        except Exception as e:
            print(f"[WARN MSG ERROR] {e}")

