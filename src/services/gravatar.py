import hashlib


def generate_gravatar_url(email: str) -> str:
    """
    Генерує URL аватарки Gravatar на основі email.

    Args:
        email (str): Email користувача.

    Returns:
        str: URL зображення аватарки Gravatar з параметром за замовчуванням `identicon`.
    """
    email = email.strip().lower()
    hash_email = hashlib.md5(email.encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_email}?d=identicon"
