"""Configuration module: loads settings from .env or Streamlit secrets."""
import os

# ─── Load .env file ────────────────────────────────────────────────────────
# Try with python-dotenv first, then fallback to manual reading
_env_loaded = False
try:
    from dotenv import load_dotenv
    _env_loaded = load_dotenv()
except ImportError:
    pass

# Manual fallback: read .env directly if dotenv not available or didn't load
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if not _env_loaded and os.path.exists(_env_path):
    try:
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip()
    except Exception:
        pass

# ─── Streamlit secrets (for production / Streamlit Cloud deployment) ───────
_SECRETS_LOADED = False
_STREAMLIT_SECRETS = {}
try:
    import streamlit as st
    _STREAMLIT_SECRETS = dict(st.secrets)
    _SECRETS_LOADED = True
except Exception:
    pass


def _get_secret(key: str, default: str = "") -> str:
    """
    Resolve a config value with priority:
      1. Streamlit secrets (production deployment)
      2. os.environ / .env file (local development)
      3. default fallback
    """
    if _SECRETS_LOADED and key in _STREAMLIT_SECRETS:
        return str(_STREAMLIT_SECRETS[key])
    return os.getenv(key, default)


class Settings:
    """Central place for all app configuration."""
    LLM_PROVIDER = _get_secret('LLM_PROVIDER', 'groq')
    # API key resolved via priority:
    #   1. Streamlit secrets (GROQ_API_KEY)
    #   2. os.environ / .env file (GROQ_API_KEY / API_KEY / OPENAI_API_KEY)
    API_KEY = (
        _get_secret('GROQ_API_KEY')
        or _get_secret('API_KEY')
        or _get_secret('OPENAI_API_KEY')
        or ''
    )
    OPENAI_MODEL = 'gpt-4o-mini'
    GEMINI_MODEL = 'gemini-2.0-flash'
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    OPENAI_URL = 'https://api.openai.com/v1'
    GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta'
    GROQ_URL = 'https://api.groq.com/openai/v1'
    MAX_TOKENS = 300
    TEMPERATURE = 0.7
    CHART_DIR = 'charts'
    CHART_FILE = 'output_chart.png'

    @classmethod
    def get_key(cls):
        """Return API key or show help if missing."""
        key = cls.API_KEY
        if not key:
            try:
                import streamlit as st
                st.warning(
                    '⚠️ No API key configured. To enable AI insights:\n\n'
                    '**Local dev:** Create a `.env` file and add:\n'
                    '`GROQ_API_KEY=your_groq_api_key`\n\n'
                    '**Streamlit Cloud:** Go to App Settings > Secrets and add:\n'
                    '```toml\n'
                    'GROQ_API_KEY = "your_groq_api_key"\n'
                    '```\n\n'
                    'Get a free key at: https://console.groq.com'
                )
            except ImportError:
                print('ERROR: Set GROQ_API_KEY in .env file')
                print('Get a free key at: https://console.groq.com')
            return None
        return key

    @classmethod
    def get_model(cls):
        """Get model name for current provider."""
        models = {'openai': cls.OPENAI_MODEL, 'gemini': cls.GEMINI_MODEL, 'groq': cls.GROQ_MODEL}
        return models.get(cls.LLM_PROVIDER, cls.GROQ_MODEL)

    @classmethod
    def get_url(cls):
        """Get API URL for current provider."""
        urls = {'openai': cls.OPENAI_URL, 'gemini': cls.GEMINI_URL, 'groq': cls.GROQ_URL}
        return urls.get(cls.LLM_PROVIDER, cls.GROQ_URL)
