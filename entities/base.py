from abc import ABC, abstractmethod
from models.position import Position

class Entity(ABC):
    def __init__(self, position: Position, hp: int):
        self.position = position
        self.hp = hp

    @abstractmethod
    def update(self):
        """Action de l'entité ) chaque tour de jeu."""
        pass

    def is_alive(self) -> bool:
        return self.hp > 0