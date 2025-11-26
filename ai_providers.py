"""
AI Provider abstraction layer for different summarization services
"""
from abc import ABC, abstractmethod
from typing import Optional

class AIProvider(ABC):
    """Base class for AI providers"""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """Summarize the given text"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        pass

class GeminiProvider(AIProvider):
    """Google Gemini AI provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "models/gemini-1.5-flash"
        self._client = None

    def _get_client(self):
        """Lazy load the Gemini client"""
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model_name)
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using Gemini"""
        try:
            # Truncate text if too long
            max_chars = 30000  # Gemini 1.5 Flash can handle more than Groq
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[Text truncated due to length...]"

            model = self._get_client()
            prompt = f"""You are a helpful assistant that creates clear, concise summaries of documents.
Provide a well-structured summary with key points and main ideas.

Please provide a comprehensive summary of the following text:

{text}"""

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            model = self._get_client()
            # Simple test prompt
            response = model.generate_content("Say 'OK' if you can read this.")
            return bool(response.text)
        except:
            return False

class GroqProvider(AIProvider):
    """Groq AI provider (legacy support)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "llama-3.1-70b-versatile"
        self._client = None

    def _get_client(self):
        """Lazy load the Groq client"""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using Groq"""
        try:
            # Truncate text if too long
            max_chars = 24000  # Roughly 6000 tokens
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[Text truncated due to length...]"

            client = self._get_client()
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates clear, concise summaries of documents. Provide a well-structured summary with key points and main ideas."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a comprehensive summary of the following text:\n\n{text}"
                    }
                ],
                model=self.model_name,
                temperature=0.3,
                max_tokens=2000
            )

            return chat_completion.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            client = self._get_client()
            # Simple test prompt
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Say OK"}],
                model=self.model_name,
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except:
            return False

def get_provider(provider_name: str, api_key: str) -> Optional[AIProvider]:
    """Factory function to get the appropriate AI provider"""
    providers = {
        'gemini': GeminiProvider,
        'groq': GroqProvider
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class:
        return provider_class(api_key)

    return None
