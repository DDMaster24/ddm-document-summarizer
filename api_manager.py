import json
import os
import sys
import base64
from typing import Dict, List, Optional


def get_config_dir():
    """Get a writable directory for config files"""
    if sys.platform == 'win32':
        # On Windows, use LOCALAPPDATA for user-specific writable storage
        base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(base_dir, 'DocumentSummarizer')
    else:
        # On Linux/Mac, use home directory
        config_dir = os.path.join(os.path.expanduser('~'), '.document_summarizer')

    os.makedirs(config_dir, exist_ok=True)
    return config_dir


class APIKeyManager:
    """Manages API keys for multiple AI providers"""

    def __init__(self, config_file=None):
        if config_file is None:
            # Use user-writable directory for config
            config_file = os.path.join(get_config_dir(), 'config.json')
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration structure"""
        return {
            'providers': {},
            'default_provider': None
        }

    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _encode_key(self, key: str) -> str:
        """Encode API key for storage"""
        return base64.b64encode(key.encode()).decode()

    def _decode_key(self, encoded_key: str) -> str:
        """Decode API key from storage"""
        return base64.b64decode(encoded_key.encode()).decode()

    def add_provider(self, provider_name: str, api_key: str, set_as_default: bool = True):
        """Add or update a provider's API key"""
        encoded_key = self._encode_key(api_key)
        self.config['providers'][provider_name] = {
            'api_key': encoded_key,
            'enabled': True
        }

        if set_as_default or self.config['default_provider'] is None:
            self.config['default_provider'] = provider_name

        self._save_config()

    def remove_provider(self, provider_name: str):
        """Remove a provider"""
        if provider_name in self.config['providers']:
            del self.config['providers'][provider_name]

            # If this was the default, set a new default
            if self.config['default_provider'] == provider_name:
                remaining = list(self.config['providers'].keys())
                self.config['default_provider'] = remaining[0] if remaining else None

            self._save_config()

    def get_api_key(self, provider_name: str = None) -> Optional[str]:
        """Get API key for a provider (uses default if not specified)"""
        if provider_name is None:
            provider_name = self.config['default_provider']

        if provider_name and provider_name in self.config['providers']:
            encoded_key = self.config['providers'][provider_name]['api_key']
            return self._decode_key(encoded_key)

        return None

    def get_default_provider(self) -> Optional[str]:
        """Get the default provider name"""
        return self.config['default_provider']

    def set_default_provider(self, provider_name: str):
        """Set the default provider"""
        if provider_name in self.config['providers']:
            self.config['default_provider'] = provider_name
            self._save_config()

    def list_providers(self) -> List[Dict]:
        """List all configured providers"""
        providers = []
        for name, data in self.config['providers'].items():
            providers.append({
                'name': name,
                'enabled': data.get('enabled', True),
                'is_default': name == self.config['default_provider'],
                'api_key_preview': self._get_key_preview(data['api_key'])
            })
        return providers

    def _get_key_preview(self, encoded_key: str) -> str:
        """Get a preview of the API key (first 8 chars + ...)"""
        try:
            key = self._decode_key(encoded_key)
            if len(key) > 12:
                return f"{key[:8]}...{key[-4:]}"
            return f"{key[:4]}..."
        except:
            return "***"

    def has_any_provider(self) -> bool:
        """Check if any provider is configured"""
        return len(self.config['providers']) > 0

    def validate_provider(self, provider_name: str) -> bool:
        """Check if a provider exists and has a key"""
        return (provider_name in self.config['providers'] and
                'api_key' in self.config['providers'][provider_name])
