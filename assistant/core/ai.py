import os
import openai
import logging

logger = logging.getLogger(__name__)

# Configure OpenAI client if the key is available
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key

async def get_ai_response(text: str, user_id: int) -> str:
    """
    Generates a response using an AI model.
    Falls back to simple logic if no API key is provided.
    """
    if not api_key:
        logger.warning("OPENAI_API_KEY not found. Using fallback logic.")
        if "joke" in text.lower():
            return "Why don't scientists trust atoms? Because they make up everything!"
        return f"I am a simple bot. You said: {text}"

    try:
        # In a real app, you would fetch user history from a database.
        user_context = f"The user's ID is {user_id}."
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful voice assistant. Keep responses brief and conversational. {user_context}"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again in a moment."