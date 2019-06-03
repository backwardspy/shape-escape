import sys

from engine import state


if __name__ == "__main__":
    state.game.run(enable_profiling="--profile" in sys.argv)
