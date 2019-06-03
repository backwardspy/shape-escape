import json
import string

import pyxel

from engine.constants import W, H


ALPHABET = string.ascii_uppercase + " "
MAX_ENTRIES = 10
MAX_LETTERS = 9
DEFAULT_NAME = "_" * MAX_LETTERS


class Highscores:
    def __init__(self, highscore_filepath):
        self.highscore_filepath = highscore_filepath
        self.score_list = []
        self.load_highscores()
        self.needs_updating = False
        self.highscore_name = DEFAULT_NAME
        self.active_letter = 0
        self.ready_to_save = False
        self.alphabet_direction = 0
        self.move_direction = 0
        self.alphabet_index = -1

    def load_highscores(self):
        try:
            with open(self.highscore_filepath, "r") as highscores:
                self.score_list = json.load(highscores)
        except FileNotFoundError:
            self.score_list = []

        self.needs_updating = False

    def save_new(self, name, score):
        new_highscore = {"name": name, "score": score}
        self.score_list.append(new_highscore)
        self.score_list = self.ordered_score_list()
        with open(self.highscore_filepath, "w") as highscore_file:
            json.dump(self.score_list, highscore_file, indent=4)

    def check_highscores(self, score):
        current_highscores = [x["score"] for x in self.score_list]
        return any(score > highscore for highscore in current_highscores)

    def ordered_score_list(self):
        scores = sorted(self.score_list, key=lambda k: k["score"], reverse=True)[
            :MAX_ENTRIES
        ]
        if len(scores) < MAX_ENTRIES:
            scores.extend([dict(score=0, name="***")] * (MAX_ENTRIES - len(scores)))
        return scores

    def update(self):
        if self.active_letter >= MAX_LETTERS:
            self.ready_to_save = True
            return

        if self.move_direction > 0:
            if not self.highscore_name[self.active_letter] == "_":
                self.alphabet_index = -1
                self.active_letter += 1
            self.move_direction = 0
            return
        elif self.move_direction < 0:
            if self.active_letter > 0:
                self.active_letter -= 1
                self.alphabet_index = ALPHABET.index(
                    self.highscore_name[self.active_letter]
                )
            self.move_direction = 0
            return

        if self.alphabet_direction == 0:
            return

        if self.alphabet_direction > 0:
            self.alphabet_index = (self.alphabet_index + 1) % len(ALPHABET)
        elif self.alphabet_direction < 0:
            self.alphabet_index -= 1
            if self.alphabet_index < 0:
                self.alphabet_index = len(ALPHABET) - 1

        self.alphabet_direction = 0
        selected_letter = ALPHABET[self.alphabet_index]
        name = self.highscore_name
        new_name = (
            name[: self.active_letter]
            + selected_letter
            + name[self.active_letter + 1 :]
        )

        self.highscore_name = new_name

    def draw(self):
        pyxel.text(W // 2 - 24, H // 2, "HIGH SCORES", 7)
        for i, score in enumerate(self.ordered_score_list()):
            pyxel.text(
                W // 2 - 48,
                H // 2 + 8 + i * 8,
                f"{score['name']: <{MAX_LETTERS}} .. {score['score']:012}",
                7,
            )
