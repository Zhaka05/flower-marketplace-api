from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base
from pydantic import BaseModel

class User(BaseModel):
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
    users: list[User]

    def __init__(self):
        self.users = []

    # необходимые методы сюда
    # save
    def save(self, user: User):
        user.id = len(self.users) + 1
        self.users.append(user)

    # get_one
    def get_by_email(self, email: str) -> User:
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_by_id(self, id: int):
        for user in self.users:
            if user.id == id:
                return user
        return None

    # конец решения
