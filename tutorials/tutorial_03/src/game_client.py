# Add Your Name Here

"""The Haunted Forest game CLIENT (the part with the pretty pictures).

Usage:
    uv run src/game_client.py <server ip address> <your name>

Controls:
    Arrow keys or W A S D   walk through the forest
    ENTER                   start a round (from the lobby)
    ESC                     quit

Collect pumpkins in the dark forest. Ghosts and owls will steal a pumpkin
and freeze you for a moment. The player with the most pumpkins wins!
"""

import json
import math
import random
import socket
import sys
import threading

import pygame

import game_settings as cfg

# `shared` is a dictionary that the network thread fills in and the drawing
# loop reads. It is how the two parts of the program pass information around.
shared = {"welcome": None, "state": None, "connected": True}


# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
def send_json(connection, message):
    """Send one dictionary to the server as a line of JSON text."""
    # TODO 1: Turn `message` into JSON text with json.dumps(message), add a
    # newline ("\n") on the end, encode it into bytes, and send it.
    # Hint: connection.sendall((json.dumps(message) + "\n").encode())
    pass


def listen_to_server(connection):
    """Run in a background thread: read every line the server sends."""
    reader = connection.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            message = json.loads(line)
            if message["type"] == "welcome":
                shared["welcome"] = message
            elif message["type"] == "state":
                shared["state"] = message
    except (OSError, ValueError):
        pass
    shared["connected"] = False


# ---------------------------------------------------------------------------
# Drawing helpers: every picture is made from simple shapes (no image files!)
# ---------------------------------------------------------------------------
def draw_tree(surface, col, row):
    """A pine tree: a brown trunk with two green triangles."""
    x, y = col * cfg.TILE, row * cfg.TILE
    pygame.draw.rect(surface, cfg.TREE_TRUNK, (x + 12, y + 20, 8, 12))
    pygame.draw.polygon(surface, cfg.TREE_LEAVES, [(x + 16, y - 6), (x + 2, y + 22), (x + 30, y + 22)])
    pygame.draw.polygon(surface, cfg.TREE_LEAVES_2, [(x + 16, y - 12), (x + 6, y + 10), (x + 26, y + 10)])


def draw_log(surface, col, row):
    """A fallen log: a brown rounded rectangle with a lighter end ring."""
    x, y = col * cfg.TILE, row * cfg.TILE
    pygame.draw.rect(surface, cfg.LOG_BROWN, (x + 1, y + 7, 30, 18), border_radius=8)
    pygame.draw.circle(surface, cfg.LOG_RING, (x + 7, y + 16), 7)
    pygame.draw.circle(surface, cfg.LOG_BROWN, (x + 7, y + 16), 3, 1)


def draw_pumpkin(surface, x, y, size=1.0):
    """A jack-o'-lantern with a green stem."""
    r = int(11 * size)
    pygame.draw.ellipse(surface, cfg.PUMPKIN_DARK, (x - r - 3, y - r + 2, 2 * r + 6, 2 * r - 2))
    pygame.draw.ellipse(surface, cfg.PUMPKIN_ORANGE, (x - r, y - r + 1, 2 * r, 2 * r))
    pygame.draw.rect(surface, cfg.STEM_GREEN, (x - 2, y - r - 4, 4, 6))
    # two triangle eyes and a zig-zag mouth
    pygame.draw.polygon(surface, (50, 20, 0), [(x - 6, y - 3), (x - 2, y - 3), (x - 4, y - 7)])
    pygame.draw.polygon(surface, (50, 20, 0), [(x + 2, y - 3), (x + 6, y - 3), (x + 4, y - 7)])
    pygame.draw.lines(surface, (50, 20, 0), False,
                      [(x - 6, y + 3), (x - 3, y + 6), (x, y + 3), (x + 3, y + 6), (x + 6, y + 3)], 2)


def draw_ghost(surface, x, y, clock):
    """A see-through white ghost with a wavy bottom that bobs up and down."""
    bob = math.sin(clock * 4 + x) * 3
    y = y + bob
    ghost = pygame.Surface((36, 40), pygame.SRCALPHA)
    body = (*cfg.GHOST_WHITE, 190)
    pygame.draw.circle(ghost, body, (18, 15), 14)
    pygame.draw.rect(ghost, body, (4, 15, 28, 18))
    for i in range(4):
        pygame.draw.circle(ghost, body, (8 + i * 7, 33), 4)
    pygame.draw.circle(ghost, (20, 10, 40), (13, 14), 3)
    pygame.draw.circle(ghost, (20, 10, 40), (23, 14), 3)
    pygame.draw.ellipse(ghost, (20, 10, 40), (14, 21, 8, 7))
    surface.blit(ghost, (x - 18, y - 20))


