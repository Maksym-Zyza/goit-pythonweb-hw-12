from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import extract
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.database.models import Contact, User


async def search_contacts(first_name, last_name, email, db: Session, user: User):
    query = db.query(Contact).filter(Contact.user_id == user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()


async def create_contact(body, db: Session, user: User):
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    try:
        db.commit()
        db.refresh(contact)
        return contact
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Email or phone number already exists."
        )


async def get_contact_by_id(id: int, db: Session, user: User):
    contact = (
        db.query(Contact).filter(Contact.id == id, Contact.user_id == user.id).first()
    )
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


async def update_contact(id: int, body, db: Session, user: User):
    contact = (
        db.query(Contact).filter(Contact.id == id, Contact.user_id == user.id).first()
    )
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    updated_data = body.model_dump()
    for key, value in updated_data.items():
        setattr(contact, key, value)

    try:
        db.commit()
        db.refresh(contact)
        return contact
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Email or phone number already exists."
        )


async def delete_contact(id: int, db: Session, user: User):
    contact = (
        db.query(Contact).filter(Contact.id == id, Contact.user_id == user.id).first()
    )
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )

    db.delete(contact)
    db.commit()
    return contact


async def get_upcoming_birthdays(db: Session, user: User):
    today = datetime.today().date()
    upcoming = today + timedelta(days=7)

    start_day = today.day
    start_month = today.month
    end_day = upcoming.day
    end_month = upcoming.month

    query = db.query(Contact).filter(Contact.user_id == user.id)

    if start_month == end_month:
        query = query.filter(
            extract("month", Contact.birthday) == start_month,
            extract("day", Contact.birthday) >= start_day,
            extract("day", Contact.birthday) <= end_day,
        )
    else:
        query = query.filter(
            (
                (extract("month", Contact.birthday) == start_month)
                & (extract("day", Contact.birthday) >= start_day)
            )
            | (
                (extract("month", Contact.birthday) == end_month)
                & (extract("day", Contact.birthday) <= end_day)
            )
        )

    return query.all()
