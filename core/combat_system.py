import time
from typing import List, Optional
from entities.tower import Tower
from entities.enemy import Enemy
from entities.base import Entity
from models.position import Position
from entities.projectile import Projectile  # À créer

class CombatSystem:
    """
    Gère le système de combat entre les tours et les ennemis
    """
    def __init__(self):
        self.projectiles: List[Projectile] = []
        self.last_shot_time = 0
        self.reload_progress = 1.0  # Prêt à tirer
    
    def update(self, towers: List[Tower], enemies: List[Enemy], game_map, delta_time: float) -> None:
        """Met à jour le système de combat"""
        # Mise à jour des projectiles
        self._update_projectiles(delta_time, enemies, game_map)
        
        # Tours attaquent les ennemis à portée
        for tower in towers:
            if tower.can_shoot():
                target = self._find_closest_enemy(tower, enemies, game_map)
                if target:
                    self._shoot(tower, target, game_map)
            else:
                tower.update_reload(delta_time)
    
    def _update_projectiles(self, delta_time: float, enemies: List[Enemy], game_map) -> None:
        """Met à jour les projectiles et vérifie les collisions"""
        remaining_projectiles = []
        
        for projectile in self.projectiles:
            projectile.update(delta_time)
            
            # Vérifier si le projectile a atteint sa cible ou est hors carte
            if (projectile.position.x < 0 or projectile.position.x >= game_map.width or
                projectile.position.y < 0 or projectile.position.y >= game_map.height):
                continue  # Projectile hors de la carte
            
            # Vérifier les collisions avec les ennemis
            hit = False
            for enemy in enemies:
                if self._check_collision(projectile, enemy):
                    enemy.hp -= projectile.damage
                    hit = True
                    break
            
            if not hit:
                remaining_projectiles.append(projectile)
        
        self.projectiles = remaining_projectiles
    
    def _check_collision(self, projectile: Projectile, entity: Entity) -> bool:
        """Vérifie si un projectile touche une entité"""
        return projectile.position == entity.position
    
    def _find_closest_enemy(self, tower: Tower, enemies: List[Enemy], game_map) -> Optional[Enemy]:
        """Trouve l'ennemi le plus proche à portée de la tour"""
        enemies_in_range = []
        
        for enemy in enemies:
            dx = enemy.position.x - tower.position.x
            dy = enemy.position.y - tower.position.y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance <= tower.range:
                enemies_in_range.append((enemy, distance))
        
        if enemies_in_range:
            # Trier par distance
            enemies_in_range.sort(key=lambda x: x[1])
            return enemies_in_range[0][0]
        
        return None
    
    def _shoot(self, tower: Tower, target: Enemy, game_map) -> None:
        """Fait tirer une tour sur une cible"""
        projectile = Projectile(
            Position(tower.position.x, tower.position.y),
            target.position,
            tower.damage,
            speed=5.0
        )
        
        self.projectiles.append(projectile)
        tower.shoot()  # Marquer la tour comme ayant tiré