from typing import List, Dict, Any
from models.position import Position
from entities.base import Entity

class GameMap:
    """
    Représente la carte du jeu et gère le placement des entités
    """
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.entities: List[Entity] = []
        
        # Pour le viewport
        self.viewport_width = 40
        self.viewport_height = 20
        self.viewport_x = 0
        self.viewport_y = 0
    
    def add_entity(self, entity: Entity) -> None:
        """Ajoute une entité à la carte"""
        self.entities.append(entity)
    
    def remove_entity(self, entity: Entity) -> None:
        """Supprime une entité de la carte"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def get_entities_at_position(self, position: Position) -> List[Entity]:
        """Retourne toutes les entités à une position donnée"""
        return [entity for entity in self.entities 
                if entity.position.x == position.x and entity.position.y == position.y]
    
    def get_entities_in_range(self, center: Position, range_value: int) -> List[Entity]:
        """Retourne toutes les entités dans un rayon donné autour d'une position"""
        result = []
        for entity in self.entities:
            dx = entity.position.x - center.x
            dy = entity.position.y - center.y
            distance = (dx**2 + dy**2) ** 0.5
            if distance <= range_value:
                result.append(entity)
        return result
    
    def center_viewport_on(self, position: Position) -> None:
        """Centre la vue sur une position donnée"""
        self.viewport_x = max(0, min(position.x - self.viewport_width // 2, 
                                     self.width - self.viewport_width))
        self.viewport_y = max(0, min(position.y - self.viewport_height // 2, 
                                     self.height - self.viewport_height))
    
    def world_to_screen(self, position: Position) -> Position:
        """Convertit des coordonnées monde en coordonnées écran"""
        screen_x = position.x - self.viewport_x
        screen_y = position.y - self.viewport_y
        return Position(screen_x, screen_y)
    
    def screen_to_world(self, position: Position) -> Position:
        """Convertit des coordonnées écran en coordonnées monde"""
        world_x = position.x + self.viewport_x
        world_y = position.y + self.viewport_y
        return Position(world_x, world_y)
    
    def is_in_viewport(self, position: Position) -> bool:
        """Vérifie si une position est visible dans la viewport actuelle"""
        screen_pos = self.world_to_screen(position)
        return (0 <= screen_pos.x < self.viewport_width and 
                0 <= screen_pos.y < self.viewport_height)