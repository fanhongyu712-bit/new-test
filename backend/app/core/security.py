import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, stored_hash = hashed_password.split("$", 1)
        computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return computed_hash == stored_hash
    except:
        return False


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hash_value}"


def create_access_token(subject: str, secret_key: str = "your-secret-key", expires_delta: Optional[timedelta] = None) -> str:
    import base64
    import json
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    payload = {"sub": str(subject), "exp": int(expire.timestamp())}
    payload_json = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    signature = hashlib.sha256((payload_b64 + secret_key).encode()).hexdigest()
    return f"{payload_b64}.{signature}"


def decode_access_token(token: str, secret_key: str = "your-secret-key") -> Optional[dict]:
    import base64
    import json
    
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_signature = hashlib.sha256((payload_b64 + secret_key).encode()).hexdigest()
        if signature != expected_signature:
            return None
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None
        return payload
    except:
        return None
