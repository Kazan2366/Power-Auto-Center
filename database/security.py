import hashlib
import hmac
import secrets


PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"{PBKDF2_ALGO}${PBKDF2_ITERATIONS}${salt}${digest}"


def is_password_hash(value: str) -> bool:
    parts = (value or "").split("$")
    return len(parts) == 4 and parts[0] == PBKDF2_ALGO


def verify_password(password: str, stored: str) -> bool:
    parts = (stored or "").split("$")
    if len(parts) != 4 or parts[0] != PBKDF2_ALGO:
        return False

    _, iterations_raw, salt, expected = parts
    try:
        iterations = int(iterations_raw)
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        iterations,
    ).hex()
    return hmac.compare_digest(digest, expected)
