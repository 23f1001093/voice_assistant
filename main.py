import os
import logging
from dotenv import load_dotenv
from pyrogram import Client
from assistant.bot.handlers import add_handlers
# Import the new initializer function
from assistant.session.manager import initialize_caller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# --- ADD THIS DEBUGGING LINE ---
print(f"BOT_TOKEN loaded: {os.getenv('BOT_TOKEN')}")
# -------------------------------

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')


# Main application entry point
async def main():
    # Initialize the Pyrogram client
    app = Client(
        "live_callbot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Initialize the global TgCaller instance
    initialize_caller(app)

    # Add command and message handlers
    add_handlers(app)

    # Start the bot
    try:
        await app.start()
        logger.info(f"Bot @{(await app.get_me()).username} started successfully!")
        logger.info("Ready to create private sessions. Send /session to the bot.")
        # Keep the bot running indefinitely
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        logger.error(f"An error occurred during bot startup: {e}", exc_info=True)
    finally:
        await app.stop()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())