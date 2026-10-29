# Add Your Name Here

"""The PING client: sends PING messages and sends spooky signals.

Usage:
    uv run src/ping_client.py <server ip address>

Every ping's round-trip time (in milliseconds) is saved to data/ping_log.txt,
one line per ping, like this:   1,12.5
"""

import os
import socket
import sys
import time

PORT = 5050

# A dictionary: each menu key is paired with a signal word.
SIGNALS = {
    "1": "wave",
    "2": "ghost",
    "3": "pumpkin",
    "4": "bat",
}

# Build the path to data/ping_log.txt no matter where we run the program from.
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(HERE, "..", "data")
LOG_FILE = os.path.join(DATA_FOLDER, "ping_log.txt")


def send_and_wait(connection, text):
    """Send one line of text to the server and return its one-line answer."""
    # TODO 2: Send `text` plus a newline ("\n") to the server.
    # Hint: sockets send BYTES, so call .encode() on the string first.
    # Hint: connection.sendall((text + "\n").encode())
    # Wait for the reply, turn the bytes back into a string, trim the newline.
    return connection.recv(1024).decode().strip()


def save_ping_to_log(number, milliseconds):
    """Add one line to the log file. Mode "a" means APPEND (keep old lines)."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{number},{milliseconds:.1f}\n")


def play_ping_round(connection, how_many):
    """Send `how_many` pings and print how long each one took."""
    for number in range(1, how_many + 1):
        start = time.perf_counter()
        reply = send_and_wait(connection, f"PING {number}")
        # Round-trip time: how long until the answer came back, in milliseconds.
        milliseconds = (time.perf_counter() - start) * 1000
        print(f"  {reply:<8} round trip = {milliseconds:6.1f} ms")
        save_ping_to_log(number, milliseconds)
        time.sleep(0.3)


def send_signal(connection):
    """Let the player choose a spooky signal from the SIGNALS dictionary."""
    print("Choose a signal to send:")
    for key, word in SIGNALS.items():
        print(f"  {key}) {word}")
    choice = input("Your choice: ").strip()
    if choice in SIGNALS:
        reply = send_and_wait(connection, f"SIGNAL {SIGNALS[choice]}")
        print("  Server says:", reply)
    else:
        print("  That is not on the menu.")


def main():
    """Connect to the server, then show a menu until the player quits."""
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("Server IP address (try 127.0.0.1): ").strip()

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect() knocks on the server's door: (ip address, port).
        connection.connect((server_ip, PORT))
    except OSError as error:
        print(f"Could not connect to {server_ip}:{PORT} -> {error}")
        return
    print(f"Connected to {server_ip}!")

    with connection:
        while True:
            print("\n1) Ping the server 5 times")
            print("2) Send a spooky signal")
            print("3) Quit")
            choice = input("Your choice: ").strip()
            if choice == "1":
                play_ping_round(connection, 5)
            elif choice == "2":
                send_signal(connection)
            elif choice == "3":
                break
    print("Goodbye! Your pings are saved in data/ping_log.txt")


if __name__ == "__main__":
    main()
