# Tutorial 2: Direct Messages with a Chat Server

## Overview

In Tutorial 1 the server talked to **one** client. In this tutorial you will build a chat system where **many** clients connect to one server at the same time and send **direct messages** to each other using IP addresses. The server keeps a **dictionary** of who is online, writes every message to a **log file**, and can read the file back to show your message history. The client has an **address book** file that turns names like `alice` into IP addresses.

You will finish four small TODOs (two in each Python file).

## How the Chat Works

The server is a post office. Nobody talks to each other directly; every message goes to the server, and the server forwards it.

```text
   Alice (192.168.1.20)          SERVER (192.168.1.50)          Bob (192.168.1.21)
         |                               |                              |
         |-- "DM 192.168.1.21 hi Bob" -->|                              |
         |                               |-- looks up 192.168.1.21      |
         |                               |   in the clients dictionary  |
         |                               |-- "FROM 192.168.1.20 hi Bob"->|
         |<-- "INFO sent to ..." --------|                              |
         |                               |-- writes a line to chat_log.txt
```

### Key Vocabulary

| Term | Meaning |
| --- | --- |
| **direct message (DM)** | A message that goes to exactly one person. |
| **thread** | A way for one program to do several things at the same time. The server uses one thread per connected client. |
| **dictionary** | Stores `key: value` pairs. The server's `clients` dictionary maps an IP address to that person's socket. |
| **protocol** | The agreed rules for what messages look like. Ours are simple lines such as `DM <ip> <text>`. |
| **log file** | A text file where a program records what happened. |
| **delimiter** | A character that separates fields. Our log uses `\|` (the pipe) and our contacts file uses `,`. |

## Part 1: Setup

You already created the shared environment in Tutorial 1. Move into the Tutorial 2 folder:

```bash
cd tutorials/tutorial_02
```

Open `src/chat_server.py`, `src/chat_client.py`, and `data/contacts.txt`. Replace `Add Your Name Here` at the top of each Python file with your name.

## Part 2: Read the Server

### The `clients` dictionary

```python
clients = {}
```

At the top of the server, `clients` starts empty. When someone connects, `handle_client()` adds them with `clients[client_id] = connection`. When they leave, it runs `clients.pop(client_id, None)`. The **client id** is the person's IP address. If two programs on the *same* computer connect (this happens when you test alone), the second one gets the id `ip:port` instead, so every key stays unique. That is what `make_client_id()` does.

### Threads: one helper per client

`server.accept()` pauses the program, so while the server is busy talking to one client it would never notice a second one. The fix is a **thread**:

```python
thread = threading.Thread(target=handle_client, args=(connection, address), daemon=True)
thread.start()
```

Every connected client gets its own copy of `handle_client()` running at the same time. `daemon=True` means "when the main program stops, stop this thread too."

### Reading lines

A TCP connection is a stream of bytes with no boundaries, so one `recv()` might return half a message or two messages stuck together. To avoid this problem we turn the socket into a file-like object:

```python
reader = connection.makefile("r", encoding="utf-8")
for line in reader:
```

Now we can read the socket one **line** at a time, just like reading a text file! This is why every message ends with `"\n"`.

### The commands

`handle_command()` splits each line into at most three parts and checks the first word:

| Client sends | What the server does |
| --- | --- |
| `DM <ip> <text>` | Delivers the message to that IP and logs it. |
| `WHO` | Lists the keys of the `clients` dictionary. |
| `HISTORY` | Reads your last 10 messages from the log file. |
| `QUIT` | Disconnects you. |

### The log file

`log_message()` appends one line to `data/chat_log.txt`:

```text
14:05:09|10.0.0.5|10.0.0.8|hello there
```

The fields are time, sender, target, and text, separated by `|`.

### `chat_server.py` TODO 1: `deliver_direct_message()`

If the target is a key in the `clients` dictionary, send them the message, log it, and return `True`. Otherwise return `False`. The three lines you need are written in the comment. Remember that `target_id in clients` checks the dictionary's **keys**.

### `chat_server.py` TODO 2: `read_history()`

