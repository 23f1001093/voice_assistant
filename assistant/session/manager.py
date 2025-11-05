import asyncio
import logging
from pyrogram import Client
from pyrogram.types import User
from tgcaller import TgCaller
from tgcaller.exceptions import CallError  # <--- THIS EXISTS IN YOUR INSTALLATION

from assistant.core.speech import text_to_speech
from assistant.core.ai import get_ai_response

ACTIVE_SESSIONS = {}
logger = logging.getLogger(__name__)

# With tgcaller, you create one global instance
caller = None

def initialize_caller(app: Client):
    """Initializes the global TgCaller instance."""
    global caller
    if caller is None:
        caller = TgCaller(app)
        asyncio.create_task(caller.start())
        logger.info("TgCaller instance created and starting.")

class SessionManager:
    def __init__(self, app: Client, user: User):
        self.app = app
        self.user = user
        # The 'caller' is now a shared global instance, not per-session
        self.chat_id = None

    async def start_session(self):
        global caller
        if not caller:
            logger.error("TgCaller is not initialized!")
            return

        logger.info(f"Session request from {self.user.first_name} ({self.user.id})")
        ack_message = await self.app.send_message(
            self.user.id, "🚀 Creating your private session room..."
        )
        try:
            group = await self.app.create_supergroup(
                title=f"AI Session - {self.user.first_name} ({self.user.id})",
            )
            self.chat_id = group.id
            logger.info(f"Created group {self.chat_id} for user {self.user.id}")
            await self.app.add_chat_members(self.chat_id, self.user.id)

            await caller.join_call(self.chat_id)

            self._register_event_handlers()
            ACTIVE_SESSIONS[self.chat_id] = {'user_id': self.user.id, 'status': 'starting'}
            logger.info(f"AI joined voice chat in new private group: {self.chat_id}")

            invite_link = await self.app.export_chat_invite_link(self.chat_id)
            await ack_message.edit_text(
                f"✅ Your private room is ready!\n\nClick to join:\n➡️ {invite_link}",
                disable_web_page_preview=True
            )
            logger.info(f"Sent invite link for {self.chat_id} to user {self.user.id}")
            asyncio.create_task(self.welcome_task())
        except Exception as e:
            logger.error(f"Failed to create session for {self.user.id}: {e}", exc_info=True)
            await ack_message.edit_text("❌ Sorry, an error occurred. Please try again.")

    def _register_event_handlers(self):
        """Binds event handlers directly to the global caller instance."""
        
        @caller.on_stream_end()
        async def on_stream_end(_, update):
            if update.chat_id == self.chat_id:
                try:
                    await caller.play(self.chat_id, 'input.raw', from_cache=False)
                except CallError as e:
                    logger.warning(f"Could not play silence: {e}")
                    await self.end_session()

    async def welcome_task(self):
        global caller
        await asyncio.sleep(10)
        if self.chat_id in ACTIVE_SESSIONS:
            logger.info(f"Playing welcome message for session {self.chat_id}")
            welcome_text = "Welcome to your private session. I am now listening."
            audio_file = await text_to_speech(welcome_text)
            if audio_file:
                try:
                    await caller.play(self.chat_id, audio_file)
                except CallError as e:
                    logger.warning(f"Could not play welcome message in {self.chat_id}: {e}")
                    await self.end_session()
            ACTIVE_SESSIONS[self.chat_id]['status'] = 'active'

    async def end_session(self):
        global caller
        if self.chat_id in ACTIVE_SESSIONS:
            logger.info(f"Cleaning up session for chat {self.chat_id}")
            chat_id_to_clean = self.chat_id
            if chat_id_to_clean in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[chat_id_to_clean]
            
            try:
                await caller.leave_call(chat_id_to_clean)
            except CallError as e:
                logger.info(f"Could not leave call: {e}")
            
            await self.app.leave_chat(chat_id_to_clean)
            logger.info(f"Session {chat_id_to_clean} has been fully terminated.")