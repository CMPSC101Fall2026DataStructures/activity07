# Tutorial 1: The Ping Game

## Overview

In this tutorial you will play a **ping game**: one laptop runs a *server* that waits for signals, and another laptop runs a *client* that sends them. The client measures how long each signal takes to travel to the server and back, and saves every result in a text file. You will finish four small TODOs, run the game with a partner, and then read your saved results back into a list and a dictionary.

## What Is a Ping?

When you "ping" a computer you send it a tiny message and wait for an answer. The time between sending and receiving is the **round-trip time**, measured in milliseconds (1 millisecond = 0.001 seconds). Gamers care a lot about low ping, because it means your computer and the game server are in close contact.

```text
   Laptop A (client)                         Laptop B (server)
   ping_client.py                            ping_server.py
        |                                          |
        |---------- "PING 1" ------------------->  |
        |                                          |  (server builds a reply)
        |  <--------- "PONG 1" -------------------|
        |                                          |
   stop the stopwatch: round trip = 12.5 ms
```

### Key Vocabulary

| Term | Meaning |
| --- | --- |
| **IP address** | A number like `192.168.1.20` that identifies a computer on a network. |
| **port** | A number from 1024 to 65535 that identifies one program on that computer. This tutorial uses `5050`. |
| **server** | The program that waits for connections. |
| **client** | The program that connects to a server. |
| **socket** | One end of a connection. You send and receive through it. |
| **TCP** | A reliable way to send data. Bytes arrive in the order they were sent. Python calls it `SOCK_STREAM`. |
| **bytes** | The raw data that travels on a network. Python strings must be turned into bytes with `.encode()` and back into strings with `.decode()`. |
| **localhost** (`127.0.0.1`) | A special IP address that always means "this computer". |

## Part 1: Create the Shared Project Environment

This activity uses **one** virtual environment for all three tutorials. You create it **once**, at the top of the activity folder, and every tutorial uses it.

Move into the top folder of the activity (the folder that contains this activity's `README.md`):

```bash
cd Act07_sockets
```

Initialize the project and install `pygame-ce` (you will use it in Tutorial 3):

```bash
uv init --bare
uv add pygame-ce
```

Note: `uv init --bare` creates a bare starter project with only a `pyproject.toml` file in it. `uv add` creates the `.venv/` folder (the virtual environment) and records the library in `pyproject.toml` and `uv.lock`. Commit both of those files.

> **Important:** Do **not** run `uv init` inside the tutorial folders. When you run `uv run` from inside `tutorials/tutorial_01`, `uv` searches upward through the parent folders, finds the `pyproject.toml` file in `Act07_sockets`, and uses that one shared environment.

Move into the Tutorial 1 folder:

```bash
cd tutorials/tutorial_01
```

## Part 2: Find Your IP Address

Open `src/show_my_ip.py` and read it. The function `get_my_ip()` asks your computer which network connection it would use to reach the internet and returns the IP address of that connection. (No data is sent while doing this.) Replace `Add Your Name Here` at the top of the file with your name, then run:

```bash
uv run src/show_my_ip.py
```

### Example Output

```text
Your computer's name is: Sams-Laptop.local
Your IP address is:      192.168.1.20
Give this IP address to a classmate so they can connect to you!
```

Your numbers will be different. Write your IP address down and ask your partner for theirs.

## Part 3: Read the Server

Open `src/ping_server.py`. Here are the important ideas, in the order they happen in `run_server()`:

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
connection, address = server.accept()
```

1. `socket.socket(...)` creates a socket. `AF_INET` means "IPv4 addresses" and `SOCK_STREAM` means "TCP".
2. `bind((HOST, PORT))` claims port `5050` on this computer. `"0.0.0.0"` means "accept calls from any network".
3. `listen()` starts waiting for calls.
4. `accept()` **pauses** the program until a client connects. It gives you a *new* socket (`connection`) for talking to that client, and the client's `address`, which is a pair like `("192.168.1.21", 52814)`.

Then `handle_client()` repeats this loop:

```python
data = connection.recv(1024)
message = data.decode().strip()
reply = make_reply(message)
connection.sendall((reply + "\n").encode())
```

- `recv(1024)` waits for up to 1024 bytes to arrive. If it returns an empty result, the client hung up.
- `.decode()` turns bytes into a string. `.strip()` removes spaces and the newline at the end.
- `make_reply()` decides what to answer. (This is your first TODO!)
- `.encode()` turns the string back into bytes, and `sendall()` sends them.

Messages in this game look like `PING 3` or `SIGNAL ghost`. The first word is the **command**; the rest is the **argument**. Inside `make_reply()` the line `message.split(" ", 1)` cuts the message at the first space only, so `"SIGNAL big ghost"` becomes `["SIGNAL", "big ghost"]`.

### TODO 1

In `make_reply()`, find the `PING` branch. The variable `reply` is empty. Make the server answer `PONG` followed by a space and the argument, so `PING 3` is answered by `PONG 3`.

## Part 4: Read the Client

Open `src/ping_client.py`.

- `SIGNALS` is a **dictionary**. The menu keys (`"1"`, `"2"`, ...) are the dictionary *keys* and the signal words are the *values*. `send_signal()` loops over `SIGNALS.items()` to print the menu and uses `SIGNALS[choice]` to look up the word.
- `connection.connect((server_ip, PORT))` is the client's "dial the number" step.
- `play_ping_round()` uses `time.perf_counter()` as a stopwatch. It subtracts the start time from the end time and multiplies by 1000 to get milliseconds.
- `save_ping_to_log()` writes to `data/ping_log.txt`. It opens the file in **append** mode (`"a"`), which adds new lines to the end of the file without erasing the old ones. Each line looks like `3,12.5`: the ping number, a comma, and the milliseconds.

The `HERE` and `DATA_FOLDER` variables build the path to the `data` folder from the location of the Python file itself, so the program works no matter which folder you run it from.

### TODO 2

In `send_and_wait()`, the client never sends anything! Add the line that sends `text` plus a newline (`"\n"`) through the socket. Remember that sockets only send **bytes**, so you must `.encode()` the string.

## Part 5: Play the Ping Game

First, finish TODOs 1 and 2, and put your name at the top of each file.

**Computer A (the server)**: from `tutorials/tutorial_01`, run:

```bash
uv run src/ping_server.py
```

### Example Output

```text
PONG server is running!
Tell your partner to connect to: 192.168.1.20  (port 5050)
Press Ctrl+C to stop.
```

**Computer B (the client)**: run the client with Computer A's IP address:

```bash
uv run src/ping_client.py 192.168.1.20
```

Testing alone? Open two terminal windows on the same computer. Run the server in one, and run `uv run src/ping_client.py 127.0.0.1` in the other.

Choose option `1` to ping five times and option `2` to send a spooky signal.

### Example Output (client)

```text
Connected to 192.168.1.20!

1) Ping the server 5 times
2) Send a spooky signal
3) Quit
Your choice: 1
  PONG 1   round trip =   14.2 ms
  PONG 2   round trip =    9.8 ms
  PONG 3   round trip =   11.1 ms
  PONG 4   round trip =   35.6 ms
  PONG 5   round trip =   10.3 ms
