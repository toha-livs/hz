import os
import hashlib
from importlib import import_module

os.environ.setdefault('FALCON_SETTINGS_MODULE', 'gusto_api.settings')


def import_object(module, default=None):
    module = module.split('.')
    return getattr(import_module('.'.join(module[:-1])), module[-1], default)


def encrypt(text: str) -> str:
    """
    Encrypt given text string using sha256
    :param text: string for encryption
    :return: encrypted string
    """
    secret_key = import_module(os.environ.get('FALCON_SETTINGS_MODULE')).SECRET_KEY
    return hashlib.sha256(str(text + secret_key).encode()).hexdigest()
