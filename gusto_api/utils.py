import hashlib
import os
from importlib import import_module


def encrypt(text: str) -> str:
    """
    Encrypt given text string using sha256
    :param text: string for encryption
    :return: encrypted string
    """
    secret_key = import_module(os.environ.get('FALCON_SETTINGS_MODULE')).SECRET_KEY
    return hashlib.sha256(str(text + secret_key).encode()).hexdigest()