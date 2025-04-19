from entities.base import Entity
from models.position import Position

class Enemy(Entity):
    def __init__(self, position: Position, speed: int = 1, hp: int = 10):
        super().__init__(position, hp)
        self.speed = speed

    def update(self):
        self.position.x -= self.speed
        print(f"[ENNEMI] Avance vers la tour. Nouvelle position : {self.position.x}, {self.position.y}")