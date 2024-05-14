# from attrs import define
from pydantic import BaseModel

# @define
class Purchase(BaseModel):
    user_id: int = 0
    flower_id: int = 0


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
