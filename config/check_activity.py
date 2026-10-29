"""Automatic checks for Activity 07. GatorGrade runs this file; you do not edit it.

Usage:
    uv run config/check_activity.py <check name>

Each check tests one of the functions that you completed. No network and no
window are needed. A check exits with code 0 when it passes.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TUTORIALS = os.path.join(ROOT, "tutorials")


def use_tutorial(number):
    """Make the src folder of one tutorial importable."""
    sys.path.insert(0, os.path.join(TUTORIALS, f"tutorial_0{number}", "src"))


def check_make_reply():
    use_tutorial(1)
    import ping_server
    assert ping_server.make_reply("PING 7") == "PONG 7", "make_reply('PING 7') should be 'PONG 7'"


def check_send_and_wait():
    use_tutorial(1)
    import ping_client

    class FakeSocket:
        def __init__(self):
            self.sent = []

        def sendall(self, data):
            self.sent.append(data)

        def recv(self, size):
            return b"PONG 1\n"

    fake = FakeSocket()
    reply = ping_client.send_and_wait(fake, "PING 1")
    assert fake.sent == [b"PING 1\n"], "send_and_wait should send b'PING 1\\n'"
    assert reply == "PONG 1"


def check_read_ping_times():
    use_tutorial(1)
    import ping_stats
    sample = os.path.join(TUTORIALS, "tutorial_01", "data", "sample_ping_log.txt")
    times = ping_stats.read_ping_times(sample)
    assert times == [12.5, 18.0, 9.2, 31.0, 16.4, 74.0, 20.1], f"unexpected list: {times}"


def check_count_by_speed():
    use_tutorial(1)
    import ping_stats
    counts = ping_stats.count_by_speed([12.5, 18.0, 9.2, 31.0, 16.4, 74.0, 20.1])
    assert counts == {"fast": 4, "ok": 2, "slow": 1}, f"unexpected counts: {counts}"


def check_read_history():
    use_tutorial(2)
    import chat_server
    sample = os.path.join(TUTORIALS, "tutorial_02", "data", "sample_chat_log.txt")
    history = chat_server.read_history("10.0.0.5", filename=sample)
    assert len(history) == 4, f"expected 4 messages for 10.0.0.5, got {len(history)}"
    assert history[0] == "[14:05:09] 10.0.0.5 -> 10.0.0.8: hello there", history[0]
    assert len(chat_server.read_history("10.0.0.5", limit=2, filename=sample)) == 2


def check_deliver_direct_message():
    use_tutorial(2)
    import chat_server

    class FakeSocket:
        def __init__(self):
            self.sent = []

        def sendall(self, data):
            self.sent.append(data)

    chat_server.log_message = lambda *args: None  # do not write to the real log
    chat_server.clients.clear()
    fake = FakeSocket()
    chat_server.clients["10.0.0.8"] = fake
    assert chat_server.deliver_direct_message("10.0.0.5", "10.0.0.8", "boo") is True
    assert fake.sent == [b"FROM 10.0.0.5 boo\n"], f"unexpected data sent: {fake.sent}"
    assert chat_server.deliver_direct_message("10.0.0.5", "9.9.9.9", "boo") is False


def check_load_contacts():
    use_tutorial(2)
    import chat_client
    contacts = chat_client.load_contacts(os.path.join(TUTORIALS, "tutorial_02", "data", "contacts.txt"))
    assert isinstance(contacts, dict) and len(contacts) >= 3, f"unexpected contacts: {contacts}"
    assert contacts["me"] == "127.0.0.1"


def check_resolve_target():
    use_tutorial(2)
    import chat_client
    contacts = {"alice": "192.168.1.20"}
    assert chat_client.resolve_target("alice", contacts) == "192.168.1.20"
    assert chat_client.resolve_target("1.2.3.4", contacts) == "1.2.3.4"


def check_load_map():
    use_tutorial(3)
    import game_server
    tiles = game_server.load_map(game_server.MAP_FILE)
    counts = {kind: len(places) for kind, places in tiles.items()}
    expected = {"trees": 151, "logs": 13, "spawns": 4, "ghosts": 3, "owls": 2}
    assert counts == expected, f"expected {expected}, got {counts}"
    assert (0, 0) in tiles["trees"]


def check_load_high_scores():
    use_tutorial(3)
    import game_server
    scores = game_server.load_high_scores(os.path.join(TUTORIALS, "tutorial_03", "data", "sample_scores.txt"))
    assert scores == {"Sam": 7, "Ann": 5, "Lee": 9}, f"unexpected scores: {scores}"


def check_send_json():
    use_tutorial(3)
    import game_client

    class FakeSocket:
        def __init__(self):
            self.sent = []

        def sendall(self, data):
            self.sent.append(data)

    fake = FakeSocket()
    game_client.send_json(fake, {"type": "start"})
    assert fake.sent == [b'{"type": "start"}\n'], f"unexpected data sent: {fake.sent}"


def check_scoreboard():
    use_tutorial(3)
    import game_client
    drawn = []

    class FakeText:
        def get_width(self):
            return 0

    class FakeFont:
        def render(self, text, antialias, color):
            drawn.append(text)
            return FakeText()

    class FakeSurface:
        def blit(self, image, position):
            pass

    state = {"players": {
        "1": {"name": "Sam", "score": 3, "color": 0},
        "2": {"name": "Ann", "score": 5, "color": 1},
    }}
    game_client.draw_scoreboard(FakeSurface(), state, "1", FakeFont())
    assert drawn == ["Ann: 5", "Sam: 3"], f"leader should be first, got {drawn}"


def check_pumpkins():
    use_tutorial(3)
    import game_client
    drawn = []
    game_client.draw_pumpkin = lambda surface, x, y, size=1.0: drawn.append((x, y))
    game_client.draw_glowing_pumpkins(None, {"pumpkins": [[10, 20], [30, 40]]}, 0.0)
    assert drawn == [(10, 20), (30, 40)], f"expected both pumpkins to be drawn, got {drawn}"


CHECKS = {
    "make_reply": check_make_reply,
    "send_and_wait": check_send_and_wait,
    "read_ping_times": check_read_ping_times,
    "count_by_speed": check_count_by_speed,
    "read_history": check_read_history,
    "deliver_direct_message": check_deliver_direct_message,
    "load_contacts": check_load_contacts,
    "resolve_target": check_resolve_target,
    "load_map": check_load_map,
    "load_high_scores": check_load_high_scores,
    "send_json": check_send_json,
    "scoreboard": check_scoreboard,
    "pumpkins": check_pumpkins,
}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CHECKS:
        print("usage: uv run config/check_activity.py <" + "|".join(CHECKS) + ">")
        sys.exit(2)
    try:
        CHECKS[sys.argv[1]]()
    except Exception as error:
        print(f"FAIL {sys.argv[1]}: {type(error).__name__}: {error}")
        sys.exit(1)
    print(f"PASS {sys.argv[1]}")
