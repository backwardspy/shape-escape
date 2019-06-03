import pyxel

from engine.constants import W, H, MUSIC_MENU, STATE_GAME
from engine import state

TEXT = "push space to begin"
TEXT_LEN = len(TEXT)
COLOUR_CYCLE_BASE = [6, 13, 5, 1]
COLOUR_CYCLE = [6, 13, 5, 1, 5, 13]
COLOUR_CYCLE_LEN = len(COLOUR_CYCLE)


class MenuState:
    def __init__(self):
        self.reset()

    def reset(self):
        pyxel.pal()
        pyxel.playm(MUSIC_MENU, loop=True)

        self.palette_cycle_timer = 0
        self.palette_cycle = 0

    def update(self):
        if self.palette_cycle_timer < 5:
            self.palette_cycle_timer += 1
        else:
            self.palette_cycle_timer = 0
            self.palette_cycle = (self.palette_cycle + 1) % COLOUR_CYCLE_LEN
            for i, colour in enumerate(COLOUR_CYCLE_BASE):
                pyxel.pal(
                    colour, COLOUR_CYCLE[(self.palette_cycle + i) % COLOUR_CYCLE_LEN]
                )

        if pyxel.btnp(pyxel.KEY_SPACE):
            state.game.set_state(STATE_GAME)

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 32, 16)
        pyxel.text((W - TEXT_LEN * 4) // 2, H - 24, TEXT, 6)

        state.scoreboard.draw()
