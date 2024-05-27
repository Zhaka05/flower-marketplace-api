from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from attrs import define
from .database import Base
from pydantic import BaseModel

@define
class UserCreate():
    email: str
    full_name: str
    password: str
    id: int = 0


# table view
# id, email, full_name, password

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    full_name = Column(String, index=True)
    password = Column(String, index=True)

    purchases = relationship("Purchase", back_populates="user")


class UsersRepository:
    # users: list[User]

    # def __init__(self):
    #     self.users = []

    # необходимые методы сюда
    # save

    def save(self, db: Session, user: UserCreate) -> User | None:
        db_user = User(email=user.email, full_name=user.full_name, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh()
        return db_user
        

    # get_one
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, db: Session, id: int) -> User | None:
        return db.query(User).filter(User.id == id).first()

    # конец решения
