from cryptography.fernet import Fernet

from src.core.settings import settings

_fernet = Fernet(settings.ENCRYPTION_KEY.get_secret_value())

def encrypt_data(data: str) -> str:
    """Encrypt the string. Return the encrypted string (in base64)."""
    if not data:
        return ""

    return _fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    """Decrypts the string. Return the original string."""
    if not token:
        return ""
    return _fernet.decrypt(token.encode()).decode()
