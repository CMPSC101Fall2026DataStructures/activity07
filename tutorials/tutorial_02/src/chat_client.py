# Add Your Name Here

"""The chat client: type commands, send direct messages, read replies.

Usage:
    uv run src/chat_client.py <server ip address>

Commands you can type:
    /dm <name or ip> <message>   send a direct message
    /who                         see who is online
    /history                     see your last 10 messages
    /quit                        leave the chat

Names come from data/contacts.txt, a file with one "name,ip" pair per line.
"""

import os
import socket
import sys
import threading

PORT = 5060

HERE = os.path.dirname(os.path.abspath(__file__))
CONTACTS_FILE = os.path.join(HERE, "..", "data", "contacts.txt")


def load_contacts(filename):
    """Read the contacts file and return a dictionary {name: ip address}."""
    contacts = {}
    if not os.path.exists(filename):
        return contacts
    # TODO 1: Open `filename` and read it line by line. Each line looks like
    # "alice,192.168.1.20". For each line:
    #   1. strip() it and skip it if it is empty,
    #   2. split(",") it into [name, ip],
    #   3. store it with   contacts[name] = ip
    # Hint: with open(filename, "r") as contacts_file:
    return contacts


def resolve_target(target, contacts):
    """Turn a name like "alice" into her IP. Unknown names are used as-is."""
    # TODO 2: Return the IP stored for `target` in the `contacts` dictionary.
    # If `target` is not a key in the dictionary, return `target` unchanged
    # (the player typed a real IP address).
    # Hint: dictionary.get(key, default_value) does exactly this in one line.
    return target


def show_incoming_messages(connection):
    """Run in a background thread: print every line the server sends us."""
    reader = connection.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            line = line.strip()
            if line.startswith("FROM "):
                # "FROM 10.0.0.5 hi there" -> sender "10.0.0.5", text "hi there"
                _, sender, text = line.split(" ", 2)
                print(f"\n  >> {sender} says: {text}")
            else:
                print(f"\n  [server] {line}")
            print("> ", end="", flush=True)
    except OSError:
        pass
    print("\nDisconnected from the server.")


def handle_user_input(text, contacts):
    """Turn what the user typed into a command line for the server.

    Return None if there is nothing to send.
    """
    if text.startswith("/dm "):
        pieces = text.split(" ", 2)
        if len(pieces) < 3:
            print("  usage: /dm <name or ip> <message>")
            return None
        target = resolve_target(pieces[1], contacts)
        return f"DM {target} {pieces[2]}"
    if text == "/who":
        return "WHO"
    if text == "/history":
        return "HISTORY"
    if text == "/quit":
        return "QUIT"
    print("  commands: /dm <name or ip> <message>, /who, /history, /quit")
    return None


def main():
    """Connect, start the listening thread, then read the user's typing."""
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("Server IP address (try 127.0.0.1): ").strip()

    contacts = load_contacts(CONTACTS_FILE)
    print(f"Loaded {len(contacts)} contacts: {', '.join(contacts.keys())}")

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect((server_ip, PORT))
    except OSError as error:
        print(f"Could not connect to {server_ip}:{PORT} -> {error}")
        return

    # This thread prints incoming messages while the main loop waits for typing.
    listener = threading.Thread(
        target=show_incoming_messages, args=(connection,), daemon=True
    )
    listener.start()

    try:
        while True:
            text = input("> ").strip()
            line = handle_user_input(text, contacts)
            if line is None:
                continue
            connection.sendall((line + "\n").encode())
            if line == "QUIT":
                break
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    finally:
        connection.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
