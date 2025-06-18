from pydantic import BaseModel, EmailStr
from datetime import date


class ContactModelRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(ContactModelRegister):
    id: int
