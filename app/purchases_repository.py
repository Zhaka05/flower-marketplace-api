from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .database import Base
from pydantic import BaseModel

# @define
class Purchase(BaseModel):
    user_id: int = 0
    flower_id: int = 0

# relationship
# table view
# user_id, flower_id

class Purchase(Base):
    __tablename__ = "purchases"

    user_id = Column(Integer, ForeignKey("users.id"))
    flower_id = Column(Integer, ForeignKey("flowers.id"))

    user = relationship("User", back_populates="purchases")
    flower = relationship("Flower", back_populates="purchases")


class PurchasesRepository:
    purchases: list[Purchase]

    def __init__(self):
        self.purchases = []

    # необходимые методы сюда
    def add_purchase(self, purchase: Purchase):
        self.purchases.append(purchase)

    def get_all(self):
        return self.purchases


    # конец решения