```

On the server you will see each message arrive, such as `received: PING 1`. Play at least two ping rounds and send two signals. **Challenge your partner:** who can get the lowest average ping? (Hint: moving closer to the Wi-Fi router helps!)

When you choose `3` to quit, the file `data/ping_log.txt` is saved. Open it in your editor and look at it.

## Part 6: Read the Log Back In

Now you will analyze your saved pings. Open `src/ping_stats.py`. It reads a log file, and then reports the average, fastest, and slowest ping, and counts how many pings were `fast`, `ok`, or `slow`. This program does not use the network at all. It practices the file-reading skills from our lessons.

### TODO 3

In `read_ping_times()`, open the file, read it line by line, and fill the `times` **list** with the milliseconds (as floats) from every line. The comment in the code lists the five steps. For the line `3,12.5`, `line.split(",")` gives `["3", "12.5"]`, so you want the piece at index `1`.

### TODO 4

In `count_by_speed()`, the **dictionary** `counts` starts with every counter at `0`. For each time in the list, add `1` to the right counter. Use `FAST_LIMIT` and `OK_LIMIT` to decide.

Run the program on the sample data first:

```bash
uv run src/ping_stats.py
```

### Example Output

```text
Ping report for sample_ping_log.txt
--------------------------------
Pings sent:   7
Average:      25.9 ms
Fastest:      9.2 ms
Slowest:      74.0 ms
 fast pings: 4
   ok pings: 2
 slow pings: 1
```

Then run it on your own log:

```bash
uv run src/ping_stats.py data/ping_log.txt
```

## Understanding the Output

- `Address already in use` means an old copy of the server is still running. Close it with `Ctrl+C` or close its terminal window.
- `Connection refused` means nothing is listening. Is the server running? Did you type the right IP address?
- If the client hangs and nothing happens, check TODOs 1 and 2. A server that never replies leaves the client waiting forever.
- Round trips on `127.0.0.1` are tiny (under 1 ms) because the message never leaves your computer.

## Try It: Change the Signals

Add a fifth signal, such as `"5": "owl"`, to the `SIGNALS` dictionary in `ping_client.py`. Run the game again. You did not have to change the server at all, because it answers any signal word!

## What You Accomplished

You found your IP address, built the server and client halves of a TCP conversation, sent and received bytes, saved results to a file with append mode, and read them back into a list and a dictionary.

Next tutorial: [Tutorial 2: Direct Messages with a Chat Server](../tutorial_02/tutorial_02.md)