Read the log file line by line. Split each line on `"|"`. Keep a line only if the sender (`fields[1]`) or the target (`fields[2]`) is `client_id`, and append a formatted string to the `history` **list**. The function then returns only the last `limit` items using the slice `history[-limit:]`.

You can test this function **without a network**. From `tutorials/tutorial_02`, run:

```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); import chat_server; print(*chat_server.read_history('10.0.0.5', filename='data/sample_chat_log.txt'), sep='\n')"
```

### Example Output

```text
[14:05:09] 10.0.0.5 -> 10.0.0.8: hello there
[14:05:31] 10.0.0.8 -> 10.0.0.5: hi! boo!
[14:06:02] 10.0.0.5 -> 10.0.0.9: did you see the ghost?
[14:07:15] 10.0.0.8 -> 10.0.0.5: see you at the party
```

Notice that the line between `10.0.0.9` and `10.0.0.8` is missing. It did not involve `10.0.0.5`.

## Part 3: Read the Client

The client does two jobs at once: it **waits for you to type**, and it **prints messages that arrive**. These two jobs would block each other, so the client also uses a thread. `show_incoming_messages()` runs in the background and prints every line from the server, while `main()` runs a loop around `input("> ")`.

### The address book

Remembering IP addresses is hard. `data/contacts.txt` lists a name and an IP address on each line, separated by a comma:

```text
me,127.0.0.1
alice,192.168.1.20
bob,192.168.1.21
```

Add your partner's real name and IP address to this file, one per line, with no spaces.

### `chat_client.py` TODO 1: `load_contacts()`

Read the contacts file into a **dictionary** `{name: ip}`. For each non-empty line, `split(",")` it into a name and an IP address, and store `contacts[name] = ip`.

### `chat_client.py` TODO 2: `resolve_target()`

If the user typed a name from the address book, return the matching IP address. If not, assume they typed a real IP and return it unchanged. The dictionary method `contacts.get(key, default)` does this in a single line.

## Part 4: Run the Chat

You need **one server** and **at least two clients**.

**Server** (one computer, one terminal):

```bash
uv run src/chat_server.py
```

### Example Output

```text
Chat server is running!
Tell your classmates to connect to: 192.168.1.50  (port 5060)
Press Ctrl+C to stop.
```

**Clients** (each person, in their own terminal):

```bash
uv run src/chat_client.py 192.168.1.50
```

Testing alone? Use `127.0.0.1` for the server address and open three terminal windows: one server and two clients.

Try these commands in a client:

```text
> /who
> /dm 192.168.1.21 Boo! Did I scare you?
> /dm alice meet me at the pumpkin patch
> /history
> /quit
```

### Example Output (two clients on one computer)

First client:

```text
Loaded 3 contacts: me, alice, bob

  [server] INFO welcome! your id is 127.0.0.1
> /who

  [server] INFO online: 127.0.0.1, 127.0.0.1:58414
> /dm 127.0.0.1:58414 hello from the first window
```

Second client:

```text
  >> 127.0.0.1 says: hello from the first window
```

When you test alone, the second client's id is `127.0.0.1:` followed by a port number. Use `/who` to find it.

Look at `data/chat_log.txt` after you have sent a few messages.

## Understanding the Output

- `ERROR nobody is connected as ...` means the IP address is not a key in the `clients` dictionary. Use `/who` to see the exact ids.
- If `/history` always says `no messages yet`, check `read_history()`. If `/dm alice ...` never works, check `load_contacts()` and `resolve_target()`.
- The server uses one thread per client, which is fine for a classroom but is not how very large chat services work.

## Try It: Add a Command

Add a `/me` command to the client that sends `WHO`. Or, add a new contact to `data/contacts.txt`, restart the client, and watch the `Loaded N contacts` line change.

## What You Accomplished

You built a multi-client chat system with threads, kept track of connections in a dictionary, logged messages to a file, read the file into a list, and loaded an address book file into a dictionary.

Next tutorial: [Tutorial 3: Haunted Forest, a Multiplayer Pumpkin Hunt](../tutorial_03/tutorial_03.md)
