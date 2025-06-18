import random
from faker import Faker
from sqlalchemy.orm import Session
from models import Contact
from models import User
from db import engine

fake = Faker()

CONTACTS = random.randint(20, 40)

with Session(engine) as session:
    for i in range(1, 6):
        user = User(username=f"user{i}", email=f"user{i}@example.com", password="pass")
        session.add(user)
    session.commit()

with Session(engine) as session:
    contacts = [
        Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.unique.numerify("+###-###-#######"),
            birthday=fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=80),
            user_id=random.randint(1, 5),
        )
        for _ in range(CONTACTS)
    ]
    session.add_all(contacts)
    session.commit()

print("Contacts table seeded successfully!")
