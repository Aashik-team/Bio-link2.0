import asyncio
import importlib
from pyrogram import idle
from MAFU import MAFU
from MAFU.modules import ALL_MODULES
from config import LOGGER_ID, BOT_USERNAME

loop = asyncio.get_event_loop()

async def roy_bot():
    for all_module in ALL_MODULES:
        importlib.import_module("MAFU.modules." + all_module)
    print("• @AviaBeatzBot B𝗈𝗍 Started Successfully.")
    await idle()
    print("• Don't edit baby, otherwise you get an error: @networkxlog")
    await MAFU.send_message(LOGGER_ID, "**✦ ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ.\n\n✦ ᴊᴏɪɴ - @shivang_xd**")

if __name__ == "__main__":
    loop.run_until_complete(roy_bot())





