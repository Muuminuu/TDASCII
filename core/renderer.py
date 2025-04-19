class Renderer:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height

    def render(self):
        #Initialisation de la grille vide
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]

        #Placement des entité sur la grille
        for entity in entities:
            x = entity.position.x
            y = entity.position.y
            if 0 <= x < self.width and 0 <= y < self.height:
                symbol = self.get_symbol(entity)
                grid[x][y] = symbol
        
        # Affichage de la grille
        print("\n--- Grille de jeu ---")
        for row in grid:
            print(' '.join(row))
        print("---------------------\n")

    def get_symbol(self, entity):
        from entities.enemy import Enemy
        from entities.tower import Tower

        if isinstance(entity, Enemy):
            return 'E'
        elif isinstance(entity, Tower):
            return 'T'
        return '?'