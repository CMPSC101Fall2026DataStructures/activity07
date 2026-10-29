# Add Your Name Here

"""The PONG server: waits for PING messages and answers them.

Run this program on ONE laptop. It listens on a *port* (a numbered door on
your computer) until another program connects to it.

Messages are lines of text that look like this:

    PING 3          -> the server answers  PONG 3
    SIGNAL ghost    -> the server answers  GOT SIGNAL: ghost
"""

import socket

from show_my_ip import get_my_ip

# "0.0.0.0" means: accept connections coming from ANY network card.
HOST = "0.0.0.0"
# The port number is the "door" that clients knock on. Pick 1024-65535.
PORT = 5050


def make_reply(message):
    """Turn one message from the client into the text we send back."""
    # split(" ", 1) cuts the message at the FIRST space only:
    # "SIGNAL big ghost" -> ["SIGNAL", "big ghost"]
    parts = message.split(" ", 1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    if command == "PING":
        # TODO 1: Set reply to the word "PONG", then a space, then the argument.
        # Hint: use + to join strings, or an f-string like f"PONG {argument}".
        reply = ""
    elif command == "SIGNAL":
        reply = "GOT SIGNAL: " + argument
    else:
        reply = "I do not understand: " + message
    return reply


def handle_client(connection, address):
    """Talk to one connected client until it hangs up."""
    print(f"Connected to {address[0]} (port {address[1]})")
    with connection:
        while True:
            # recv() waits until bytes arrive. It gives us at most 1024 bytes.
            data = connection.recv(1024)
            if not data:
                # An empty result means the client closed the connection.
                break
            # Network data is BYTES. decode() turns bytes into a normal string.
            message = data.decode().strip()
            print(f"  received: {message}")
            reply = make_reply(message)
            # encode() turns our string back into bytes so it can be sent.
            connection.sendall((reply + "\n").encode())
    print(f"{address[0]} disconnected")


def run_server():
    """Open the door (port) and serve one client at a time."""
    # AF_INET = IPv4 addresses, SOCK_STREAM = TCP (a reliable connection).
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Lets you restart the server right away without "address already in use".
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("PONG server is running!")
    print(f"Tell your partner to connect to: {get_my_ip()}  (port {PORT})")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            # accept() waits here until a client connects.
            connection, address = server.accept()
            handle_client(connection, address)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
