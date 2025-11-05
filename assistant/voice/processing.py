import logging
import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

from assistant.core.speech import text_to_speech
from assistant.core.ai import get_ai_response

logger = logging.getLogger(__name__)

# This would be a shared Redis/DB store in a real multi-worker setup
from assistant.session.manager import ACTIVE_SESSIONS

def add_voice_handlers(pytgcalls: PyTgCalls):
    """Adds all the PyTgCalls event handlers."""

    @pytgcalls.on_kicked()
    async def on_kicked(_, chat_id: int):
        if chat_id in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[chat_id]
        logger.warning(f"Kicked from voice chat: {chat_id}")

    @pytgcalls.on_closed_voice_chat()
    async def on_closed(_, chat_id: int):
        if chat_id in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[chat_id]
        logger.info(f"Voice chat closed: {chat_id}")

    @pytgcalls.on_stream_end()
    async def on_stream_end(_, update):
        """Restarts the output stream if it ends, to keep the bot 'on the line'."""
        chat_id = update.chat_id
        if chat_id in ACTIVE_SESSIONS:
            await pytgcalls.change_stream(chat_id, AudioPiped('input.raw', is_stereo=False))

    # This is the most complex part. Real-time audio processing requires
    # handling raw audio frames from `pytgcalls` directly.
    # The following is a simplified simulation loop.
    async def voice_processor_loop():
        while True:
            await asyncio.sleep(10) # Run this check every 10 seconds
            for chat_id, session_info in list(ACTIVE_SESSIONS.items()):
                if session_info.get('status') == 'active':
                    # --- PRODUCTION LOGIC WOULD GO HERE ---
                    # 1. Capture raw audio stream for the user_id in this chat_id.
                    # 2. Use a streaming Speech-to-Text service.
                    # 3. Once a phrase is detected, pass it to the AI.
                    
                    # --- SIMULATED LOGIC FOR DEMONSTRATION ---
                    logger.info(f"Simulating AI response for session in chat {chat_id}")
                    
                    # Simulate user input and AI response
                    simulated_text = "Welcome to your private session! I am listening."
                    ai_response = await get_ai_response(simulated_text, session_info['user_id'])
                    
                    # Convert response to speech and play it
                    audio_file = await text_to_speech(ai_response)
                    
                    if audio_file:
                        try:
                            await pytgcalls.change_stream(chat_id, AudioPiped(audio_file))
                            logger.info(f"Played welcome message in {chat_id}")
                        except Exception as e:
                            logger.error(f"Error playing audio in {chat_id}: {e}")
                        # In production, manage audio file cleanup carefully.
                    
                    # Update status to avoid sending the welcome message again
                    ACTIVE_SESSIONS[chat_id]['status'] = 'welcomed'

    # Start the background task when handlers are added
    asyncio.create_task(voice_processor_loop())