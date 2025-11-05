import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pytgcalls import PyTgCalls

from assistant.session.manager import SessionManager

logger = logging.getLogger(__name__)

def add_handlers(app: Client, pytgcalls: PyTgCalls):
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
    async def session_handler(_, message: Message):
        """Handles the /session command to start a new private call."""
        session_manager = SessionManager(app, pytgcalls, message.from_user)
        await session_manager.start_session()