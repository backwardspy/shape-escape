import pyxel

from engine import state, highscores
from engine.constants import STATE_MENU, W, H


class DeadState:
    def update(self):
        go_to_menu = False

        if state.has_set_high_score:
            if state.scoreboard.ready_to_save:
                state.scoreboard.save_new(state.scoreboard.highscore_name, state.score)
                go_to_menu = True
            else:
                if pyxel.btnp(pyxel.KEY_UP):
                    state.scoreboard.alphabet_direction = 1
                elif pyxel.btnp(pyxel.KEY_DOWN):
                    state.scoreboard.alphabet_direction = -1
                elif pyxel.btnp(pyxel.KEY_RIGHT):
                    state.scoreboard.move_direction = 1
                elif pyxel.btnp(pyxel.KEY_LEFT):
                    state.scoreboard.move_direction = -1
                state.scoreboard.update()
        elif pyxel.btnp(pyxel.KEY_SPACE):
            go_to_menu = True

        if go_to_menu:
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
            pyxel.text(W // 2 - 20, H // 2 - 32, state.scoreboard.highscore_name, 8)
            for i in range(0, highscores.MAX_LETTERS):
                x = W // 2 - 20 + i * 4
                top_y = H // 2 - 36
                bottom_y = top_y + 10
                if i == state.scoreboard.active_letter:
                    pyxel.blt(x, top_y, 0, 8, 0, 3, 2, 0)
                    pyxel.blt(x, bottom_y, 0, 11, 0, 3, 2, 0)
                else:
                    pyxel.blt(x, bottom_y, 0, 8, 4, 3, 1, 0)
        else:
            pyxel.text(W // 2 - 56, H // 2 - 24, "push space to return to menu", 7)

        state.scoreboard.draw()
