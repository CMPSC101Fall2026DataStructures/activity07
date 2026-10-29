# Add Your Name Here

"""Show the IP address of this computer.

Every computer on a network has an *IP address*, which works like a home
address for the computer. Other computers need your IP address to send
messages to you. Run this program on each laptop and write the address down.
"""

import socket


def get_my_ip():
    """Return this computer's IP address on the local network as a string."""
    # A UDP socket is the simplest way to ask "which network card would I use
    # to reach the internet?". No data is actually sent by connect() for UDP.
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        # No network? Fall back to "localhost", which always means "this computer".
        return "127.0.0.1"
    finally:
        probe.close()


if __name__ == "__main__":
    print("Your computer's name is:", socket.gethostname())
    print("Your IP address is:     ", get_my_ip())
    print("Give this IP address to a classmate so they can connect to you!")
