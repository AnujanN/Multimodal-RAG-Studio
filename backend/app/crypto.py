"""Fernet symmetric encryption helpers for storing user API keys securely."""
import base64
import secrets
import logging
from cryptography.fernet import Fernet
from .config import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Get or auto-generate a Fernet encryption key."""
    key = settings.encryption_key.strip()
    if not key:
        # Auto-generate and warn — admin should persist this in .env
        logger.warning(
            "ENCRYPTION_KEY not set in .env — generating ephemeral key. "
            "Encrypted data will be lost on restart! Set ENCRYPTION_KEY in .env."
        )
        key = Fernet.generate_key().decode()
    try:
        return Fernet(key.encode())
    except Exception:
        # If the key is malformed, generate a new one (still warns)
        logger.error("ENCRYPTION_KEY is malformed — generating ephemeral key.")
        return Fernet(Fernet.generate_key())


def encrypt(plaintext: str) -> str:
    """Encrypt a plaintext string to a base64 Fernet token string."""
    if not plaintext:
        return ""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a Fernet token string back to plaintext."""
    if not ciphertext:
        return ""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception as e:
        logger.error("Failed to decrypt credential: %s", e)
        return ""


def generate_fernet_key() -> str:
    """Utility to generate a new Fernet key — run once to populate .env."""
    return Fernet.generate_key().decode()
