from sqlalchemy.orm import Session
from .models import User
from .security import hash_password

def seed_users(db: Session):
    # idempotent seed
    if db.query(User).count() > 0:
        return
    db.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))
    db.add(User(username="viewer", password_hash=hash_password("viewer123"), role="viewer"))
    db.commit()
