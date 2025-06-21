import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

CLD_NAME = os.getenv("CLOUDINARY_NAME")
CLD_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLD_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")


class UploadFileService:
    """
    Сервіс для завантаження файлів на Cloudinary.

    Ініціалізує конфігурацію Cloudinary при створенні екземпляру.
    """

    def __init__(self):
        """
        Ініціалізація конфігурації Cloudinary з параметрами із змінних середовища.
        """
        cloudinary.config(
            cloud_name=CLD_NAME,
            api_key=CLD_API_KEY,
            api_secret=CLD_API_SECRET,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантажує файл на Cloudinary, зберігаючи під унікальним публічним ідентифікатором.

        Args:
            file: Файл, який потрібно завантажити (очікується об'єкт із атрибутом `.file`).
            username (str): Ім'я користувача для формування шляху зберігання.

        Returns:
            str: URL зображення, обрізаного та масштабованого до 250x250 px.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
