# Add Your Name Here

"""Read a ping log file and report how fast the pings were.

Usage:
    uv run src/ping_stats.py                  (reads data/sample_ping_log.txt)
    uv run src/ping_stats.py data/ping_log.txt

This program does NOT need a network. It only practices reading a text file
and using lists and dictionaries.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(HERE, "..", "data", "sample_ping_log.txt")

# Pings faster than FAST_LIMIT are "fast"; faster than OK_LIMIT are "ok".
FAST_LIMIT = 20.0
OK_LIMIT = 50.0


def read_ping_times(filename):
    """Read the log file and return a list of round-trip times (floats)."""
    times = []
    # TODO 3: Open `filename` and read it line by line. Each line looks like
    # "3,12.5" (ping number, milliseconds). For each line:
    #   1. strip() the newline off the end,
    #   2. skip the line if it is empty,
    #   3. split(",") it into two pieces,
    #   4. convert the SECOND piece (index 1) to a float,
    #   5. append it to the `times` list.
    # Hint: with open(filename, "r") as log_file:
    # Hint:     for line in log_file:
    return times


def count_by_speed(times):
    """Return a dictionary that counts the "fast", "ok" and "slow" pings."""
    counts = {"fast": 0, "ok": 0, "slow": 0}
    for milliseconds in times:
        # TODO 4: Add 1 to the correct counter in the `counts` dictionary.
        # Hint: if milliseconds < FAST_LIMIT, then counts["fast"] += 1
        # Hint: use elif for "ok" (below OK_LIMIT) and else for "slow".
        pass
    return counts


def main():
    """Print a short report about the ping log."""
    filename = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_FILE
    times = read_ping_times(filename)
    if len(times) == 0:
        print("No pings found. Run ping_client.py first!")
        return

    print(f"Ping report for {os.path.basename(filename)}")
    print("-" * 32)
    print(f"Pings sent:   {len(times)}")
    print(f"Average:      {sum(times) / len(times):.1f} ms")
    print(f"Fastest:      {min(times):.1f} ms")
    print(f"Slowest:      {max(times):.1f} ms")
    counts = count_by_speed(times)
    for label, amount in counts.items():
        print(f"{label:>5} pings: {amount}")


if __name__ == "__main__":
    main()
