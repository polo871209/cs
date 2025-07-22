"""AI client wrapper for Gemini API"""

from typing import List, Optional

from google import genai
from google.genai import types

from ..config import settings


class GeminiClient:
    """Wrapper for Gemini AI client with consistent error handling"""
    
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
    
    def generate_content(
        self, 
        contents: List[types.Content], 
        model: str = "gemini-2.0-flash",
        config: Optional[types.GenerateContentConfig] = None
    ) -> types.GenerateContentResponse:
        """Generate content using Gemini API"""
        try:
            return self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config or types.GenerateContentConfig(response_mime_type="text/plain")
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}") from e
    
    def generate_content_stream(
        self, 
        contents: List[types.Content], 
        model: str = "gemini-2.0-flash",
        config: Optional[types.GenerateContentConfig] = None
    ):
        """Generate streaming content using Gemini API"""
        try:
            return self.client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config or types.GenerateContentConfig(response_mime_type="text/plain")
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API streaming error: {str(e)}") from e
    
    def generate_session_name(self, user_input: str, ai_response: str) -> str:
        """Generate a concise session name using AI"""
        if not user_input or not ai_response:
            return "New Conversation"

        try:
            summary_prompt = f"""Create a short, descriptive title (2-4 words) for this conversation topic. Return only the title, no quotes or extra text.

User: {user_input[:200]}
AI: {ai_response[:200]}

Title:"""

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=summary_prompt)],
                )
            ]

            response = self.generate_content(
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="text/plain",
                    max_output_tokens=20,
                )
            )

            if response and response.text:
                session_name = response.text.strip()
                session_name = session_name.replace('"', '').replace("'", "")
                if len(session_name) > 50:
                    session_name = session_name[:47] + "..."
                return session_name if session_name else self._fallback_session_name(user_input)
            else:
                return self._fallback_session_name(user_input)

        except Exception as e:
            print(f"⚠️ AI session naming failed, using fallback: {str(e)}")
            return self._fallback_session_name(user_input)

    def _fallback_session_name(self, user_input: str) -> str:
        """Fallback method for generating session names"""
        try:
            words = user_input.split()[:3]
            return " ".join(words) + ("..." if len(user_input.split()) > 3 else "")
        except Exception:
            return "New Conversation"
