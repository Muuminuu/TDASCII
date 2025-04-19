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
        
    def initialize(self):
        """Initialise l'interface TCOD"""
        # Remplacer la ligne problématique par l'initialisation simple
        self.console = tcod.console_init_root(self.screen_width, self.screen_height, 
                                            'Tower Defense ASCII - POO', False)
    
    def clear(self):
        """Efface l'écran"""
        tcod.console_clear(self.console)
    
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
        tcod.console_flush()
    
    def _draw_map(self, game_map):
        """Dessine la carte"""
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print_frame(self.console, 0, 0, self.map_width + 2, self.map_height + 2, 
                               "World View", False, tcod.BKGND_NONE)
        
        for y_screen in range(self.map_height):
            for x_screen in range(self.map_width):
                world_pos = game_map.screen_to_world(Position(x_screen, y_screen))
                
                # Afficher le fond
                if 0 <= world_pos.x < game_map.width and 0 <= world_pos.y < game_map.height:
                    tcod.console_put_char_ex(self.console, x_screen + 1, y_screen + 1, 
                                          '.', tcod.dark_grey, tcod.black)
    
    def _draw_entities(self, game_map, towers: List[Tower], enemies: List[Enemy], 
                      projectiles: List[Projectile]):
        """Dessine les entités sur la carte"""
        # Dessiner les tours
        for tower in towers:
            screen_pos = game_map.world_to_screen(tower.position)
            if game_map.is_in_viewport(tower.position):
                tcod.console_put_char_ex(self.console, screen_pos.x + 1, screen_pos.y + 1, 
                                      self.TOWER_CHAR, tcod.yellow, tcod.black)
        
        # Dessiner les ennemis
        for enemy in enemies:
            screen_pos = game_map.world_to_screen(enemy.position)
            if game_map.is_in_viewport(enemy.position):
                tcod.console_put_char_ex(self.console, screen_pos.x + 1, screen_pos.y + 1, 
                                      self.ENEMY_CHAR, tcod.red, tcod.black)
        
        # Dessiner les projectiles
        for projectile in projectiles:
            screen_pos = game_map.world_to_screen(projectile.position)
            if game_map.is_in_viewport(projectile.position):
                tcod.console_put_char_ex(self.console, screen_pos.x + 1, screen_pos.y + 1, 
                                      self.PROJECTILE_CHAR, tcod.green, tcod.black)
    
    def _draw_dashboard(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine le tableau de bord"""
        # Cadre du tableau de bord
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print_frame(self.console, self.dashboard_x, self.dashboard_y, 
                               self.dashboard_width, self.dashboard_height, "Dashboard")
        
        # Onglets
        tab_attack_color = tcod.white if self.current_tab == "attack" else tcod.grey
        tab_defense_color = tcod.white if self.current_tab == "defense" else tcod.grey
        
        tcod.console_set_default_foreground(self.console, tab_attack_color)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 2, "[A] Attaque")
        
        tcod.console_set_default_foreground(self.console, tab_defense_color)
        tcod.console_print(self.console, self.dashboard_x + 15, self.dashboard_y + 2, "[D] Défense")
        
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_hline(self.console, self.dashboard_x + 1, self.dashboard_y + 3, self.dashboard_width - 2)
        
        # Contenu de l'onglet
        if self.current_tab == "attack":
            self._draw_attack_tab(game_state, tower)
        elif self.current_tab == "defense":
            self._draw_defense_tab(game_state, tower)
        
        # Barre de rechargement
        self._draw_reload_bar(tower.reload_progress if tower else 0.0)
        
        # Score et vague
        tcod.console_set_default_foreground(self.console, tcod.yellow)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + self.dashboard_height - 3, 
                         f"Score: {game_state.get('score', 0)}")
        
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + self.dashboard_height - 2, 
                         f"Vague: {game_state.get('wave', 1)}")
    
    def _draw_attack_tab(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine l'onglet d'amélioration des attaques"""
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 5, 
                         "--- Améliorations d'Attaque ---")
        
        # Dégâts
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 7, 
                         f"[1] Dégâts (+1): Coût {10}")
        
        tcod.console_set_default_foreground(self.console, tcod.grey)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 8, 
                         f"    Actuel: {tower.damage if tower else 1}")
        
        # Portée
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 10, 
                         f"[2] Portée (+1): Coût {15}")
        
        tcod.console_set_default_foreground(self.console, tcod.grey)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 11, 
                         f"    Actuelle: {tower.range if tower else 3}")
        
        # Vitesse de tir
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 13, 
                         f"[S] Vitesse Tir (+0.2): Coût {25}")
        
        tcod.console_set_default_foreground(self.console, tcod.grey)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 14, 
                         f"    Actuelle: {tower.fire_rate:.1f if tower else 1.0}")
    
    def _draw_defense_tab(self, game_state: Dict[str, Any], tower: Tower):
        """Dessine l'onglet d'amélioration de la défense"""
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 5, 
                         "--- Améliorations de Défense ---")
        
        # Vie de la tour
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 7, 
                         f"[3] Vie de la Tour (+5): Coût {20}")
        
        tcod.console_set_default_foreground(self.console, tcod.grey)
        if tower:
            tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 8, 
                             f"    Actuelle: {tower.hp}/{game_state.get('max_tower_hp', 10)}")
        else:
            tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 8, 
                             f"    Actuelle: 0/0")
    
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
            color = tcod.green
        elif value > maximum // 4:
            color = tcod.yellow
        else:
            color = tcod.red
        
        tcod.console_set_default_foreground(self.console, color)
        tcod.console_print(self.console, x, y, f"HP: [{bar}]")
    
    def _draw_reload_bar(self, progress: float):
        """Dessine la barre de rechargement"""
        # Calculer le remplissage
        fill_length = int(self.RELOAD_BAR_LENGTH * progress)
        bar = self.RELOAD_BAR_CHAR_FULL * fill_length + self.RELOAD_BAR_CHAR_EMPTY * (self.RELOAD_BAR_LENGTH - fill_length)
        
        # Choisir la couleur en fonction de l'état
        color = tcod.cyan if progress >= 1.0 else tcod.grey
        
        tcod.console_set_default_foreground(self.console, color)
        tcod.console_print(self.console, self.dashboard_x + 2, self.dashboard_y + 16, f"Prêt: [{bar}]")
    
    def _draw_game_over(self):
        """Affiche l'écran de Game Over"""
        tcod.console_set_default_foreground(self.console, tcod.red)
        tcod.console_print_ex(self.console, self.screen_width // 2, self.screen_height // 2, 
                           tcod.BKGND_NONE, tcod.CENTER, "GAME OVER")
        
        tcod.console_set_default_foreground(self.console, tcod.white)
        tcod.console_print_ex(self.console, self.screen_width // 2, self.screen_height // 2 + 2, 
                           tcod.BKGND_NONE, tcod.CENTER, "Appuyez sur une touche pour quitter")
    
    def wait_for_keypress(self) -> Dict:
        """Attend une touche et retourne l'événement"""
        event = tcod.event.wait()
        return self._convert_event(event)
    
    def check_for_event(self) -> Dict:
        """Vérifie si un événement est disponible"""
        # Utiliser get() au lieu de poll()
        for event in tcod.event.get():
            if event.type == "QUIT":
                return {'type': 'QUIT'}
            elif event.type == "KEYDOWN":
                return self._convert_event(event)
        return {}
    
    def _convert_event(self, event) -> Dict:
        """Convertit un événement tcod en dictionnaire"""
        if event.type == "QUIT":
            return {'type': 'QUIT'}
        elif event.type == "KEYDOWN":
            return {
                'type': 'KEYDOWN',
                'key': event.sym,
                'alt': event.mod & tcod.event.KMOD_ALT,
                'ctrl': event.mod & tcod.event.KMOD_CTRL,
                'shift': event.mod & tcod.event.KMOD_SHIFT
            }
        return {}