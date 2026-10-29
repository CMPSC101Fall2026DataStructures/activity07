# Add Your Name Here

"""The Haunted Forest game SERVER.

One person runs this program. It does NOT open a window. It keeps the
"truth" of the game (where everyone is, where the pumpkins are, who has the
most points) and tells every client about it 30 times each second.

Clients (game_client.py) only send what keys the player is holding and draw
whatever the server tells them. This is called a client-server game.

How the server and a client talk (one JSON message per line):

    client -> server    {"type": "join", "name": "Sam"}
                        {"type": "input", "dx": 1, "dy": 0}
                        {"type": "start"}
    server -> client    {"type": "welcome", "id": 1, "map": {...}}
                        {"type": "state", "players": {...}, "pumpkins": [...], ...}
"""

import json
import math
import os
import random
import socket
import threading
import time

import game_settings as cfg

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(HERE, "..", "maps", "forest.txt")
SCORES_FILE = os.path.join(HERE, "..", "data", "high_scores.txt")

# Which map character means which kind of thing. (A dictionary!)
KIND_BY_CHAR = {
    "#": "trees",
    "L": "logs",
    "S": "spawns",
    "G": "ghosts",
    "O": "owls",
}


def get_my_ip():
    """Return this computer's IP address on the local network as a string."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


# ---------------------------------------------------------------------------
# Reading and writing files
# ---------------------------------------------------------------------------
def load_map(filename):
    """Read the map text file and return a dictionary of lists of (col, row).

    The result looks like:
        {"trees": [(0, 0), (1, 0), ...], "logs": [...], "spawns": [...],
         "ghosts": [...], "owls": [...]}
    """
    tiles = {"trees": [], "logs": [], "spawns": [], "ghosts": [], "owls": []}
    with open(filename, "r") as map_file:
        lines = map_file.readlines()
    # TODO 1: Loop over the lines with a row number, and over each line with a
    # column number. For each character that is a key in KIND_BY_CHAR, add the
    # tuple (col, row) to the correct list in the `tiles` dictionary.
    # Hint: for row, line in enumerate(lines):
    # Hint:     for col, character in enumerate(line.strip()):
    # Hint:         if character in KIND_BY_CHAR:
    # Hint:             kind = KIND_BY_CHAR[character]
    # Hint:             tiles[kind].append((col, row))
    return tiles


def load_high_scores(filename):
    """Read the high score file and return a dictionary {player name: best score}."""
    scores = {}
    if not os.path.exists(filename):
        return scores
    # TODO 2: Each line of the file looks like "Sam,7". For each line:
    #   1. strip() it and skip it if it is empty,
    #   2. split(",") it into a name and a score,
    #   3. store   scores[name] = int(score)   (int() turns text into a number).
    # Hint: with open(filename, "r") as scores_file:
    return scores


def save_high_scores(filename, scores):
    """Write the scores dictionary to the file, best score first."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # sorted() with key=... sorts the (name, score) pairs by the score.
    ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
    with open(filename, "w") as scores_file:
        for name, score in ranked:
            scores_file.write(f"{name},{score}\n")


# ---------------------------------------------------------------------------
# The game world
# ---------------------------------------------------------------------------
def distance(x1, y1, x2, y2):
    """Straight-line distance between two points (the Pythagorean theorem)."""
    return math.hypot(x1 - x2, y1 - y2)


def tile_center(col, row):
    """Return the pixel position of the middle of a map tile."""
    return col * cfg.TILE + cfg.TILE / 2, row * cfg.TILE + cfg.TILE / 2


