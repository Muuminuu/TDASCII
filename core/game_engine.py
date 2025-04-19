import time
from typing import List, Dict, Any

from core.tcod_ui import TcodUI
from core.tcod_input_handler import TcodInputHandler
from models.position import Position
from models.game_map import GameMap
from entities.tower import Tower
from entities.enemy import Enemy
from entities.projectile import Projectile
from core.combat_system import CombatSystem
from core.wave_manager import WaveManager

class GameEngine:
    """
    Moteur de jeu principal
    """
    def __init__(self, screen_width: int = 80, screen_height: int = 40,
                map_width: int = 50, map_height: int = 30,
                world_width: int = 100, world_height: int = 100):
        
        # Configuration de l'écran et de la carte
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        
        # État du jeu
        self.game_state: Dict[str, Any] = {
            'is_running': True,
            'game_over': False,
            'score': 50,
            'wave': 1,
            'tower_hp': 10,
            'max_tower_hp': 10,
            'current_tab': 'attack',
            'game_speed': 0.1  # Temps entre chaque mise à jour (en secondes)
        }
        
        # Initialisation des composants
        self.game_map = GameMap(world_width, world_height)
        self.ui = TcodUI(screen_width, screen_height, map_width, map_height)
        self.input_handler = TcodInputHandler(self.game_state)
        
        # Position initiale de la tour
        tower_position = Position(world_width // 2, world_height // 2)
        
        # Création de la tour
        self.tower = Tower(tower_position, range=5, damage=1, fire_rate=1.0)
        self.towers: List[Tower] = [self.tower]
        
        # Système de combat
        self.combat_system = CombatSystem()
        
        # Gestionnaire de vagues
        self.wave_manager = WaveManager(self.game_map, tower_position)
        
        # Liste des entités
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        
        # Centrer la vue sur la tour
        self.game_map.center_viewport_on(tower_position)
        
        # Temps
        self.last_update_time = time.time()
    
    def run(self):
        """Lance le jeu"""
        # Initialiser l'interface
        self.ui.initialize()
        
        while self.game_state['is_running']:
            # Calcul du delta time
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            
            # Limiter la vitesse du jeu
            if delta_time < self.game_state['game_speed']:
                time.sleep(self.game_state['game_speed'] - delta_time)
                current_time = time.time()
                delta_time = current_time - self.last_update_time
            
            self.last_update_time = current_time
            
            # Traiter les entrées
            event = self.ui.check_for_event()
            self._handle_input(event)
            
            # Mettre à jour l'état du jeu
            if not self.game_state['game_over']:
                self._update(delta_time)
            
            # Afficher l'état du jeu
            self._render()
            
            # Vérifier si la partie est terminée
            if self.game_state['tower_hp'] <= 0:
                self.game_state['game_over'] = True
            
            # Si Game Over, attendre une touche pour quitter
            if self.game_state['game_over']:
                self._render()  # Afficher l'écran de Game Over
                self.ui.wait_for_keypress()
                self.game_state['is_running'] = False
    
    def _handle_input(self, event: Dict[str, Any]):
        """Traite les entrées utilisateur"""
        action = self.input_handler.handle_input(event)
        
        if action.get('quit'):
            self.game_state['is_running'] = False
        
        # Changement d'onglet
        if action.get('change_tab'):
            self.game_state['current_tab'] = action['change_tab']
            self.ui.current_tab = action['change_tab']
        
        # Déplacement de la tour
        if action.get('move') and self.tower:
            dx, dy = action['move']
            self.tower.position.x += dx
            self.tower.position.y += dy
            
            # Maintenir la tour dans les limites de la carte
            self.tower.position.x = max(0, min(self.tower.position.x, self.game_map.width - 1))
            self.tower.position.y = max(0, min(self.tower.position.y, self.game_map.height - 1))
            
            # Centrer la vue sur la tour
            self.game_map.center_viewport_on(self.tower.position)
        
        # Amélioration de la tour
        if action.get('upgrade'):
            upgrade_type = action['upgrade']
            cost = action['cost']
            
            # Soustraire le coût
            self.game_state['score'] -= cost
            
            if upgrade_type == 'damage':
                self.tower.upgrade_damage()
            elif upgrade_type == 'range':
                self.tower.upgrade_range()
            elif upgrade_type == 'fire_rate':
                self.tower.upgrade_fire_rate()
            elif upgrade_type == 'hp':
                self.game_state['max_tower_hp'] += 5
                self.game_state['tower_hp'] += 5
        
        # Déclencher une nouvelle vague
        if action.get('next_wave'):
            self.wave_manager.next_wave()
    
    def _update(self, delta_time: float):
        """Met à jour l'état du jeu"""
        # Générer de nouveaux ennemis
        new_enemies = self.wave_manager.update(delta_time)
        self.enemies.extend(new_enemies)
        
        # Mettre à jour les ennemis
        self._update_enemies(delta_time)
        
        # Mettre à jour le système de combat
        self.combat_system.update(self.towers, self.enemies, self.game_map, delta_time)
        
        # Récupérer les projectiles du système de combat
        self.projectiles = self.combat_system.projectiles
        
        # Vérifier si tous les ennemis sont vaincus
        if len(self.enemies) == 0 and self.wave_manager.all_enemies_defeated():
            self.wave_manager.next_wave()
            self.game_state['wave'] = self.wave_manager.current_wave
    
    def _update_enemies(self, delta_time: float):
        """Met à jour les ennemis"""
        remaining_enemies = []
        
        for enemy in self.enemies:
            enemy.update(delta_time)
            
            # Vérifier si l'ennemi a atteint la tour
            if enemy.has_reached_target():
                # Infliger des dégâts à la tour
                self.game_state['tower_hp'] -= 1
                self.wave_manager.remove_enemy(enemy)
            elif not enemy.is_alive():
                # L'ennemi est mort, ajouter des points
                self.game_state['score'] += enemy.value
                self.wave_manager.remove_enemy(enemy)
            else:
                remaining_enemies.append(enemy)
        
        self.enemies = remaining_enemies
    
    def _render(self):
        """Affiche l'état du jeu"""
        self.ui.render(
            self.game_map,
            self.towers,
            self.enemies,
            self.projectiles,
            self.game_state
        )