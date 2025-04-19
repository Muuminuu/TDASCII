import time
from entities.base import Entity
from models.position import Position

class Tower(Entity):
    """
    Représente une tour de défense qui peut tirer sur les ennemis
    """
    def __init__(self, position: Position, range: int = 3, damage: int = 1, fire_rate: float = 1.0):
        super().__init__(position, hp=99)
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate  # Tirs par seconde
        self.reload_time = 1.0 / fire_rate
        self.last_shot_time = 0
        self.reload_progress = 1.0  # 1.0 = prêt à tirer
    
    def update(self):
        """Met à jour l'état de la tour"""
        print(f"[TOUR] Prête à attaquer dans un rayon de {self.range}")
    
    def update_reload(self, delta_time: float):
        """Met à jour le temps de rechargement"""
        current_time = time.time()
        elapsed = current_time - self.last_shot_time
        
        self.reload_progress = min(1.0, elapsed / self.reload_time)
    
    def can_shoot(self) -> bool:
        """Vérifie si la tour peut tirer"""
        return self.reload_progress >= 1.0
    
    def shoot(self):
        """Marque la tour comme ayant tiré, réinitialise le rechargement"""
        self.last_shot_time = time.time()
        self.reload_progress = 0.0
    
    def upgrade_damage(self, amount: int = 1):
        """Améliore les dégâts de la tour"""
        self.damage += amount
        print(f"[TOUR] Dégâts améliorés à {self.damage}")
    
    def upgrade_range(self, amount: int = 1):
        """Améliore la portée de la tour"""
        self.range += amount
        print(f"[TOUR] Portée améliorée à {self.range}")
    
    def upgrade_fire_rate(self, amount: float = 0.2):
        """Améliore la cadence de tir de la tour"""
        self.fire_rate += amount
        self.reload_time = 1.0 / self.fire_rate
        print(f"[TOUR] Cadence de tir améliorée à {self.fire_rate:.1f} tirs/s")