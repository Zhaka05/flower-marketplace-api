from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session

from attrs import define
from .database import Base
from pydantic import BaseModel

@define
class PurchaseCreate():
    user_id: int = 0
    flower_id: int = 0

# relationship
# table view
# user_id, flower_id

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    flower_id = Column(Integer, ForeignKey("flowers.id"))

    user = relationship("User", back_populates="purchases")
    flower = relationship("Flower", back_populates="purchases")


class PurchasesRepository:
    # purchases: list[Purchase]

    # def __init__(self):
    #     self.purchases = []

    # необходимые методы сюда
    def add_purchase(self, db: Session, purchase: PurchaseCreate) -> Purchase:

        db_purchase = Purchase(user_id=purchase.user_id, flower_id=purchase.flower_id)
        db.add(db_purchase)
        db.commit()
        db.refresh()

        return db_purchase

    def get_all(self, db: Session, skip: int = 0, limit: int = 5) -> list[Purchase]:
        return db.query(Purchase).offset(skip).limit(limit).all()


    # конец решения
