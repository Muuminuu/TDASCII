import random
from typing import List, Optional
from models.position import Position
from entities.enemy import Enemy

class WaveManager:
    """
    Gère les vagues d'ennemis
    """
    def __init__(self, game_map, tower_position: Position):
        self.game_map = game_map
        self.tower_position = tower_position
        self.current_wave = 1
        self.enemies_per_wave = 3
        self.spawn_timer = 0
        self.spawn_interval = 60  # Frames entre chaque vague
        self.difficulty_multiplier = 1.1
        self.spawned_enemies: List[Enemy] = []
    
    def update(self, delta_time: float = 1.0) -> List[Enemy]:
        """Met à jour le gestionnaire de vagues et retourne les nouveaux ennemis"""
        self.spawn_timer += 1
        
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return self._spawn_enemies()
        
        return []
    
    def _spawn_enemies(self) -> List[Enemy]:
        """Génère une nouvelle vague d'ennemis"""
        num_to_spawn = int(self.enemies_per_wave * self.current_wave * 0.6) + 1
        new_enemies = []
        
        for _ in range(num_to_spawn):
            enemy = self._create_enemy()
            new_enemies.append(enemy)
            self.spawned_enemies.append(enemy)
        
        print(f"[VAGUE] Vague {self.current_wave} : {num_to_spawn} ennemis apparaissent !")
        return new_enemies
    
    def _create_enemy(self) -> Enemy:
        """Crée un ennemi à une position aléatoire sur les bords de la carte"""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.randint(0, self.game_map.width - 1)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, self.game_map.width - 1)
            y = self.game_map.height - 1
        elif side == 'left':
            x = 0
            y = random.randint(0, self.game_map.height - 1)
        else:  # right
            x = self.game_map.width - 1
            y = random.randint(0, self.game_map.height - 1)
        
        enemy = Enemy.create_enemy(
            Position(x, y),
            self.tower_position,
            self.current_wave,
            self.difficulty_multiplier
        )
        
        return enemy
    
    def next_wave(self):
        """Passe à la vague suivante"""
        self.current_wave += 1
        self.spawn_timer = self.spawn_interval  # Déclenche immédiatement la prochaine vague
        print(f"[VAGUE] Préparation de la vague {self.current_wave}")
    
    def remove_enemy(self, enemy: Enemy):
        """Supprime un ennemi de la liste des ennemis générés"""
        if enemy in self.spawned_enemies:
            self.spawned_enemies.remove(enemy)
    
    def all_enemies_defeated(self) -> bool:
        """Vérifie si tous les ennemis de la vague ont été vaincus"""
        return len(self.spawned_enemies) == 0