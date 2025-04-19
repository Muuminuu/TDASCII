import tcod
import random
import time

# === CONFIGURATION ===
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 30
MAP_WIDTH = 40
MAP_HEIGHT = 20

WORLD_WIDTH = 100
WORLD_HEIGHT = 100
TOWER_WORLD_X = WORLD_WIDTH // 2
TOWER_WORLD_Y = WORLD_HEIGHT // 2
VIEWPORT_X = TOWER_WORLD_X - MAP_WIDTH // 2
VIEWPORT_Y = TOWER_WORLD_Y - MAP_HEIGHT // 2
TOWER_SCREEN_X = MAP_WIDTH // 2
TOWER_SCREEN_Y = MAP_HEIGHT // 2
TOWER_CHAR = "T"

ENEMY_CHAR = "E"
SHOT_CHAR = "*"

HEALTH_BAR_LENGTH = 10
HEALTH_BAR_CHAR_FULL = "█"
HEALTH_BAR_CHAR_EMPTY = "░"

RELOAD_BAR_LENGTH = 10
RELOAD_BAR_CHAR_FULL = "●"
RELOAD_BAR_CHAR_EMPTY = "○"

DASHBOARD_WIDTH = SCREEN_WIDTH - MAP_WIDTH - 2
DASHBOARD_HEIGHT = SCREEN_HEIGHT - 2
DASHBOARD_X = MAP_WIDTH + 2
DASHBOARD_Y = 1

# === GLOBAL VARIABLES ===
WORLD = [['.' for _ in range(WORLD_WIDTH)] for _ in range(WORLD_HEIGHT)]
WORLD[TOWER_WORLD_Y][TOWER_WORLD_X] = 'T'

enemies = []
score = 50
tower_hp = 10
max_tower_hp = 10
wave = 1
spawn_timer = 0
spawn_interval = 60
enemies_per_wave = 1
enemy_speed = 0.5
enemy_hp_multiplier = 1.1

tower_damage = 1
tower_range = 5
tower_speed = 1

last_shot_time = 0
shoot_delay = 1.0 / tower_speed
reload_progress = 0.0
can_shoot = True

game_speed = 0.1
current_tab = "attack"