def draw_owl(surface, x, y, direction, clock):
    """An owl with big yellow eyes and wings that flap."""
    flap = math.sin(clock * 12) * 9
    pygame.draw.polygon(surface, cfg.OWL_BROWN, [(x - 6, y), (x - 26, y - flap - 4), (x - 6, y + 10)])
    pygame.draw.polygon(surface, cfg.OWL_BROWN, [(x + 6, y), (x + 26, y - flap - 4), (x + 6, y + 10)])
    pygame.draw.ellipse(surface, cfg.OWL_BROWN, (x - 11, y - 12, 22, 28))
    for eye_x in (x - 5, x + 5):
        pygame.draw.circle(surface, cfg.OWL_EYE, (eye_x, y - 4), 5)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x + direction, y - 4), 2)
    pygame.draw.polygon(surface, (255, 150, 30), [(x - 2, y), (x + 2, y), (x, y + 5)])


def draw_player(surface, x, y, color_index, name, font, stunned, safe, clock):
    """A little witch: a coloured body, a pointy black hat, and a name tag."""
    # Flash on and off while safe so everyone can see you were hit.
    if safe and int(clock * 10) % 2 == 0:
        return
    color = cfg.PLAYER_COLORS[color_index]
    pygame.draw.circle(surface, color, (x, y), 11)
    pygame.draw.circle(surface, (255, 255, 255), (x - 4, y - 2), 2)
    pygame.draw.circle(surface, (255, 255, 255), (x + 4, y - 2), 2)
    pygame.draw.ellipse(surface, (20, 10, 30), (x - 15, y - 12, 30, 7))
    pygame.draw.polygon(surface, (20, 10, 30), [(x - 8, y - 9), (x + 8, y - 9), (x + 2, y - 28)])
    pygame.draw.rect(surface, cfg.PUMPKIN_ORANGE, (x - 8, y - 12, 16, 3))
    if stunned:
        for i in range(3):
            angle = clock * 8 + i * 2.1
            pygame.draw.circle(surface, (255, 240, 120),
                               (int(x + math.cos(angle) * 14), int(y - 26 + math.sin(angle) * 4)), 3)
    label = font.render(name, True, cfg.TEXT_WHITE)
    surface.blit(label, (x - label.get_width() // 2, y + 14))


def build_forest_layer(welcome):
    """Draw the parts that never move (floor, trees, logs) onto one picture."""
    layer = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
    layer.fill(cfg.FOREST_FLOOR)
    random.seed(7)  # the same seed means the same speckles on every computer
    for _ in range(500):
        spot = (random.randint(0, cfg.WIDTH), random.randint(0, cfg.HEIGHT))
        pygame.draw.circle(layer, cfg.FOREST_FLOOR_2, spot, random.randint(2, 5))
    for col, row in welcome["map"]["logs"]:
        draw_log(layer, col, row)
    # Draw trees from the top row down so lower trees overlap higher ones.
    for col, row in sorted(welcome["map"]["trees"], key=lambda tile: tile[1]):
        draw_tree(layer, col, row)
    return layer


def build_light_sprite(radius):
    """Make a soft circle of 'light' that we cut out of the darkness."""
    sprite = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    sprite.fill((255, 255, 255, 255))  # start fully dark, then carve out the glow
    for r in range(radius, 0, -4):
        alpha = int(235 * (r / radius) ** 2)
        pygame.draw.circle(sprite, (255, 255, 255, alpha), (radius, radius), r)
    return sprite


def draw_darkness(surface, light_sprites, lit_points):
    """Cover the screen in darkness, then cut a glow around each lantern."""
    darkness = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
    darkness.fill((*cfg.NIGHT, 235))
    for x, y, size in lit_points:
        sprite = light_sprites[size]
        # BLEND_RGBA_MIN keeps the smaller alpha, which makes a see-through hole.
        darkness.blit(sprite, (x - sprite.get_width() // 2, y - sprite.get_height() // 2),
                      special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(darkness, (0, 0))


def draw_scoreboard(surface, state, my_id, font):
    """Show every player and their pumpkins, with the leader at the top."""
    # TODO 2: Make a list of the player dictionaries sorted by score, highest first.
    # state["players"] is a dictionary like {"1": {"name": "Sam", "score": 3, ...}}
    # Hint: players = sorted(state["players"].values(), key=lambda p: p["score"], reverse=True)
    players = list(state["players"].values())
    y = 10
    for player in players:
        color = cfg.PLAYER_COLORS[player["color"]]
        text = font.render(f"{player['name']}: {player['score']}", True, color)
        surface.blit(text, (cfg.WIDTH - text.get_width() - 14, y))
        y += 24


def draw_glowing_pumpkins(surface, state, clock):
    """Draw every pumpkin. They glow a little so you can spot them in the dark."""
    # TODO 3: Loop over state["pumpkins"]. Each item is a list [x, y].
    # For each one, call:  draw_pumpkin(surface, x, y, size)
    # where size pulses with:  size = 1 + math.sin(clock * 3) * 0.1
    # Hint: for x, y in state["pumpkins"]:
    pass


def draw_banner(surface, lines, big_font, small_font):
    """Draw centred lines of text on a see-through panel."""
    panel = pygame.Surface((560, 40 + 44 * len(lines)), pygame.SRCALPHA)
    panel.fill((10, 5, 25, 215))
    pygame.draw.rect(panel, cfg.PUMPKIN_ORANGE, panel.get_rect(), 3, border_radius=6)
    for number, (text, color, use_big) in enumerate(lines):
        font = big_font if use_big else small_font
        label = font.render(text, True, color)
        panel.blit(label, (280 - label.get_width() // 2, 20 + number * 44))
    surface.blit(panel, (cfg.WIDTH // 2 - 280, cfg.HEIGHT // 2 - panel.get_height() // 2))


# ---------------------------------------------------------------------------
# The main program
# ---------------------------------------------------------------------------
def read_keys():
    """Return (dx, dy) for the keys that are being held: each is -1, 0 or 1."""
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
    dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
    return int(dx), int(dy)


def main():
    """Connect to the server, then run the window until the player quits."""
    server_ip = sys.argv[1] if len(sys.argv) > 1 else input("Server IP address (try 127.0.0.1): ").strip()
    name = sys.argv[2] if len(sys.argv) > 2 else input("Your name: ").strip() or "Player"

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect((server_ip, cfg.PORT))
    except OSError as error:
        print(f"Could not connect to {server_ip}:{cfg.PORT} -> {error}")
        return
    threading.Thread(target=listen_to_server, args=(connection,), daemon=True).start()
    send_json(connection, {"type": "join", "name": name})

    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Haunted Forest - Pumpkin Hunt")
    clock = pygame.time.Clock()
    small_font = pygame.font.Font(None, 24)
    mid_font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 56)
    light_sprites = {"big": build_light_sprite(150), "small": build_light_sprite(55)}

    forest_layer = None
    last_input = (0, 0)
    seconds = 0.0
    running = True

    while running:
        seconds += clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    send_json(connection, {"type": "start"})
        if not shared["connected"]:
            running = False

        welcome, state = shared["welcome"], shared["state"]
        if welcome is None or state is None:
            screen.fill(cfg.NIGHT)
            screen.blit(mid_font.render("Connecting to the haunted forest...", True, cfg.TEXT_ORANGE), (240, 300))
            pygame.display.flip()
            continue
        if forest_layer is None:
            forest_layer = build_forest_layer(welcome)

        # Only tell the server when the keys CHANGE (saves network traffic).
        current_input = read_keys()
        if current_input != last_input:
            send_json(connection, {"type": "input", "dx": current_input[0], "dy": current_input[1]})
            last_input = current_input

        # --- draw the world ---
        screen.blit(forest_layer, (0, 0))
        draw_glowing_pumpkins(screen, state, seconds)
        for x, y in state["ghosts"]:
            draw_ghost(screen, x, y, seconds)
        for x, y, direction in state["owls"]:
            draw_owl(screen, x, y, direction, seconds)

        my_id = str(welcome["id"])
        lit_points = []
        for pid, player in state["players"].items():
            lit_points.append((player["x"], player["y"], "big" if pid == my_id else "small"))
        for x, y in state["pumpkins"]:
            lit_points.append((x, y, "small"))
        draw_darkness(screen, light_sprites, lit_points)

        for pid, player in state["players"].items():
            draw_player(screen, player["x"], player["y"], player["color"], player["name"],
                        small_font, player["stunned"], player["safe"], seconds)

        # --- heads-up display ---
        me = state["players"].get(my_id)
        if me is not None:
            score_text = mid_font.render(f"Pumpkins: {me['score']}", True, cfg.TEXT_ORANGE)
            screen.blit(score_text, (cfg.WIDTH // 2 - 150, 8))
        time_text = mid_font.render(f"Time: {int(state['time_left'])}", True, cfg.TEXT_PURPLE)
        screen.blit(time_text, (cfg.WIDTH // 2 + 40, 8))
        draw_scoreboard(screen, state, my_id, small_font)

        if state["phase"] == "lobby":
            lines = [("HAUNTED FOREST", cfg.TEXT_ORANGE, True),
                     (f"{len(state['players'])} player(s) in the forest", cfg.TEXT_WHITE, False),
                     ("Press ENTER to start the round", cfg.TEXT_PURPLE, False)]
            for rank, (champ, best) in enumerate(state["top"], start=1):
                lines.append((f"#{rank} {champ}: {best} pumpkins", cfg.TEXT_WHITE, False))
            draw_banner(screen, lines, big_font, mid_font)
        elif state["phase"] == "over":
            draw_banner(screen, [("TIME'S UP!", cfg.TEXT_ORANGE, True),
                                 (state["winner"], cfg.TEXT_WHITE, False)], big_font, mid_font)

        pygame.display.flip()

    pygame.quit()
    connection.close()


if __name__ == "__main__":
    main()
