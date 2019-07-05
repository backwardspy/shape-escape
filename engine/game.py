from random import randint as rand, random as randf
import math
import sys

import pyxel

from engine.constants import W, H, STATE_MENU, STATE_GAME, STATE_DEAD
from engine.states import MenuState, GameState, DeadState


class Game:
    def __init__(self):
        pyxel.init(W - 1, H - 1, caption="Shape Escape", fps=60)
        pyxel.load("../assets.pyxres")

        self.state = MenuState()

    def run(self, *, enable_profiling):
        if enable_profiling:
            pyxel.run_with_profiler(self.update, self.draw)
        else:
            pyxel.run(self.update, self.draw)

    def update(self):
        self.state.update()

    def set_state(self, state):
        self.state = {
            STATE_MENU: MenuState,
            STATE_GAME: GameState,
            STATE_DEAD: DeadState,
        }[state]()

    def draw(self):
        self.state.draw()