# === FUNCTIONS ===
def update_viewport():
    global VIEWPORT_X, VIEWPORT_Y, TOWER_WORLD_X, TOWER_WORLD_Y, WORLD_WIDTH, WORLD_HEIGHT
    VIEWPORT_X = max(0, min(TOWER_WORLD_X - MAP_WIDTH // 2, WORLD_WIDTH - MAP_WIDTH))
    VIEWPORT_Y = max(0, min(TOWER_WORLD_Y - MAP_HEIGHT // 2, WORLD_HEIGHT - MAP_HEIGHT))

def draw_map(console):
    console.draw_frame(1, 1, MAP_WIDTH, MAP_HEIGHT, "World View", clear=False)
    for y_screen in range(MAP_HEIGHT):
        for x_screen in range(MAP_WIDTH):
            world_x = VIEWPORT_X + x_screen
            world_y = VIEWPORT_Y + y_screen
            if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                console.print(x_screen + 1, y_screen + 1, WORLD[world_y][world_x], fg=(50, 50, 50))
    console.print(TOWER_SCREEN_X + 1, TOWER_SCREEN_Y + 1, TOWER_CHAR, fg=(255, 255, 0))

def draw_health_bar(console, hp, max_hp, x, y, length):
    filled_length = int(length * hp / max_hp)
    bar = HEALTH_BAR_CHAR_FULL * filled_length + HEALTH_BAR_CHAR_EMPTY * (length - filled_length)
    console.print(x, y, f"HP: [{bar}]", fg=(0, 255, 0) if hp > max_hp // 2 else (255, 255, 0) if hp > max_hp // 4 else (255, 0, 0))

def draw_reload_bar(console, progress, length):
    filled_length = int(length * progress)
    bar = RELOAD_BAR_CHAR_FULL * filled_length + RELOAD_BAR_CHAR_EMPTY * (length - filled_length)
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 15, f"Prêt: [{bar}]", fg=(0, 200, 255) if progress >= 1.0 else (100, 100, 100))

def draw_enemies(console):
    global tower_hp
    new_enemies = []
    for enemy in enemies:
        screen_x = int(enemy['x'] - VIEWPORT_X) + 1
        screen_y = int(enemy['y'] - VIEWPORT_Y) + 1
        if 1 <= screen_x < MAP_WIDTH + 1 and 1 <= screen_y < MAP_HEIGHT + 1:
            dx = (TOWER_SCREEN_X + 1) - screen_x
            dy = (TOWER_SCREEN_Y + 1) - screen_y
            move_x = 0
            move_y = 0
            if abs(dx) > 0:
                move_x = 1 if dx > 0 else -1
            if abs(dy) > 0:
                move_y = 1 if dy > 0 else -1

            enemy['x'] += move_x * enemy_speed
            enemy['y'] += move_y * enemy_speed

            if abs(screen_x - (TOWER_SCREEN_X + 1)) < 0.6 and abs(screen_y - (TOWER_SCREEN_Y + 1)) < 0.6:
                tower_hp -= 1
            else:
                new_enemies.append(enemy)
                console.print(int(enemy['x']), int(enemy['y']), ENEMY_CHAR, fg=(255, 0, 0))
        else:
            new_enemies.append(enemy)
    return new_enemies

def spawn_enemies():
    global enemies, spawn_timer, wave, enemies_per_wave, spawn_interval, WORLD_WIDTH, WORLD_HEIGHT
    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        num_to_spawn = int(enemies_per_wave * wave * 0.6) + 1
        for _ in range(num_to_spawn):
            side = random.choice(['top', 'bottom', 'left', 'right'])
            enemy_hp = int(wave * enemy_hp_multiplier) + 1
            if side == 'top':
                enemies.append({'x': random.randint(0, WORLD_WIDTH - 1), 'y': -1, 'hp': enemy_hp})
            elif side == 'bottom':
                enemies.append({'x': random.randint(0, WORLD_WIDTH - 1), 'y': WORLD_HEIGHT, 'hp': enemy_hp})
            elif side == 'left':
                enemies.append({'x': -1, 'y': random.randint(0, WORLD_HEIGHT - 1), 'hp': enemy_hp})
            elif side == 'right':
                enemies.append({'x': WORLD_WIDTH, 'y': random.randint(0, WORLD_HEIGHT - 1), 'hp': enemy_hp})

def draw_dashboard(console):
    console.draw_frame(DASHBOARD_X, DASHBOARD_Y, DASHBOARD_WIDTH, DASHBOARD_HEIGHT, "Dashboard", clear=False)

    tab_attack_color = (255, 255, 255) if current_tab == "attack" else (150, 150, 150)
    tab_defense_color = (255, 255, 255) if current_tab == "defense" else (150, 150, 150)

    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 2, "[A] Attaque", fg=tab_attack_color)
    console.print(DASHBOARD_X + 15, DASHBOARD_Y + 2, "[D] Défense", fg=tab_defense_color)
    console.hline(DASHBOARD_X + 1, DASHBOARD_Y + 3, DASHBOARD_WIDTH - 2)

    if current_tab == "attack":
        draw_attack_tab(console)
    elif current_tab == "defense":
        draw_defense_tab(console)

    draw_reload_bar(console, reload_progress, RELOAD_BAR_LENGTH)
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + DASHBOARD_HEIGHT - 3, f"Score: {score}", fg=(255, 255, 0))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + DASHBOARD_HEIGHT - 2, f"Wave: {wave}", fg=(255, 255, 255))

def draw_attack_tab(console):
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 5, "--- Améliorations d'Attaque ---", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 7, f"[1] Dégâts (+1): Coût {10}", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 8, f"    Actuel: {tower_damage}", fg=(150, 150, 150))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 10, f"[2] Portée (+1): Coût {15}", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 11, f"    Actuelle: {tower_range}", fg=(150, 150, 150))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 13, f"[S] Vitesse Tir (+0.2): Coût {25}", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 14, f"    Actuelle: {tower_speed:.1f}", fg=(150, 150, 150))

def draw_defense_tab(console):
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 5, "--- Améliorations de Défense ---", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 7, f"[3] Vie de la Tour (+5): Coût {20}", fg=(200, 200, 200))
    console.print(DASHBOARD_X + 2, DASHBOARD_Y + 8, f"    Actuelle: {tower_hp}/{max_tower_hp}", fg=(150, 150, 150))

