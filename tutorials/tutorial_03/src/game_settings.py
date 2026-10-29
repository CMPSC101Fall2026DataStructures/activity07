# Add Your Name Here

"""Settings shared by the game server and the game client.

Both programs import this file, so they always agree on the size of the map,
the port number, and the colours. Change a number here and rebuild the fun!
"""

# --- Network ---------------------------------------------------------------
PORT = 5070

# --- The map ---------------------------------------------------------------
TILE = 32                 # each square of the map is 32 x 32 pixels
COLS = 30                 # map width in tiles
ROWS = 20                 # map height in tiles
WIDTH = COLS * TILE       # window width in pixels  (960)
HEIGHT = ROWS * TILE      # window height in pixels (640)

# --- Game rules (used by the server) ---------------------------------------
TICK_RATE = 30            # how many times per second the server updates the world
ROUND_SECONDS = 60        # how long one round lasts
PUMPKIN_COUNT = 12        # how many pumpkins are on the map at once
PLAYER_SPEED = 150        # pixels per second
GHOST_SPEED = 55          # ghosts drift slowly towards the nearest player
OWL_SPEED = 130           # owls swoop quickly across the forest
PLAYER_RADIUS = 11        # size of a player for bumping into trees
PICKUP_DISTANCE = 22      # how close you must be to grab a pumpkin
HIT_DISTANCE = 24         # how close a ghost or owl must be to hurt you
STUN_SECONDS = 1.5        # how long you freeze after being hit
SAFE_SECONDS = 3.0        # how long you are protected after being hit
GAME_OVER_SECONDS = 8     # how long the winner screen stays up

# --- Colours (red, green, blue) ---------------------------------------------
NIGHT = (14, 8, 30)
FOREST_FLOOR = (28, 22, 46)
FOREST_FLOOR_2 = (34, 27, 54)
TREE_TRUNK = (84, 52, 30)
TREE_LEAVES = (22, 92, 60)
TREE_LEAVES_2 = (34, 122, 78)
LOG_BROWN = (122, 78, 40)
LOG_RING = (176, 128, 74)
PUMPKIN_ORANGE = (255, 128, 0)
PUMPKIN_DARK = (204, 92, 0)
STEM_GREEN = (80, 190, 70)
GHOST_WHITE = (225, 235, 255)
OWL_BROWN = (150, 105, 70)
OWL_EYE = (255, 220, 40)
TEXT_ORANGE = (255, 150, 30)
TEXT_WHITE = (245, 240, 255)
TEXT_PURPLE = (190, 130, 255)

# One colour for each player (up to 4 players).
PLAYER_COLORS = [
    (255, 90, 160),    # pink
    (80, 200, 255),    # blue
    (160, 255, 90),    # lime
    (190, 120, 255),   # violet
]
