import tempfile
import logging
from gtts import gTTS
import speech_recognition as sr

logger = logging.getLogger(__name__)

async def text_to_speech(text: str) -> str | None:
    """Converts text to a temporary MP3 file and returns its path."""
    try:
        tts = gTTS(text=text, lang='en')
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        logger.info(f"Generated TTS file: {fp.name}")
        return fp.name
    except Exception as e:
        logger.error(f"gTTS Error: {e}", exc_info=True)
        return None

async def speech_to_text(audio_file_path: str) -> str | None:
    """
    Transcribes speech from an audio file.
    Note: This is for processing saved files, not live streams.
    Live stream processing requires a different approach.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            logger.info(f"Transcribed text: {text}")
            return text
    except sr.UnknownValueError:
        logger.warning("Google Speech Recognition could not understand audio.")
        return None
    except sr.RequestError as e:
        logger.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None