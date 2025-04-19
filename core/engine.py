from core.input_handler import InputHandler
from core.renderer import Renderer
from entities.tower import Tower
from entities.enemy import Enemy
from models.position import Position


class GameEngine:
    def __init__(self):
        self.is_running = True
        self.input_handler = InputHandler()
        self.renderer = Renderer()

        self.entities = []

        tower = Tower(Position(3, 0))
        enemy1 = Enemy(Position(6, 2))
        enemy2 = Enemy(Position(5, 2))

        self.entities.append(tower)
        self.entities.append(enemy1)
        self.entities.append(enemy2)

    def run(self):
        while self.is_running:
            self.handle_input()
            self.update()
            self.render()

    def handle_input(self):
        #TODO: utiliser InputHandler
        user_input = self.input_handler.get_input()
        if user_input == "q":
            self.is_running = False
        else:
            print(f"[INFO] Commande reçue : {user_input}")

    def update(self):
        print("\n[MOTEUR] Mise à jour des entités ... \n")
        for entity in self.entities:
            if entity.is_alive():
                entity.update()
            else:
                print(f"[INFO] Entité morte ignorée à {entity.position.x}, {entity.position.y}")

    def render(self):
        #TODO: utiliser renderer
        self.renderer.render(self.entities)