# Add Your Name Here

"""The chat server: lets people send direct messages to each other by IP address.

Run this program on ONE laptop. Everybody else runs chat_client.py and
connects to this laptop's IP address.

Lines the CLIENT can send to the server:
    DM <ip> <text>   send a direct message to the person at that IP
    WHO              list everyone who is connected
    HISTORY          show your last 10 messages from the log file
    QUIT             disconnect

Lines the SERVER sends back:
    INFO <text>      a normal notice
    ERROR <text>     something went wrong
    FROM <ip> <text> a direct message for you
"""

import os
import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5060

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(HERE, "..", "data")
LOG_FILE = os.path.join(DATA_FOLDER, "chat_log.txt")

# A dictionary that remembers who is connected: {client id: socket}.
# The client id is the person's IP address (see make_client_id below).
clients = {}


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


def send_line(connection, text):
    """Send one line of text to a client."""
    connection.sendall((text + "\n").encode())


def make_client_id(ip, port):
    """Return the id for a new client: its IP address, made unique if needed.

    Two programs on the SAME laptop share one IP address (this happens when
    you test alone), so the second one is named "ip:port" instead.
    """
    if ip in clients:
        return f"{ip}:{port}"
    return ip


def log_message(sender_id, target_id, text):
    """Add one line to the chat log. Fields are separated by the | symbol."""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    stamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{stamp}|{sender_id}|{target_id}|{text}\n")


def read_history(client_id, limit=10, filename=LOG_FILE):
    """Return a list of the last `limit` log lines that involve `client_id`."""
    history = []
    if not os.path.exists(filename):
        return history
    # TODO 1: Read `filename` line by line. Each line looks like
    #   "14:05:09|10.0.0.5|10.0.0.8|hello"
    # For each line:
    #   1. strip() the newline and split("|") into 4 fields,
    #   2. keep the line ONLY if fields[1] (sender) or fields[2] (target)
    #      equals client_id,
    #   3. append a nice string such as f"[{fields[0]}] {fields[1]} -> {fields[2]}: {fields[3]}"
    #      to the `history` list.
    # Hint: with open(filename, "r") as log_file:
    # A slice with a negative number keeps only the LAST `limit` items.
    return history[-limit:]


def deliver_direct_message(sender_id, target_id, text):
    """Send `text` from one client to another. Return True if it was delivered."""
    # TODO 2: Look for target_id in the `clients` dictionary.
    # If it is there:
    #   - call send_line(clients[target_id], f"FROM {sender_id} {text}")
    #   - call log_message(sender_id, target_id, text)
    #   - return True
    # If it is NOT there, return False.
    # Hint: the test is   if target_id in clients:
    return False


def handle_command(client_id, connection, line):
    """Run one command line from a client. Return False when it wants to quit."""
    parts = line.split(" ", 2)
    command = parts[0].upper()

    if command == "DM" and len(parts) == 3:
        target_id, text = parts[1], parts[2]
        if deliver_direct_message(client_id, target_id, text):
            send_line(connection, f"INFO sent to {target_id}")
        else:
            send_line(connection, f"ERROR nobody is connected as {target_id}")
    elif command == "WHO":
        send_line(connection, "INFO online: " + ", ".join(clients.keys()))
    elif command == "HISTORY":
        past_messages = read_history(client_id)
        if len(past_messages) == 0:
            send_line(connection, "INFO no messages yet")
        for message in past_messages:
            send_line(connection, "INFO " + message)
    elif command == "QUIT":
        return False
    else:
        send_line(connection, "ERROR use: DM <ip> <text>, WHO, HISTORY or QUIT")
    return True


def handle_client(connection, address):
    """Look after ONE client. Each client gets its own copy of this function
    running in its own thread, so everyone can chat at the same time."""
    client_id = make_client_id(address[0], address[1])
    clients[client_id] = connection
    print(f"+ {client_id} joined ({len(clients)} online)")
    send_line(connection, f"INFO welcome! your id is {client_id}")
    try:
        # makefile() lets us read the socket one LINE at a time.
        reader = connection.makefile("r", encoding="utf-8")
        for line in reader:
            line = line.strip()
            if line == "":
                continue
            if not handle_command(client_id, connection, line):
                break
    except OSError:
        pass
    finally:
        # Remove the client from the dictionary and close its socket.
        clients.pop(client_id, None)
        connection.close()
        print(f"- {client_id} left ({len(clients)} online)")


def run_server():
    """Accept clients forever, starting a new thread for each one."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("Chat server is running!")
    print(f"Tell your classmates to connect to: {get_my_ip()}  (port {PORT})")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            connection, address = server.accept()
            # daemon=True means the thread stops when the program stops.
            thread = threading.Thread(
                target=handle_client, args=(connection, address), daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
