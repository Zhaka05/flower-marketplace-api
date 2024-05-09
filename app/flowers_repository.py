from attrs import define


@define
class Flower:
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    # необходимые методы сюда
    def get_id(self) -> int:
        return len(self.flowers) + 1

    def save(self, flower: Flower):
        flower.id = self.get_id()
        self.flowers.append(flower)
    
    def get_by_id(self, id: int) -> Flower:
        for flower in self.flowers:
            if flower.id == id:
                return flower
        return None
    
    def get_all(self) -> list[Flower]:
        return self.flowers
    

    # конец решения
