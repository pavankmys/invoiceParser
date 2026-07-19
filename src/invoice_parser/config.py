import os
from pathlib import Path
from typing import Optional

from invoice_parser.core.exceptions import ConfigurationError


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key not in os.environ:
                os.environ[key] = value


def get_gemini_api_key() -> str:
    _load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ConfigurationError(
            "GEMINI_API_KEY not found. Set the env var, or create a .env file "
            "with: GEMINI_API_KEY=your-key"
        )
    return key
