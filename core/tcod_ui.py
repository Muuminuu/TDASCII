import tcod
from typing import List, Dict, Any, Tuple
from entities.tower import Tower
from entities.enemy import Enemy
from entities.projectile import Projectile
from models.position import Position

class TcodUI:
    """
    Interface utilisateur basée sur TCOD
    """
    # Constantes pour l'affichage
    HEALTH_BAR_LENGTH = 10
    HEALTH_BAR_CHAR_FULL = "█"
    HEALTH_BAR_CHAR_EMPTY = "░"
    
    RELOAD_BAR_LENGTH = 10
    RELOAD_BAR_CHAR_FULL = "●"
    RELOAD_BAR_CHAR_EMPTY = "○"
    
    # Caractères pour les entités
    TOWER_CHAR = "T"
    ENEMY_CHAR = "E"
    PROJECTILE_CHAR = "*"
    
    def __init__(self, screen_width: int = 80, screen_height: int = 40, 
                 map_width: int = 50, map_height: int = 30):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        
        # Pour le tableau de bord (dashboard)
        self.dashboard_width = screen_width - map_width - 2
        self.dashboard_height = screen_height - 2
        self.dashboard_x = map_width + 2
        self.dashboard_y = 1
        
        # Onglet actuel du tableau de bord
        self.current_tab = "attack"
        
        # Initialisation de TCOD
        self.console = None
        self.context = None
        
    def initialize(self):
        """Initialise l'interface TCOD"""
        # Utiliser l'approche moderne de tcod
        self.console = tcod.Console(self.screen_width, self.screen_height)
        self.context = tcod.context.new_terminal(
            self.screen_width, 
            self.screen_height,
            title="Tower Defense ASCII - POO",
            vsync=True
        )
    
    def clear(self):
        """Efface l'écran"""
        self.console.clear()
    
    def render(self, game_map, towers: List[Tower], enemies: List[Enemy], 
               projectiles: List[Projectile], game_state: Dict[str, Any]):
        """Affiche l'état du jeu"""
        self.clear()
        
        # Afficher la carte
        self._draw_map(game_map)
        
        # Afficher les entités
        self._draw_entities(game_map, towers, enemies, projectiles)
        
        # Afficher le tableau de bord
        self._draw_dashboard(game_state, towers[0] if towers else None)
        
        # Afficher le HUD
        self._draw_hud(game_state)
        
        # Gérer le Game Over
        if game_state.get('game_over', False):
            self._draw_game_over()
        
        # Mettre à jour l'écran
        self.context.present(self.console)
    
    def _draw_map(self, game_map):
        """Dessine la carte"""
        # Dessiner le cadre de la carte
        self.console.draw_frame(0, 0, self.map_width + 2, self.map_height + 2, 
                               "World View", fg=(255, 255, 255))
        
        for y_screen in range(self.map_height):
            for x_screen in range(self.map_width):
                world_pos = game_map.screen_to_world(Position(x_screen, y_screen))
                
                # Afficher le fond
                if 0 <= world_pos.x < game_map.width and 0 <= world_pos.y < game_map.height:
                    self.console.print(x_screen + 1, y_screen + 1, '.', fg=(100, 100, 100))
    
    def _draw_entities(self, game_map, towers: List[Tower], enemies: List[Enemy], 
                      projectiles: List[Projectile]):
        """Dessine les entités sur la carte"""
        # Dessiner les tours
        for tower in towers:
            screen_pos = game_map.world_to_screen(tower.position)
            if game_map.is_in_viewport(tower.position):
                self.console.print(screen_pos.x + 1, screen_pos.y + 1, 
                               self.TOWER_CHAR, fg=(255, 255, 0))
        
        # Dessiner les ennemis
        for enemy in enemies:
            screen_pos = game_map.world_to_screen(enemy.position)
            if game_map.is_in_viewport(enemy.position):
                self.console.print(screen_pos.x + 1, screen_pos.y + 1, 
                               self.ENEMY_CHAR, fg=(255, 0, 0))
        
        # Dessiner les projectiles
        for projectile in projectiles:
            screen_pos = game_map.world_to_screen(projectile.position)
            if game_map.is_in_viewport(projectile.position):
                self.console.print(screen_pos.x + 1, screen_pos.y + 1, 
                               self.PROJECTILE_CHAR, fg=(0, 255, 0))
    
    def _draw_dashboard(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine le tableau de bord"""
        # Cadre du tableau de bord
        self.console.draw_frame(self.dashboard_x, self.dashboard_y, 
                              self.dashboard_width, self.dashboard_height, 
                              "Dashboard", fg=(255, 255, 255))
        
        # Onglets
        tab_attack_color = (255, 255, 255) if self.current_tab == "attack" else (150, 150, 150)
        tab_defense_color = (255, 255, 255) if self.current_tab == "defense" else (150, 150, 150)
        
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 2, "[A] Attaque", fg=tab_attack_color)
        self.console.print(self.dashboard_x + 15, self.dashboard_y + 2, "[D] Défense", fg=tab_defense_color)
        
        # Ligne horizontale sous les onglets
        for x in range(self.dashboard_width - 2):
            self.console.print(self.dashboard_x + 1 + x, self.dashboard_y + 3, "─", fg=(255, 255, 255))
        
        # Contenu de l'onglet
        if self.current_tab == "attack":
            self._draw_attack_tab(game_state, tower)
        elif self.current_tab == "defense":
            self._draw_defense_tab(game_state, tower)
        
        # Barre de rechargement
        self._draw_reload_bar(tower.reload_progress if tower else 0.0)
        
        # Score et vague
        self.console.print(self.dashboard_x + 2, self.dashboard_y + self.dashboard_height - 3, 
                         f"Score: {game_state.get('score', 0)}", fg=(255, 255, 0))
        
        self.console.print(self.dashboard_x + 2, self.dashboard_y + self.dashboard_height - 2, 
                         f"Vague: {game_state.get('wave', 1)}", fg=(255, 255, 255))
    
    def _draw_attack_tab(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine l'onglet d'amélioration des attaques"""
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 5, 
                         "--- Améliorations d'Attaque ---", fg=(200, 200, 200))
        
        # Dégâts
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 7, 
                         f"[1] Dégâts (+1): Coût {10}", fg=(200, 200, 200))
        
        damage_display = str(tower.damage) if tower else "1"
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 8, 
                         f"    Actuel: {damage_display}", fg=(150, 150, 150))
        
        # Portée
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 10, 
                         f"[2] Portée (+1): Coût {15}", fg=(200, 200, 200))
        
        range_display = str(tower.range) if tower else "3"
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 11, 
                         f"    Actuelle: {range_display}", fg=(150, 150, 150))
        
        # Vitesse de tir
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 13, 
                         f"[S] Vitesse Tir (+0.2): Coût {25}", fg=(200, 200, 200))
        
        fire_rate_display = f"{tower.fire_rate:.1f}" if tower else "1.0"
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 14, 
                         f"    Actuelle: {fire_rate_display}", fg=(150, 150, 150))
    
    def _draw_defense_tab(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine l'onglet d'amélioration de la défense"""
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 5, 
                         "--- Améliorations de Défense ---", fg=(200, 200, 200))
        
        # Vie de la tour
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 7, 
                         f"[3] Vie de la Tour (+5): Coût {20}", fg=(200, 200, 200))
        
        if tower:
            hp_display = f"{tower.hp}/{game_state.get('max_tower_hp', 10)}"
        else:
            hp_display = "0/0"
            
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 8, 
                         f"    Actuelle: {hp_display}", fg=(150, 150, 150))
    
    def _draw_hud(self, game_state: Dict[str, Any]):
        """Dessine le HUD (barre de vie, etc.)"""
        tower_hp = game_state.get('tower_hp', 0)
        max_tower_hp = game_state.get('max_tower_hp', 10)
        
        self._draw_health_bar(tower_hp, max_tower_hp, 1, self.map_height + 2)
    
    def _draw_health_bar(self, value: int, maximum: int, x: int, y: int):
        """Dessine une barre de vie"""
        # Calculer le remplissage
        fill_length = int(self.HEALTH_BAR_LENGTH * value / maximum) if maximum > 0 else 0
        bar = self.HEALTH_BAR_CHAR_FULL * fill_length + self.HEALTH_BAR_CHAR_EMPTY * (self.HEALTH_BAR_LENGTH - fill_length)
        
        # Choisir la couleur en fonction de la santé
        if value > maximum // 2:
            color = (0, 255, 0)  # Vert
        elif value > maximum // 4:
            color = (255, 255, 0)  # Jaune
        else:
            color = (255, 0, 0)  # Rouge
        
        self.console.print(x, y, f"HP: [{bar}]", fg=color)
    
    def _draw_reload_bar(self, progress: float):
        """Dessine la barre de rechargement"""
        # Calculer le remplissage
        fill_length = int(self.RELOAD_BAR_LENGTH * progress)
        bar = self.RELOAD_BAR_CHAR_FULL * fill_length + self.RELOAD_BAR_CHAR_EMPTY * (self.RELOAD_BAR_LENGTH - fill_length)
        
        # Choisir la couleur en fonction de l'état
        color = (0, 200, 255) if progress >= 1.0 else (100, 100, 100)  # Cyan ou Gris
        
        self.console.print(self.dashboard_x + 2, self.dashboard_y + 16, f"Prêt: [{bar}]", fg=color)
    
    def _draw_game_over(self):
        """Affiche l'écran de Game Over"""
        self.console.print(self.screen_width // 2, self.screen_height // 2, 
                         "GAME OVER", fg=(255, 0, 0), alignment=tcod.CENTER)
        
        self.console.print(self.screen_width // 2, self.screen_height // 2 + 2, 
                         "Appuyez sur une touche pour quitter", fg=(255, 255, 255), alignment=tcod.CENTER)
    
    def wait_for_keypress(self) -> Dict:
        """Attend une touche et retourne l'événement"""
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.KeyDown):
                return self._convert_event(event)
        return {}
    
    def check_for_event(self) -> Dict:
        """Vérifie si un événement est disponible"""
        for event in tcod.event.get():
            if event.type == "QUIT" or isinstance(event, tcod.event.Quit):
                return {'type': 'QUIT'}
            elif event.type == "KEYDOWN" or isinstance(event, tcod.event.KeyDown):
                return self._convert_event(event)
        return {}
    
    def _convert_event(self, event) -> Dict:
        """Convertit un événement tcod en dictionnaire"""
        if isinstance(event, tcod.event.Quit):
            return {'type': 'QUIT'}
        elif isinstance(event, tcod.event.KeyDown):
            return {
                'type': 'KEYDOWN',
                'key': event.sym,
                'alt': bool(event.mod & tcod.event.KMOD_ALT),
                'ctrl': bool(event.mod & tcod.event.KMOD_CTRL),
                'shift': bool(event.mod & tcod.event.KMOD_SHIFT)
            }
        return {}