from core.game_engine import GameEngine

def main():
    # Créer et lancer le moteur de jeu
    engine = GameEngine(
        screen_width=80,
        screen_height=40,
        map_width=50,
        map_height=30,
        world_width=100,
        world_height=100
    )
    engine.run()

if __name__ == "__main__":
    main()