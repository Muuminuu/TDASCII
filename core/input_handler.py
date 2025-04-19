class InputHandler:
    def get_input(self):
        user_input = input("Commande > ")
        return user_input.strip().lower()