import logging
from pyrogram import Client
from pyrogram.types import User
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall

# This would be a shared Redis/DB store in a real multi-worker setup
ACTIVE_SESSIONS = {}

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages the lifecycle of a single private voice session."""
    
    def __init__(self, app: Client, pytgcalls: PyTgCalls, user: User):
        self.app = app
        self.pytgcalls = pytgcalls
        self.user = user

    async def start_session(self):
        """Creates a private group and starts the voice session."""
        logger.info(f"Session request from {self.user.first_name} ({self.user.id})")
        ack_message = await self.app.send_message(
            self.user.id,
            "🚀 Creating your private session room... Please wait a moment."
        )

        try:
            # 1. Create a new private group (supergroup for more features)
            group = await self.app.create_supergroup(
                title=f"AI Session - {self.user.first_name} - {self.user.id}",
                description="A private room for your AI voice session."
            )
            chat_id = group.id
            logger.info(f"Created group {chat_id} for user {self.user.id}")

            # 2. Add the user to the group
            await self.app.add_chat_members(chat_id, self.user.id)

            # 3. Join the voice chat
            await self.pytgcalls.join_group_call(
                chat_id,
                AudioPiped('input.raw', is_stereo=False), # A placeholder input stream
            )
            ACTIVE_SESSIONS[chat_id] = {'user_id': self.user.id, 'status': 'active'}
            logger.info(f"AI joined voice chat in new private group: {chat_id}")

            # 4. Get an invite link to the group
            invite_link = await self.app.export_chat_invite_link(chat_id)

            # 5. Send the final invitation to the user
            await ack_message.edit_text(
                "✅ Your private room is ready!\n\n"
                f"Click the link below to join the live call. I'll be waiting for you inside!\n\n"
                f"➡️ {invite_link}",
                disable_web_page_preview=True
            )
            logger.info(f"Sent invite link for {chat_id} to user {self.user.id}")

        except Exception as e:
            logger.error(f"Failed to create session for {self.user.id}: {e}", exc_info=True)
            await ack_message.edit_text("❌ Sorry, I encountered an error. Please try again later.")

    async def end_session(self, chat_id: int):
        """Cleans up a session after it has ended."""
        if chat_id in ACTIVE_SESSIONS:
            logger.info(f"Cleaning up session for chat {chat_id}")
            del ACTIVE_SESSIONS[chat_id]
            # In a real app, you might archive the group or delete it.
            await self.app.leave_chat(chat_id)