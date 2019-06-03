import json
import string

import pyxel

from engine.constants import W, H


ALPHABET = string.ascii_uppercase + " "
MAX_ENTRIES = 10
MAX_LETTERS = 9


class Highscores:
    def __init__(self, highscore_filepath):
        self.highscore_filepath = highscore_filepath
        self.score_list = []
        self.load_highscores()
        self.name_letters = [" "] * MAX_LETTERS
        self.active_letter = 0
        self.alphabet_index = -1

    @property
    def name(self):
        return "".join(self.name_letters)

    def load_highscores(self):
        try:
            with open(self.highscore_filepath, "r") as highscores:
                self.score_list = json.load(highscores)
        except FileNotFoundError:
            self.score_list = []

    def _save_new(self, name, score):
        new_highscore = {"name": name, "score": score}
        self.score_list.append(new_highscore)
        self.score_list = self.ordered_score_list(include_placeholders=False)
        with open(self.highscore_filepath, "w") as highscore_file:
            json.dump(self.score_list, highscore_file)

    def check_highscores(self, score):
        current_highscores = [x["score"] for x in self.score_list]
        return any(score > highscore for highscore in current_highscores)

    def ordered_score_list(self, *, include_placeholders=True):
        scores = sorted(self.score_list, key=lambda k: k["score"], reverse=True)[
            :MAX_ENTRIES
        ]
        if include_placeholders and len(scores) < MAX_ENTRIES:
            scores.extend([None] * (MAX_ENTRIES - len(scores)))
        return scores

    def up(self):
        self.alphabet_index = (self.alphabet_index + 1) % len(ALPHABET)
        self.name_letters[self.active_letter] = ALPHABET[self.alphabet_index]

    def down(self):
        self.alphabet_index -= 1
        if self.alphabet_index < 0:
            self.alphabet_index = len(ALPHABET) - 1
        self.name_letters[self.active_letter] = ALPHABET[self.alphabet_index]

    def left(self):
        if self.active_letter > 0:
            self.active_letter -= 1
            self.alphabet_index = ALPHABET.index(self.name_letters[self.active_letter])

    def right(self):
        if self.active_letter < MAX_LETTERS - 1:
            self.active_letter += 1
            self.alphabet_index = ALPHABET.index(self.name_letters[self.active_letter])

    def enter(self, score):
        if all(l == " " for l in self.name_letters):
            return
        self._save_new(self.name, score)

    def draw(self):
        pyxel.text(W // 2 - 24, H // 2, "HIGH SCORES", 7)
        x = W // 2 - 48
        for i, score in enumerate(self.ordered_score_list()):
            y = H // 2 + (i + 1) * 8
            if score is not None:
                pyxel.text(
                    x, y, f"{score['name']: <{MAX_LETTERS}} .. {score['score']:012}", 7
                )
            else:
                pyxel.text(x, y, "- - - - - - - - - - - - -", 7)
