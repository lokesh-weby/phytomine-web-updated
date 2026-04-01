# crypto_utils.py
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib
import json
import time

# Generate key ONCE and store it securely (settings.py or env)
def get_fernet():
    key = settings.SECRET_KEY.encode()
    key = hashlib.sha256(key).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt_data(value: str) -> str:
    f = get_fernet()
    token = f.encrypt(value.encode())
    return token.decode()


def decrypt_data(token: str) -> str:
    f = get_fernet()
    value = f.decrypt(token.encode())
    return value.decode()


def generate_token(record_id):
    """
    Time-bound secure token
    """
    payload = {
        "id": record_id,
        "ts": int(time.time())
    }
    payload_str = json.dumps(payload)
    return encrypt_data(payload_str)


def verify_token(token, record_id, expiry=600):
    """
    Verify token & expiry (default 10 mins)
    """
    data = json.loads(decrypt_data(token))
    if str(data["id"]) != str(record_id):
        return False
    if time.time() - data["ts"] > expiry:
        return False
    return True
