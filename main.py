import asyncio
import logging
from dotenv import load_dotenv

from pyrogram import Client
from pytgcalls import PyTgCalls

from assistant.bot.handlers import add_handlers
from assistant.voice.processing import add_voice_handlers

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

# --- Initialize Clients ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "private_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

pytgcalls = PyTgCalls(app)


async def main():
    """Main function to start the bot and voice client."""
    logger.info("Starting AI Voice Assistant...")
    
    # Add command and message handlers
    add_handlers(app, pytgcalls)
    
    # Add voice stream and event handlers
    add_voice_handlers(pytgcalls)
    
    try:
        await app.start()
        await pytgcalls.start()
        
        bot_info = await app.get_me()
        logger.info(f"Bot @{bot_info.username} started successfully!")
        
        # Keep the application running indefinitely
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"An error occurred during startup: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        await pytgcalls.stop()
        await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown requested by user.")