"""
AI Provider abstraction layer for multiple AI services
Supports: Gemini, ChatGPT, Claude, Groq, Grok
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class AIProvider(ABC):
    """Base class for AI providers"""

    # Override in subclasses
    PROVIDER_NAME = "base"
    DISPLAY_NAME = "Base Provider"
    MODELS: Dict[str, str] = {}  # model_id: display_name
    DEFAULT_MODEL = ""
    API_KEY_URL = ""
    API_KEY_HELP = ""

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL

    @abstractmethod
    def summarize(self, text: str) -> str:
        """Summarize the given text"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        pass

    @classmethod
    def get_models(cls) -> Dict[str, str]:
        """Return available models for this provider"""
        return cls.MODELS


class GeminiProvider(AIProvider):
    """Google Gemini AI provider"""

    PROVIDER_NAME = "gemini"
    DISPLAY_NAME = "Google Gemini"
    MODELS = {
        "gemini-2.5-pro": "Gemini 2.5 Pro (Best Quality)",
        "gemini-2.5-flash": "Gemini 2.5 Flash (Fast)",
        "gemini-2.0-flash": "Gemini 2.0 Flash",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
    }
    DEFAULT_MODEL = "gemini-2.5-pro"
    API_KEY_URL = "https://aistudio.google.com/app/apikey"
    API_KEY_HELP = "Get your free API key from Google AI Studio"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self._genai = None

    def _get_genai(self):
        """Get configured genai module"""
        if self._genai is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._genai = genai
        return self._genai

    def summarize(self, text: str) -> str:
        """Summarize text using Gemini"""
        max_chars = 500000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        prompt = f"""You are a helpful assistant that creates clear, concise summaries of documents.
Provide a well-structured summary with key points and main ideas.

Please provide a comprehensive summary of the following text:

{text}"""

        try:
            genai = self._get_genai()
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            genai = self._get_genai()
            model = genai.GenerativeModel(self.model)
            response = model.generate_content("Say 'OK' if you can read this.")
            return bool(response.text)
        except:
            return False


class OpenAIProvider(AIProvider):
    """OpenAI ChatGPT provider"""

    PROVIDER_NAME = "openai"
    DISPLAY_NAME = "OpenAI (ChatGPT)"
    MODELS = {
        "gpt-4o": "GPT-4o (Best Quality)",
        "gpt-4o-mini": "GPT-4o Mini (Fast & Cheap)",
        "gpt-4-turbo": "GPT-4 Turbo",
        "gpt-4": "GPT-4",
        "gpt-3.5-turbo": "GPT-3.5 Turbo (Budget)",
    }
    DEFAULT_MODEL = "gpt-4o"
    API_KEY_URL = "https://platform.openai.com/api-keys"
    API_KEY_HELP = "Get your API key from OpenAI Platform"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self._client = None

    def _get_client(self):
        """Get OpenAI client"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using OpenAI"""
        max_chars = 100000  # ~25k tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
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
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except:
            return False


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider"""

    PROVIDER_NAME = "claude"
    DISPLAY_NAME = "Anthropic Claude"
    MODELS = {
        "claude-sonnet-4-20250514": "Claude Sonnet 4 (Latest)",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-5-haiku-20241022": "Claude 3.5 Haiku (Fast)",
        "claude-3-opus-20240229": "Claude 3 Opus (Most Capable)",
    }
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    API_KEY_URL = "https://console.anthropic.com/settings/keys"
    API_KEY_HELP = "Get your API key from Anthropic Console"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self._client = None

    def _get_client(self):
        """Get Anthropic client"""
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using Claude"""
        max_chars = 400000  # Claude has 200k context
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        try:
            client = self._get_client()
            message = client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a helpful assistant that creates clear, concise summaries of documents.
Provide a well-structured summary with key points and main ideas.

Please provide a comprehensive summary of the following text:

{text}"""
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            client = self._get_client()
            message = client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say OK"}]
            )
            return bool(message.content[0].text)
        except:
            return False


class GroqProvider(AIProvider):
    """Groq provider (fast inference)"""

    PROVIDER_NAME = "groq"
    DISPLAY_NAME = "Groq"
    MODELS = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B (Best)",
        "llama-3.1-70b-versatile": "Llama 3.1 70B",
        "llama-3.1-8b-instant": "Llama 3.1 8B (Fast)",
        "mixtral-8x7b-32768": "Mixtral 8x7B",
        "gemma2-9b-it": "Gemma 2 9B",
    }
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    API_KEY_URL = "https://console.groq.com/keys"
    API_KEY_HELP = "Get your free API key from Groq Console"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self._client = None

    def _get_client(self):
        """Get Groq client"""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using Groq"""
        max_chars = 24000  # Roughly 6000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        try:
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
                model=self.model,
                temperature=0.3,
                max_tokens=2000
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Say OK"}],
                model=self.model,
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except:
            return False


class GrokProvider(AIProvider):
    """xAI Grok provider"""

    PROVIDER_NAME = "grok"
    DISPLAY_NAME = "xAI Grok"
    MODELS = {
        "grok-2-latest": "Grok 2 (Latest)",
        "grok-2-1212": "Grok 2",
        "grok-beta": "Grok Beta",
    }
    DEFAULT_MODEL = "grok-2-latest"
    API_KEY_URL = "https://console.x.ai/"
    API_KEY_HELP = "Get your API key from xAI Console"

    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self._client = None

    def _get_client(self):
        """Get xAI client (uses OpenAI-compatible API)"""
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"
            )
        return self._client

    def summarize(self, text: str) -> str:
        """Summarize text using Grok"""
        max_chars = 100000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
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
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Grok API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except:
            return False


# Registry of all providers
PROVIDERS: Dict[str, type] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "groq": GroqProvider,
    "grok": GrokProvider,
}


def get_provider(provider_name: str, api_key: str, model: str = None) -> Optional[AIProvider]:
    """Factory function to get the appropriate AI provider"""
    provider_class = PROVIDERS.get(provider_name.lower())
    if provider_class:
        return provider_class(api_key, model)
    return None


def get_all_providers() -> Dict[str, Dict]:
    """Get information about all available providers"""
    result = {}
    for name, cls in PROVIDERS.items():
        result[name] = {
            "name": name,
            "display_name": cls.DISPLAY_NAME,
            "models": cls.MODELS,
            "default_model": cls.DEFAULT_MODEL,
            "api_key_url": cls.API_KEY_URL,
            "api_key_help": cls.API_KEY_HELP,
        }
    return result


def get_provider_info(provider_name: str) -> Optional[Dict]:
    """Get information about a specific provider"""
    all_providers = get_all_providers()
    return all_providers.get(provider_name.lower())
