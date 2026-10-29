# Tutorial 3: Haunted Forest, a Multiplayer Pumpkin Hunt

## Overview

In this tutorial you will play **Haunted Forest**, a colourful Halloween game for up to four players. You walk through a **dark forest** with only a small glow of light around you. Hunt for glowing **pumpkins**, dodge **ghosts** and **owls**, and squeeze between **trees** and **logs**. When the 60-second round ends, the player who collected the **most pumpkins** wins!

The game uses two libraries:

- `socket` to connect the players, just like the previous tutorials
- `pygame` to open a window and draw everything (you installed `pygame-ce` in Tutorial 1)

You will finish five small TODOs. Two of them read files into a **dictionary** and **lists**.

```text
                        +---------------------------+
                        |  game_server.py (host)    |
                        |  no window; knows the     |
                        |  truth about the game     |
                        +---------------------------+
                       /        |        |         \
        "input" keys  /         |        |          \   "state" snapshot
        (up/down/...)           |        |           \  30 times a second
                     v          v        v            v
            game_client.py  game_client.py  game_client.py  game_client.py
            (Player 1)      (Player 2)      (Player 3)      (Player 4)
            draws the forest and sends key presses
```

### Key Vocabulary

| Term | Meaning |
| --- | --- |
| **client-server game** | One program (the server) decides what is true. The others (clients) send key presses and draw what the server says. |
| **game loop** | A loop that runs many times per second: read input, update the world, draw a frame. |
| **tick** | One update of the game world. The server ticks 30 times per second. |
| **state / snapshot** | All of the information needed to draw one frame: where the players, pumpkins, ghosts, and owls are. |
| **JSON** | A text format for dictionaries and lists. `json.dumps()` turns Python data into text and `json.loads()` turns it back. |
| **tile** | One square of the map. Our map is 30 tiles wide and 20 tiles tall, and each tile is 32 pixels. |
| **pixel** | One dot on the screen. Positions are `(x, y)` with `(0, 0)` at the top-left corner. |

## Part 1: Setup

Move into the Tutorial 3 folder and open these files:

```bash
cd tutorials/tutorial_03
```

| File | Purpose |
| --- | --- |
| `src/game_settings.py` | Numbers and colours shared by the server and the client. |
| `src/game_server.py` | The host. It has no window. |
| `src/game_client.py` | The pygame window for each player. |
| `maps/forest.txt` | The map, drawn with text characters. |
| `data/sample_scores.txt` | Practice data for the high score file. |

Replace `Add Your Name Here` at the top of each Python file with your name.

## Part 2: The Map is a Text File

Open `maps/forest.txt`. Every character is one tile:

| Character | Meaning |
| --- | --- |
| `#` | a tree (blocks you) |
| `L` | a log (blocks you) |
| `S` | a player start point |
| `G` | where a ghost starts |
| `O` | where an owl starts |
| `.` | open forest floor |

```text
##############################
#S...#....L..G...#.....#....S#
#..#....##..........L......#.#
```

You can edit this file to design your own forest! Keep every row exactly 30 characters, and keep 20 rows.

### `game_server.py` TODO 1: `load_map()`

At the top of `game_server.py` there is a dictionary that connects characters to kinds of things:

```python
KIND_BY_CHAR = {"#": "trees", "L": "logs", "S": "spawns", "G": "ghosts", "O": "owls"}
```

`load_map()` opens the file and reads all the lines into a list. You must finish the loop that walks over every row and every column and records where each thing is. `enumerate()` gives you a counter along with each item:

```python
for row, line in enumerate(lines):
    for col, character in enumerate(line.strip()):
```

If the `character` is a key in `KIND_BY_CHAR`, look up its `kind` and add the tuple `(col, row)` to the right list in the `tiles` dictionary: `tiles[kind].append((col, row))`.

Test it without starting the game. From `tutorials/tutorial_03`, run:

```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); import game_server as g; print({k: len(v) for k, v in g.load_map(g.MAP_FILE).items()})"
```

### Example Output

```text
{'trees': 151, 'logs': 13, 'spawns': 4, 'ghosts': 3, 'owls': 2}
```

If every number is `0`, the TODO is not finished yet.

## Part 3: High Scores in a File

The server remembers each player's best score between games in `data/high_scores.txt`. `save_high_scores()` is already written. It sorts the dictionary with `sorted(..., key=lambda pair: pair[1], reverse=True)` and writes one `name,score` line per player. (A `lambda` is a tiny function with no name. Here it says "sort by the second item of each pair, the score.")

### `game_server.py` TODO 2: `load_high_scores()`

Read the file back into a **dictionary** `{name: best score}`. For every non-empty line, `split(",")` it into a name and a score, and store `scores[name] = int(score)`. `int()` is needed because everything you read from a file is text.

Test it:

```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); import game_server as g; print(g.load_high_scores('data/sample_scores.txt'))"
```

### Example Output

```text
{'Sam': 7, 'Ann': 5, 'Lee': 9}
```

## Part 4: Read the Rest of the Server

You do not need to change the rest of `game_server.py`, but you should read it. The comments explain every part.

