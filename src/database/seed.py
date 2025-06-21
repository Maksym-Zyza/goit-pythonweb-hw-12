import random
from faker import Faker
from sqlalchemy.orm import Session
from models import Contact, User
from db import engine

fake = Faker()
CONTACTS = random.randint(20, 40)


def seed_users(session: Session) -> None:
    """
    Створює та додає у базу 5 користувачів з фіктивними даними.

    Args:
        session (Session): Сесія SQLAlchemy для роботи з базою.
    """
    for i in range(1, 6):
        user = User(username=f"user{i}", email=f"user{i}@example.com", password="pass")
        session.add(user)
    session.commit()


def seed_contacts(session: Session, num_contacts: int) -> None:
    """
    Створює та додає у базу випадкову кількість контактів із фейковими даними.

    Args:
        session (Session): Сесія SQLAlchemy для роботи з базою.
        num_contacts (int): Кількість контактів для створення.
    """
    contacts = [
        Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.unique.numerify("+###-###-#######"),
            birthday=fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=80),
            user_id=random.randint(1, 5),
        )
        for _ in range(num_contacts)
    ]
    session.add_all(contacts)
    session.commit()


if __name__ == "__main__":
    with Session(engine) as session:
        seed_users(session)
    with Session(engine) as session:
        seed_contacts(session, CONTACTS)
    print("Contacts table seeded successfully!")
