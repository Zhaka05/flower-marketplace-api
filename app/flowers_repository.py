from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from .database import Base
from pydantic import BaseModel

from attrs import define
@define
class FlowerCreate():
    name: str
    count: int
    cost: int
    id: int = 0

# id, name, count, cost

class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    count = Column(Integer, index=True)
    cost = Column(Integer, index=True)
    purchases = relationship("Purchase", back_populates="flower")

class FlowersRepository:
    # flowers: list[Flower]

    # def __init__(self):
    #     self.flowers = []

    # необходимые методы сюда

    def save(self, db: Session, flower: FlowerCreate) -> Flower:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        db.add(db_flower)
        db.commit()
        db.refresh()

        return db_flower
    
    def get_by_id(self, db: Session, id: int) -> Flower:
        return db.query(Flower).filter(Flower.id == id).first()
    
    def get_all(self, db: Session, offset: int = 0, limit: int = 5) -> list[Flower]:
        return db.query(Flower).offset(offset).limit(limit).all()
    
    def delete_flower(self, db: Session, flower_id: int):
        db_flower = db.query(Flower).filter(Flower.id == flower_id).first()
        db.delete(db_flower)
        db.commit()
        db.refresh()
        return db_flower


    # конец решения
