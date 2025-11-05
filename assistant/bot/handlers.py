import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from assistant.session.manager import SessionManager

logger = logging.getLogger(__name__)

def add_handlers(app: Client):
    """Adds all the command handlers to the Pyrogram client."""

    @app.on_message(filters.command("start"))
    async def start_handler(_, message: Message):
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(
                "Hello! I am your personal AI voice assistant.\n\n"
                "Send `/session` to start a private live call with me."
            )
        else:
            await message.reply("Please start me in a private chat to create a session.")

    @app.on_message(filters.command("session") & filters.private)
    async def session_handler(app_client: Client, message: Message):
        """Handles the /session command to start a new private call."""
        logger.info(f"Creating a new SessionManager for user {message.from_user.id}")
        # Each session gets its own manager instance for complete isolation.
        session_manager = SessionManager(app_client, message.from_user)
        await session_manager.start_session()