- **`GameWorld`** is a *class* that holds everything in the game: the players, pumpkins, ghosts, owls, and the timer. A class keeps related data and functions together.
- **`tick(dt)`** moves everything forward by `dt` seconds. `dt` is the tiny amount of time since the last tick, so the game runs at the same speed on every computer.
- **`phase`** is the game's mode: `"lobby"` (waiting), `"playing"`, or `"over"` (showing the winner).
- **`move_player()`** moves one axis at a time (first left/right, then up/down). That lets you *slide* along a tree instead of getting stuck on it.
- **Ghosts** float straight through trees and slowly chase the nearest player. **Owls** fly in straight lines and bounce off the edges of the forest.
- **A hit** from a ghost or an owl costs you one pumpkin, freezes you for 1.5 seconds, and makes you safe (flashing) for 3 seconds.
- **`snapshot()`** builds a dictionary describing the world. The server turns it into JSON and sends it to every client on every tick.
- **`handle_client()`** runs in a thread for each player (just like the chat server). It reads one JSON line at a time: `join`, `input`, or `start`.

Why does the server decide everything? If every player moved their own character on their own computer, the players would disagree about who grabbed a pumpkin first. With one server, there is only one truth.

## Part 5: Read the Client

Open `src/game_client.py`.

- `shared` is a dictionary that is the meeting place between two threads. The **network thread** (`listen_to_server`) writes the latest `state` into it, and the **drawing loop** in `main()` reads it.
- `read_keys()` returns `(dx, dy)`, each `-1`, `0`, or `1`. The client only sends a message to the server when your keys **change**, which saves network traffic.
- The `draw_...` functions make every picture out of simple shapes such as circles, polygons, and rectangles. There are no image files.
- **The darkness.** `draw_darkness()` covers the whole screen with a nearly black layer and then cuts soft glowing holes for each player and each pumpkin. That is why you can only see what is near you.

### `game_client.py` TODO 1: `send_json()`

The client cannot tell the server anything yet! Turn the dictionary `message` into JSON text with `json.dumps(message)`, add `"\n"` at the end, `.encode()` it into bytes, and send it with `connection.sendall(...)`. This is the same pattern as Tutorials 1 and 2.

### `game_client.py` TODO 2: `draw_scoreboard()`

The server sends `state["players"]` as a dictionary like this:

```python
{"1": {"name": "Sam", "score": 3, "color": 0}, "2": {"name": "Ann", "score": 5, "color": 1}}
```

Use `sorted()` to make a **list** of just the player dictionaries (`state["players"].values()`) ordered by score, highest first. The code in the comment shows you the `key=lambda p: p["score"]` part. The leader will show at the top right of the window.

### `game_client.py` TODO 3: `draw_glowing_pumpkins()`

Loop over the list `state["pumpkins"]`. Each item is a list `[x, y]`. For each pumpkin, call `draw_pumpkin(surface, x, y, size)`. The `size` is already calculated for you with `math.sin`, so the pumpkins pulse gently.

## Part 6: Play the Game

First, finish all five TODOs.

**The host** (one person) opens a terminal in `tutorials/tutorial_03` and runs:

```bash
uv run src/game_server.py
```

### Example Output

```text
Map loaded: 151 trees, 13 logs, 3 ghosts, 2 owls
High scores loaded: {}
Haunted Forest server is running!
Tell your friends to connect to: 192.168.1.20  (port 5070)
Press Ctrl+C to stop.
```

**Every player, including the host**, opens another terminal and runs the client with the host's IP address and their own name:

```bash
uv run src/game_client.py 192.168.1.20 Sam
```

Playing alone? Use `127.0.0.1` as the IP address. You can start several clients on one computer to test with multiple players.

### Controls

| Key | Action |
| --- | --- |
| Arrow keys or `W` `A` `S` `D` | Walk |
| `ENTER` | Start a round (from the lobby) |
| `ESC` | Quit |

### How to Win

1. Wait in the lobby until everyone has joined, then anyone presses `ENTER`.
2. Look for the orange glow of pumpkins in the dark and walk into them to collect them.
3. Avoid the white ghosts (they chase you!) and the owls (they swoop in straight lines).
4. When the 60 seconds are up, the player with the **most pumpkins wins**. Ties share the win.
5. Your best score is saved to `data/high_scores.txt`, and the lobby shows the top three the next time.

> **Tip for groups:** Make the game harder by changing `GHOST_SPEED`, `OWL_SPEED`, or `PUMPKIN_COUNT` in `game_settings.py`. The **server** reads the rules, so only the host needs to change them. The map sizes must stay the same for everyone.

## Understanding the Output

- `Could not connect` means the server is not running, or the IP address is wrong. Check that all players are on the same Wi-Fi.
- The window says `Connecting to the haunted forest...` forever: the client could not send the `join` message, so check `send_json()` (TODO 1).
- Everything is dark and there are no pumpkins: check `draw_glowing_pumpkins()` (TODO 3). If there are no trees, check `load_map()` (TODO 1 in the server).
- If your character seems to be lagging, the Wi-Fi is busy. Move closer to the router, or try a phone hotspot.
- When a player closes their window, the server prints `- player N left` and removes them from the game.

## Try It: Design Your Own Forest

Copy `maps/forest.txt` to `maps/my_forest.txt`, then change a few `#`, `L`, `G`, and `O` characters. Change `MAP_FILE` in `game_server.py` to the new file name, restart the server, and explore your new forest. You did not need to change any drawing code, because the map is **data** in a file.

## What You Accomplished

You read a map from a text file into a dictionary of lists, loaded and saved high scores with a dictionary, sent JSON messages over a socket, sorted players into a leaderboard, and played a real multiplayer game built from the same ideas as the Ping game and the Chat server.

Return to the [README](../../README.md) and complete the reflection in [writing/reflection.md](../../writing/reflection.md).
