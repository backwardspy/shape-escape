import pyxel

from engine import state, highscores
from engine.constants import STATE_MENU, W, H


class DeadState:
    def __init__(self):
        self.reset()

    def reset(self):
        pass

    def update(self):
        if state.has_set_high_score:
            if pyxel.btnp(pyxel.KEY_UP):
                state.scoreboard.up()
            elif pyxel.btnp(pyxel.KEY_DOWN):
                state.scoreboard.down()
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                state.scoreboard.right()
            elif pyxel.btnp(pyxel.KEY_LEFT):
                state.scoreboard.left()
            elif pyxel.btnp(pyxel.KEY_SPACE):
                state.scoreboard.enter(state.score)
                state.game.set_state(STATE_MENU)
        elif pyxel.btnp(pyxel.KEY_SPACE):
            state.game.set_state(STATE_MENU)

    def draw(self):
        pyxel.cls(0)

        lines = ["better luck next time", "", f"score: {state.score}"]
        for i, line in enumerate(lines):
            if line:
                pyxel.text((W - len(line) * 4) // 2, 24 + i * 8, line, 8)

        if state.has_set_high_score:
            pyxel.text(W // 2 - 28, H // 2 - 64, "new high score!", 7)
            pyxel.text(W // 2 - 20, H // 2 - 48, "ENTER NAME", 7)
            pyxel.text(W // 2 - 20, H // 2 - 32, state.scoreboard.name, 8)

            start_x = W // 2 - 20
            top_y = H // 2 - 36
            bottom_y = top_y + 10
            for i in range(0, highscores.MAX_LETTERS):
                if state.scoreboard.name_letters[i] == " ":
                    pyxel.blt(start_x + i * 4, bottom_y - 2, 0, 8, 3, 3, 1, 0)

            active_x = start_x + state.scoreboard.active_letter * 4
            pyxel.blt(active_x, top_y, 0, 8, 0, 3, 2, 0)
            pyxel.blt(active_x, bottom_y, 0, 11, 0, 3, 2, 0)
        else:
            pyxel.text(W // 2 - 56, H // 2 - 24, "push space to return to menu", 7)

        state.scoreboard.draw()
