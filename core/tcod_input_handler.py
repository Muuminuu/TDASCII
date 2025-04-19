import tcod
from typing import Dict, Any, Optional
from models.position import Position

class TcodInputHandler:
    """
    Gestionnaire d'entrée utilisant TCOD
    """
    def __init__(self, game_state: Dict[str, Any]):
        self.game_state = game_state
    
    def handle_input(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les entrées et retourne les actions à effectuer
        """
        action = {}
        
        if not event:
            return action
            
        if event['type'] == 'QUIT':
            action['quit'] = True
            return action
            
        if event['type'] != 'KEYDOWN':
            return action
            
        key = event.get('key', None)
        
        # Changement d'onglet
        if key == ord('a'):
            action['change_tab'] = 'attack'
        elif key == ord('d'):
            action['change_tab'] = 'defense'
            
        # Déplacement
        elif key == tcod.event.K_LEFT:
            action['move'] = (-1, 0)
        elif key == tcod.event.K_RIGHT:
            action['move'] = (1, 0)
        elif key == tcod.event.K_UP:
            action['move'] = (0, -1)
        elif key == tcod.event.K_DOWN:
            action['move'] = (0, 1)
            
        # Actions spécifiques à l'onglet
        if self.game_state.get('current_tab') == 'attack':
            # Amélioration des dégâts
            if key == ord('1') and self.game_state.get('score', 0) >= 10:
                action['upgrade'] = 'damage'
                action['cost'] = 10
                
            # Amélioration de la portée
            elif key == ord('2') and self.game_state.get('score', 0) >= 15:
                action['upgrade'] = 'range'
                action['cost'] = 15
                
            # Amélioration de la vitesse de tir
            elif key == ord('s') and self.game_state.get('score', 0) >= 25:
                action['upgrade'] = 'fire_rate'
                action['cost'] = 25
                
        elif self.game_state.get('current_tab') == 'defense':
            # Amélioration des points de vie
            if key == ord('3') and self.game_state.get('score', 0) >= 20:
                action['upgrade'] = 'hp'
                action['cost'] = 20
                
        # Déclencher manuellement la prochaine vague
        if key == tcod.event.K_SPACE:
            action['next_wave'] = True
            
        return action