class GameWorld:
    """Everything that exists in the game, and the rules for how it changes."""

    def __init__(self, tiles, high_scores):
        self.tiles = tiles
        self.high_scores = high_scores
        # A set is a fast way to ask "is this tile a tree or a log?"
        self.blocked = set(tiles["trees"]) | set(tiles["logs"])
        self.players = {}          # {player id: dictionary of that player's data}
        self.next_id = 1
        self.phase = "lobby"       # "lobby" -> "playing" -> "over" -> "lobby"
        self.time_left = cfg.ROUND_SECONDS
        self.over_timer = 0.0
        self.winner_text = ""
        self.pumpkins = []         # list of [x, y]
        self.ghosts = []           # list of [x, y]
        self.owls = []             # list of dictionaries with x, y, vx, vy
        self.clock = 0.0
        self.reset_enemies()

    # -- players ------------------------------------------------------------
    def spawn_point(self, number):
        """Pick a starting position for the player with this number."""
        spawns = self.tiles["spawns"]
        if len(spawns) == 0:
            return tile_center(cfg.COLS // 2, cfg.ROWS // 2)
        col, row = spawns[number % len(spawns)]
        return tile_center(col, row)

    def add_player(self, name):
        """Create a new player and return their id number."""
        player_id = self.next_id
        self.next_id += 1
        x, y = self.spawn_point(player_id - 1)
        self.players[player_id] = {
            "name": name, "x": x, "y": y, "dx": 0, "dy": 0, "score": 0,
            "stun": 0.0, "safe": 0.0, "color": (player_id - 1) % len(cfg.PLAYER_COLORS),
        }
        return player_id

    def remove_player(self, player_id):
        self.players.pop(player_id, None)

    def set_input(self, player_id, dx, dy):
        """Remember which direction a player is pressing (-1, 0 or 1)."""
        if player_id in self.players:
            self.players[player_id]["dx"] = max(-1, min(1, int(dx)))
            self.players[player_id]["dy"] = max(-1, min(1, int(dy)))

    # -- the round ----------------------------------------------------------
    def start_round(self):
        """Begin a new round if we are in the lobby."""
        if self.phase != "lobby" or len(self.players) == 0:
            return
        for number, player in enumerate(self.players.values()):
            player["x"], player["y"] = self.spawn_point(number)
            player["score"] = 0
            player["stun"] = 0.0
            player["safe"] = 0.0
        self.reset_enemies()
        self.pumpkins = []
        for _ in range(cfg.PUMPKIN_COUNT):
            self.pumpkins.append(list(self.random_free_position()))
        self.time_left = cfg.ROUND_SECONDS
        self.phase = "playing"
        print("Round started!")

    def finish_round(self):
        """Work out the winner and update the high score dictionary."""
        best = max(player["score"] for player in self.players.values()) if self.players else 0
        winners = [p["name"] for p in self.players.values() if p["score"] == best]
        self.winner_text = " & ".join(winners) + f" won with {best} pumpkins!"
        for player in self.players.values():
            old_best = self.high_scores.get(player["name"], 0)
            self.high_scores[player["name"]] = max(old_best, player["score"])
        save_high_scores(SCORES_FILE, self.high_scores)
        self.phase = "over"
        self.over_timer = cfg.GAME_OVER_SECONDS
        print(self.winner_text)

    def random_free_position(self):
        """Return a random pixel position that is not inside a tree or log."""
        while True:
            col = random.randint(1, cfg.COLS - 2)
            row = random.randint(1, cfg.ROWS - 2)
            if (col, row) not in self.blocked:
                return tile_center(col, row)

    def reset_enemies(self):
        """Put every ghost and owl back at its starting tile from the map."""
        self.ghosts = [list(tile_center(c, r)) for c, r in self.tiles["ghosts"]]
        self.owls = []
        for col, row in self.tiles["owls"]:
            x, y = tile_center(col, row)
            self.owls.append({
                "x": x, "y": y,
                "vx": random.choice([-1, 1]) * cfg.OWL_SPEED * 0.8,
                "vy": random.choice([-1, 1]) * cfg.OWL_SPEED * 0.6,
            })

    # -- movement -----------------------------------------------------------
    def is_blocked(self, x, y):
        """True if a player centred at (x, y) would overlap a tree or log."""
        r = cfg.PLAYER_RADIUS
        for corner_x in (x - r, x + r):
            for corner_y in (y - r, y + r):
                tile = (int(corner_x // cfg.TILE), int(corner_y // cfg.TILE))
                if tile in self.blocked:
                    return True
        return False

    def move_player(self, player, dt):
        """Move one player, one axis at a time so they can slide along trees."""
        if player["stun"] > 0:
            return
        length = math.hypot(player["dx"], player["dy"])
        if length == 0:
            return
        # Dividing by length keeps diagonal movement from being faster.
        step_x = player["dx"] / length * cfg.PLAYER_SPEED * dt
        step_y = player["dy"] / length * cfg.PLAYER_SPEED * dt
        if not self.is_blocked(player["x"] + step_x, player["y"]):
            player["x"] += step_x
        if not self.is_blocked(player["x"], player["y"] + step_y):
            player["y"] += step_y

    def move_ghosts(self, dt):
        """Ghosts float (right through trees!) towards the nearest player."""
        for number, ghost in enumerate(self.ghosts):
            if len(self.players) == 0:
                continue
            nearest = min(
                self.players.values(),
                key=lambda p: distance(ghost[0], ghost[1], p["x"], p["y"]),
            )
            gap = distance(ghost[0], ghost[1], nearest["x"], nearest["y"])
            if gap > 1:
                ghost[0] += (nearest["x"] - ghost[0]) / gap * cfg.GHOST_SPEED * dt
                ghost[1] += (nearest["y"] - ghost[1]) / gap * cfg.GHOST_SPEED * dt

    def move_owls(self, dt):
        """Owls fly in straight lines and bounce off the edge of the forest."""
        low, high_x, high_y = cfg.TILE * 1.5, cfg.WIDTH - cfg.TILE * 1.5, cfg.HEIGHT - cfg.TILE * 1.5
        for owl in self.owls:
            owl["x"] += owl["vx"] * dt
            owl["y"] += owl["vy"] * dt
            if owl["x"] < low or owl["x"] > high_x:
                owl["vx"] = -owl["vx"]
            if owl["y"] < low or owl["y"] > high_y:
                owl["vy"] = -owl["vy"]

    # -- one update of the whole world -----------------------------------------
    def tick(self, dt):
        """Advance the world by `dt` seconds."""
        self.clock += dt
        if self.phase == "over":
            self.over_timer -= dt
            if self.over_timer <= 0:
                self.phase = "lobby"
            return
        if self.phase != "playing":
            return

        self.move_ghosts(dt)
        self.move_owls(dt)
        for player in self.players.values():
            player["stun"] = max(0.0, player["stun"] - dt)
            player["safe"] = max(0.0, player["safe"] - dt)
            self.move_player(player, dt)
            self.collect_pumpkins(player)
            self.check_enemy_hits(player)

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.finish_round()

    def collect_pumpkins(self, player):
        """Give a point for every pumpkin the player is touching."""
        for pumpkin in list(self.pumpkins):
            if distance(player["x"], player["y"], pumpkin[0], pumpkin[1]) < cfg.PICKUP_DISTANCE:
                self.pumpkins.remove(pumpkin)
                self.pumpkins.append(list(self.random_free_position()))
                player["score"] += 1

    def check_enemy_hits(self, player):
        """A ghost or owl touch costs one pumpkin and freezes you for a moment."""
        if player["safe"] > 0:
            return
        enemies = self.ghosts + [[owl["x"], owl["y"]] for owl in self.owls]
        for ex, ey in enemies:
            if distance(player["x"], player["y"], ex, ey) < cfg.HIT_DISTANCE:
                player["score"] = max(0, player["score"] - 1)
                player["stun"] = cfg.STUN_SECONDS
                player["safe"] = cfg.SAFE_SECONDS
                return

    # -- what we tell the clients -------------------------------------------------
    def snapshot(self):
        """Return a dictionary describing the world (it is sent as JSON)."""
        top_scores = sorted(self.high_scores.items(), key=lambda pair: pair[1], reverse=True)[:3]
        return {
            "type": "state",
            "phase": self.phase,
            "time_left": round(self.time_left, 1),
            "winner": self.winner_text,
            "top": top_scores,
            "players": {
                str(pid): {
                    "name": p["name"], "x": round(p["x"]), "y": round(p["y"]),
                    "score": p["score"], "color": p["color"],
                    "stunned": p["stun"] > 0, "safe": p["safe"] > 0,
                }
                for pid, p in self.players.items()
            },
            "pumpkins": [[round(x), round(y)] for x, y in self.pumpkins],
            "ghosts": [[round(x), round(y)] for x, y in self.ghosts],
            "owls": [[round(o["x"]), round(o["y"]), 1 if o["vx"] > 0 else -1] for o in self.owls],
        }


# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
world = None                  # the GameWorld (created in run_server)
world_lock = threading.Lock() # only one thread may change the world at a time
connections = {}              # {player id: socket}


def send_json(connection, message):
    """Send one dictionary to a client as a line of JSON text."""
    connection.sendall((json.dumps(message) + "\n").encode())


def handle_client(connection, address):
    """Look after ONE player. Runs in its own thread."""
    player_id = None
    try:
        reader = connection.makefile("r", encoding="utf-8")
        for line in reader:
            message = json.loads(line)
            kind = message.get("type")
            if kind == "join" and player_id is None:
                name = str(message.get("name", "ghost-hunter"))[:12]
                with world_lock:
                    player_id = world.add_player(name)
                welcome = {
                    "type": "welcome", "id": player_id,
                    "map": {"trees": world.tiles["trees"], "logs": world.tiles["logs"]},
                }
                send_json(connection, welcome)
                connections[player_id] = connection
                print(f"+ {name} joined from {address[0]} as player {player_id}")
            elif kind == "input" and player_id is not None:
                with world_lock:
                    world.set_input(player_id, message.get("dx", 0), message.get("dy", 0))
            elif kind == "start":
                with world_lock:
                    world.start_round()
    except (OSError, ValueError):
        pass
    finally:
        if player_id is not None:
            with world_lock:
                world.remove_player(player_id)
            connections.pop(player_id, None)
            print(f"- player {player_id} left")
        connection.close()


def accept_clients(server):
    """Wait for new players and start a thread for each one."""
    while True:
        try:
            connection, address = server.accept()
        except OSError:
            return
        threading.Thread(target=handle_client, args=(connection, address), daemon=True).start()


def run_server():
    """Load the files, open the port, then update and broadcast forever."""
    global world
    tiles = load_map(MAP_FILE)
    print(f"Map loaded: {len(tiles['trees'])} trees, {len(tiles['logs'])} logs, "
          f"{len(tiles['ghosts'])} ghosts, {len(tiles['owls'])} owls")
    high_scores = load_high_scores(SCORES_FILE)
    print(f"High scores loaded: {high_scores}")
    world = GameWorld(tiles, high_scores)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", cfg.PORT))
    server.listen()
    print("Haunted Forest server is running!")
    print(f"Tell your friends to connect to: {get_my_ip()}  (port {cfg.PORT})")
    print("Press Ctrl+C to stop.")
    threading.Thread(target=accept_clients, args=(server,), daemon=True).start()

    last = time.perf_counter()
    try:
        while True:
            time.sleep(1 / cfg.TICK_RATE)
            now = time.perf_counter()
            dt, last = now - last, now
            with world_lock:
                world.tick(dt)
                data = (json.dumps(world.snapshot()) + "\n").encode()
            for player_id, connection in list(connections.items()):
                try:
                    connection.sendall(data)
                except OSError:
                    connections.pop(player_id, None)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
