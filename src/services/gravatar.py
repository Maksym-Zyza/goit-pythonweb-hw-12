import hashlib


def generate_gravatar_url(email: str) -> str:
    email = email.strip().lower()
    hash_email = hashlib.md5(email.encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_email}?d=identicon"