def display_hud(console):
    draw_health_bar(console, tower_hp, max_tower_hp, 1, MAP_HEIGHT + 2, HEALTH_BAR_LENGTH)

def shoot_tower(console):
    global last_shot_time, score, enemies, can_shoot, reload_progress
    current_time = time.time()

    if can_shoot:
        for enemy in list(enemies):
            screen_x = int(enemy['x'] - VIEWPORT_X) + 1
            screen_y = int(enemy['y'] - VIEWPORT_Y) + 1
            dx = (TOWER_SCREEN_X + 1) - screen_x
            dy = (TOWER_SCREEN_Y + 1) - screen_y
            distance = (dx**2 + dy**2) ** 0.5
            if distance <= tower_range:
                console.print(screen_x, screen_y, SHOT_CHAR, fg=(0, 255, 0))
                enemy['hp'] -= tower_damage
                if enemy['hp'] <= 0:
                    enemies.remove(enemy)
                    score += 5
                last_shot_time = current_time
                can_shoot = False
                reload_progress = 0.0
                break
    else:
        reload_progress = min(1.0, (current_time - last_shot_time) / shoot_delay)
        if reload_progress >= 1.0:
            can_shoot = True

def handle_input(event):
    global score, wave, tower_damage, tower_range, spawn_timer, spawn_interval, current_tab, tower_hp, max_tower_hp, tower_speed, shoot_delay, TOWER_WORLD_X, TOWER_WORLD_Y
    if event.type == "KEYDOWN":
        if event.sym == tcod.event.K_a:
            current_tab = "attack"
        elif event.sym == tcod.event.K_d:
            current_tab = "defense"
        elif event.sym == tcod.event.K_LEFT:
            TOWER_WORLD_X = max(0, TOWER_WORLD_X - 1)
            update_viewport()
        elif event.sym == tcod.event.K_RIGHT:
            TOWER_WORLD_X = min(WORLD_WIDTH - 1, TOWER_WORLD_X + 1)
            update_viewport()
        elif event.sym == tcod.event.K_UP:
            TOWER_WORLD_Y = max(0, TOWER_WORLD_Y - 1)
            update_viewport()
        elif event.sym == tcod.event.K_DOWN:
            TOWER_WORLD_Y = min(WORLD_HEIGHT - 1, TOWER_WORLD_Y + 1)
            update_viewport()
        elif current_tab == "attack":
            if event.sym == tcod.event.K_1 and score >= 10:
                score -= 10
                tower_damage += 1
            elif event.sym == tcod.event.K_2 and score >= 15:
                score -= 15
                tower_range += 1
            elif event.sym == tcod.event.K_s and score >= 25:
                score -= 25
                tower_speed += 0.2
                shoot_delay = 1.0 / tower_speed
        elif current_tab == "defense":
            if event.sym == tcod.event.K_3 and score >= 20:
                score -= 20
                max_tower_hp += 5
                tower_hp += 5
        elif event.sym == tcod.event.K_SPACE:
            spawn_timer = spawn_interval

def main():
    with tcod.context.new(columns=SCREEN_WIDTH, rows=SCREEN_HEIGHT, title="Mobile ASCII Defense") as context:
        console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        global enemies, tower_hp, max_tower_hp, score, wave, spawn_timer, spawn_interval, game_speed, current_tab, last_shot_time, shoot_delay, can_shoot, reload_progress, WORLD, TOWER_WORLD_X, TOWER_WORLD_Y

        update_viewport() # Initialisation de la viewport

        while True:
            start_time = time.time()

            console.clear()

            # Draw map and enemies
            draw_map(console)
            enemies = draw_enemies(console)
            spawn_enemies()
            shoot_tower(console)

            # Draw dashboard
            draw_dashboard(console)

            # Basic HUD
            display_hud(console)

            # Game Over
            if tower_hp <= 0:
                console.print(MAP_WIDTH // 2 - 4 + 1, MAP_HEIGHT // 2 + 1, "GAME OVER", fg=(255, 0, 0))
                context.present(console)
                tcod.console_wait_for_keypress(True)
                break

            context.present(console)

            for event in tcod.event.wait(timeout=game_speed):
                if event.type == "QUIT":
                    raise SystemExit()
                handle_input(event)

            elapsed_time = time.time() - start_time
            sleep_time = max(0, game_speed - elapsed_time)
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()