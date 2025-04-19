from entities.base import Entity
from models.position import Position
import math

class Enemy(Entity):
    """
    Représente un ennemi qui se déplace vers la tour
    """
    def __init__(self, position: Position, target_position: Position = None, speed: float = 1.0, hp: int = 10):
        super().__init__(position, hp)
        self.target_position = target_position
        self.speed = speed
        self.value = 5  # Points gagnés quand l'ennemi est vaincu
    
    def set_target(self, target_position: Position):
        """Définit la position cible de l'ennemi"""
        self.target_position = target_position
    
    def update(self, delta_time: float = 1.0):
        """Met à jour la position de l'ennemi vers sa cible"""
        if not self.target_position:
            print(f"[ENNEMI] Pas de cible définie pour l'ennemi à {self.position.x}, {self.position.y}")
            return
        
        # Calculer la direction vers la cible
        dx = self.target_position.x - self.position.x
        dy = self.target_position.y - self.position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.speed:
            # Arrivé à destination
            self.position.x = self.target_position.x
            self.position.y = self.target_position.y
        else:
            # Se déplacer vers la cible
            move_x = (dx / distance) * self.speed * delta_time
            move_y = (dy / distance) * self.speed * delta_time
            
            self.position.x = round(self.position.x + move_x)
            self.position.y = round(self.position.y + move_y)
        
        print(f"[ENNEMI] Avance vers la cible. Nouvelle position : {self.position.x}, {self.position.y}")
    
    def has_reached_target(self) -> bool:
        """Vérifie si l'ennemi a atteint sa cible"""
        if not self.target_position:
            return False
            
        return self.position.x == self.target_position.x and self.position.y == self.target_position.y
    
    @staticmethod
    def create_enemy(position: Position, target_position: Position = None, 
                     wave: int = 1, difficulty_multiplier: float = 1.1) -> 'Enemy':
        """Crée un ennemi adapté au niveau de vague actuel"""
        hp = int(10 * (difficulty_multiplier ** (wave - 1)))
        speed = 1.0 + (wave * 0.1)  # Augmente légèrement avec le niveau
        
        return Enemy(position, target_position, speed, hp)