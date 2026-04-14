import getpass

from app.database import SessionLocal
from app.models import Admin
from app.core.security import hash_password


def main():
    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ").strip()

    db = SessionLocal()
    try:
        exists = db.query(Admin).filter(Admin.username == username).first()
        if exists:
            print("Admin already exists.")
            return

        admin = Admin(username=username, hashed_password=hash_password(password))
        db.add(admin)
        db.commit()
        print("Admin created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()