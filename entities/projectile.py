from entities.base import Entity
from models.position import Position
import math

class Projectile(Entity):
    """
    Représente un projectile tiré par une tour vers une cible
    """
    def __init__(self, position: Position, target_position: Position, damage: int = 1, speed: float = 3.0):
        super().__init__(position, hp=1)  # Les projectiles ont 1 HP
        self.target_position = target_position
        self.damage = damage
        self.speed = speed
        
        # Calculer la direction du mouvement
        dx = target_position.x - position.x
        dy = target_position.y - position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update(self, delta_time: float = 1.0):
        """Met à jour la position du projectile"""
        # Position décimale pour des mouvements plus fluides
        new_x = self.position.x + self.velocity_x * delta_time
        new_y = self.position.y + self.velocity_y * delta_time
        
        # Mettre à jour la position (conversion en entier)
        self.position.x = round(new_x)
        self.position.y = round(new_y)
        
        print(f"[PROJECTILE] Se déplace vers ({self.position.x}, {self.position.y})")
    
    def has_reached_target(self) -> bool:
        """Vérifie si le projectile a atteint sa cible"""
        dx = abs(self.position.x - self.target_position.x)
        dy = abs(self.position.y - self.target_position.y)
        return dx <= 0.5 and dy <= 0.5