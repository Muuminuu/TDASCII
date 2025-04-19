from entities.base import Entity
from models.position import Position

class Tower(Entity):
    def __init__(self, position: Position, range: int = 3):
        super().__init(position, hp=99)
        self.range = range

    def update(self):
        print(f"[TOUR] Prête à attaquer dans un rayon de {self.range}")