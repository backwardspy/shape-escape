from random import randint as rand, random as randf
import math
import sys

import pyxel

from highscores import Highscores

W = 256
H = 256

TWO_PI = math.pi * 2

MENU_TEXT = "push space to begin"
MENU_TEXT_LEN = len(MENU_TEXT)
MENU_COLOUR_CYCLE_BASE = [6, 13, 5, 1]
MENU_COLOUR_CYCLE = [6, 13, 5, 1, 5, 13]
MENU_COLOUR_CYCLE_LEN = len(MENU_COLOUR_CYCLE)


def btni(key):
    return 1 if pyxel.btn(key) else 0


def lerp(a, b, v):
    return a + (b - a) * v


def lerpi(a, b, v):
    return int(lerp(a, b, v))


def sgn(v):
    if v < 0:
        return -1
    elif v > 0:
        return 1
    return 0


def sgnz(v):
    if v <= 0:
        return -1
    return 1


def wrap_ang(a):
    if a > TWO_PI:
        a -= TWO_PI
    if a < 0:
        a += TWO_PI
    return a


class Shape:
    def __init__(self, segment, depth, thickness, colour):
        self.segment = segment
        self.depth = depth
        self.thickness = thickness
        self.colour = colour


class TextParticle:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.life = 30
        self.age = 0

    def update(self):
        self.y -= 1
        if self.age < self.life:
            self.age += 1

    def draw(self, cam_x, cam_y):
        colour = 5 + int(3 * (1 - self.age / self.life))
        pyxel.text(self.x - cam_x, self.y - cam_y, self.text, colour)


class Particle:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = rand(30, 40)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.99
        self.vy *= 0.99
        if self.age < self.life:
            self.age += 1

    def draw(self, cam_x, cam_y):
        colour = 7 - int(3 * (self.age / self.life))
        pyxel.circ(self.x - cam_x, self.y - cam_y, 1, colour)


class ObjectPool:
    class Object:
        def __init__(self, value):
            self.value = value
            self.alive = True

    def __init__(self):
        self.objects = []

    def insert(self, value):
        new = self.Object(value)
        for i, obj in enumerate(self.objects):
            if obj.alive is False:
                self.objects[i] = new
                break
        else:
            self.objects.append(new)

    def each(self):
        for i, obj in enumerate(self.objects):
            if obj.alive:
                yield i, obj.value

    def kill(self, i):
        self.objects[i].alive = False


class Game:
    MENU = 0
    GAME = 1
    DEAD = 2

    def __init__(self):
        pyxel.init(W - 1, H - 1, caption="Shape Escape", fps=60)
        pyxel.load("assets.pyxel")

        self.high_score = 0
        self.has_set_high_score = False
        self.reset_score()

        self.update_functions = {
            self.MENU: self.update_menu,
            self.GAME: self.update_game,
            self.DEAD: self.update_dead,
        }
        self.draw_functions = {
            self.MENU: self.draw_menu,
            self.GAME: self.draw_game,
            self.DEAD: self.draw_dead,
        }
        self.state = self.MENU
        self.reset()

        pyxel.playm(0, loop=True)

    def reset(self):
        pyxel.pal()  # reset the palette after cycling

        self.highscores = Highscores("highscores")
        self.high_score = self.highscores.ordered_score_list()[0]["score"]

        self.shapes = ObjectPool()
        self.score_particles = ObjectPool()
        self.particles = ObjectPool()
        self.segments = 6
        self.rotation = 0
        self.rotation_speed = 0.001

        self.last_segment = 0

        self.start_spawn_interval = 3 * 60  # frames
        self.end_spawn_interval = 45
        self.spawn_timer = 0

        self.speed = 1  # pixel/frame

        self.difficulty_duration = (
            60 * 60 * 2
        )  # how long it takes to get to 1.0 difficulty multiplier in frames
        self.difficulty_timer = 0
        self.difficulty = 0  # actual difficulty quotient from 0..1

        self.player_ang = 0

        self.cam_x = 0
        self.cam_y = 0
        self.cam_punch = 0

        self.palette_cycle_timer = 0
        self.palette_cycle = 0

        self.segment_line_cycle = 0
        self.segment_line_cycle_timer = 0

    def reset_score(self):
        self.score = 0
        self.display_score = 0
        self.has_set_high_score = False

    def run(self, *, enable_profiling):
        if enable_profiling:
            pyxel.run_with_profiler(self.update, self.draw)
        else:
            pyxel.run(self.update, self.draw)

    def spawn_shape(self):
        seg = rand(0, self.segments - 1)
        thickness = 8
        colour = rand(8, 12)
        n_segments = rand(3, self.segments - 1)
        for i in range(n_segments):
            si = (seg + i) % self.segments
            self.shapes.insert(Shape(si, 256, thickness, colour))

    def increment_score(self):
        points = int(250 * (2 ** (self.difficulty * 3)))
        self.score += points
        if self.score > self.high_score:
            self.has_set_high_score = True
            self.high_score = self.score

        self.score_particles.insert(TextParticle(W // 2 + 24, H // 2, f"{points} pts"))

        for _ in range(30):
            ang = randf() * TWO_PI
            ax = math.cos(ang)
            ay = math.sin(ang)
            v = 8.0 + randf() * 2.0
            self.particles.insert(
                Particle(W // 2 + ax * v, H // 2 + ay * v, ax * v * 0.1, ay * v * 0.1)
            )

        self.cam_punch = 5
        self.rotation_speed = -sgnz(self.rotation_speed) * (
            0.005 + randf() * self.difficulty * 0.05
        )

    def update(self):
        self.update_functions[self.state]()

    def update_menu(self):
        if self.palette_cycle_timer < 5:
            self.palette_cycle_timer += 1
        else:
            self.palette_cycle_timer = 0
            self.palette_cycle = (self.palette_cycle + 1) % MENU_COLOUR_CYCLE_LEN
            for i, colour in enumerate(MENU_COLOUR_CYCLE_BASE):
                pyxel.pal(
                    colour,
                    MENU_COLOUR_CYCLE[(self.palette_cycle + i) % MENU_COLOUR_CYCLE_LEN],
                )

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.state = self.GAME
            self.reset()

    def update_game(self):
        self.difficulty = self.difficulty_timer / self.difficulty_duration
        if self.spawn_timer <= 0:
            self.spawn_timer = lerpi(
                self.start_spawn_interval, self.end_spawn_interval, self.difficulty
            )
            self.spawn_shape()
        else:
            self.spawn_timer -= 1

        if self.difficulty_timer < self.difficulty_duration:
            self.difficulty_timer += 1

        if self.cam_punch > 0:
            self.cam_x = -self.cam_punch + randf() * self.cam_punch * 2
            self.cam_y = -self.cam_punch + randf() * self.cam_punch * 2
            self.cam_punch -= 1
        else:
            self.cam_punch = 0
            self.cam_x = 0
            self.cam_y = 0

        score_diff = self.score - self.display_score
        self.display_score += math.ceil(score_diff / 8)

        player_seg = int(self.segments * self.player_ang / TWO_PI)
        scored = False
        died = False
        for i, shape in self.shapes.each():
            if shape.depth <= shape.thickness:
                self.shapes.kill(i)
                scored = True
            elif shape.depth <= shape.thickness * 2:
                if player_seg == shape.segment:
                    died = True
                shape.colour = 1
            shape.depth -= self.speed
        if died:
            pyxel.stop()
            pyxel.play(3, 1)
            if self.highscores.check_highscores(self.score):
                self.has_set_high_score = True
            self.state = self.DEAD
            self.reset()
            return
        elif scored:
            self.increment_score()
            pyxel.play(3, 0)

        self.rotation += self.rotation_speed
        if self.rotation > TWO_PI:
            self.rotation -= TWO_PI

        self.player_ang = wrap_ang(
            self.player_ang + (btni(pyxel.KEY_RIGHT) - btni(pyxel.KEY_LEFT)) * 0.1
        )

        for i, sp in self.score_particles.each():
            sp.update()
            if sp.age >= sp.life:
                self.score_particles.kill(i)

        for i, p in self.particles.each():
            p.update()
            if p.age >= p.life:
                self.particles.kill(i)

    def update_dead(self):
        go_to_menu = False

        if self.has_set_high_score:
            if self.highscores.ready_to_save:
                self.highscores.save_new(self.highscores.highscore_name, self.score)
                go_to_menu = True
            else:
                if pyxel.btnp(pyxel.KEY_UP):
                    self.highscores.alphabet_direction = 1
                elif pyxel.btnp(pyxel.KEY_DOWN):
                    self.highscores.alphabet_direction = -1
                elif pyxel.btnp(pyxel.KEY_RIGHT):
                    self.highscores.move_to_next = True
                self.highscores.update()
        elif pyxel.btnp(pyxel.KEY_SPACE):
            go_to_menu = True

        if go_to_menu:
            self.state = self.MENU
            self.reset()
            self.reset_score()
            pyxel.playm(0, loop=True)

    def draw_shape(self, shape, arc, angle):
        a = arc * shape.segment + angle
        b = arc * (shape.segment + 1) + angle

        ax = math.cos(a)
        ay = math.sin(a)
        bx = math.cos(b)
        by = math.sin(b)

        p0x = W // 2 + ax * shape.depth
        p1x = W // 2 + ax * (shape.depth + shape.thickness)
        p2x = W // 2 + bx * (shape.depth + shape.thickness)
        p3x = W // 2 + bx * shape.depth

        p0y = W // 2 + ay * shape.depth
        p1y = W // 2 + ay * (shape.depth + shape.thickness)
        p2y = W // 2 + by * (shape.depth + shape.thickness)
        p3y = W // 2 + by * shape.depth

        lines = [
            (p0x, p0y, p1x, p1y),
            (p1x, p1y, p2x, p2y),
            (p2x, p2y, p3x, p3y),
            (p3x, p3y, p0x, p0y),
        ]

        for x0, y0, x1, y1 in lines:
            pyxel.line(
                x0 - self.cam_x,
                y0 - self.cam_y,
                x1 - self.cam_x,
                y1 - self.cam_y,
                shape.colour,
            )

    def draw(self):
        pyxel.cls(0)
        self.draw_functions[self.state]()

    def draw_menu(self):
        pyxel.bltm(0, 0, 0, 0, 0, 32, 16)
        pyxel.text((W - MENU_TEXT_LEN * 4) // 2, H - 24, MENU_TEXT, 6)

        self.draw_scoreboard()

    def draw_game(self):
        arc = TWO_PI / self.segments

        player_seg = int(self.segments * self.player_ang / TWO_PI)
        for seg in range(0, self.segments):
            if player_seg == seg or ((player_seg + 1) % self.segments) == seg:
                col = 2
            else:
                col = 1
            x = W // 2 - self.cam_x
            y = H // 2 - self.cam_y
            end_x = W // 2 + math.cos(self.rotation + arc * seg) * 256 - self.cam_x
            end_y = H // 2 + math.sin(self.rotation + arc * seg) * 256 - self.cam_y
            dx = end_x - x
            dy = end_y - y

            steps = int(abs(dx) if abs(dx) > abs(dy) else abs(dy))
            xup = dx / steps
            yup = dy / steps
            for k in range(0, steps):
                if k % 4 == self.segment_line_cycle:
                    pyxel.pix(x, y, col)
                x += xup
                y += yup

        if self.segment_line_cycle_timer < 3:
            self.segment_line_cycle_timer += 1
        else:
            self.segment_line_cycle_timer = 0
            self.segment_line_cycle = (self.segment_line_cycle + 1) % 4

        for _, shape in self.shapes.each():
            self.draw_shape(shape, arc, self.rotation)

        for _, p in self.particles.each():
            p.draw(self.cam_x, self.cam_y)

        vx = math.cos(self.player_ang + self.rotation)
        vy = math.sin(self.player_ang + self.rotation)
        top_x = W // 2 + vx * 14 - self.cam_x
        top_y = H // 2 + vy * 14 - self.cam_y
        left_x = W // 2 + vx * 8 + vy * 2 - self.cam_x
        left_y = H // 2 + vy * 8 - vx * 2 - self.cam_y
        right_x = W // 2 + vx * 8 - vy * 2 - self.cam_x
        right_y = H // 2 + vy * 8 + vx * 2 - self.cam_y
        pyxel.line(left_x, left_y, top_x, top_y, 8)
        pyxel.line(right_x, right_y, top_x, top_y, 8)
        pyxel.line(left_x, left_y, right_x, right_y, 8)
        pyxel.circ(W // 2 - self.cam_x, H // 2 - self.cam_y, 2, 7)

        for _, sp in self.score_particles.each():
            sp.draw(self.cam_x, self.cam_y)

        pyxel.text(5, 5, f"{self.display_score:010} pts", 7)
        pyxel.text(145, 5, f"HIGH SCORE: {self.high_score:010} pts", 7)

    def draw_dead(self):
        lines = ["better luck next time", "", f"score: {self.score}"]
        for i, line in enumerate(lines):
            if line:
                pyxel.text((W - len(line) * 4) // 2, 24 + i * 8, line, 8)

        if self.has_set_high_score:
            pyxel.text(W // 2 - 28, H // 2 - 64, "new high score!", 7)
            pyxel.text(W // 2 - 20, H // 2 - 48, "ENTER NAME", 7)
            pyxel.text(W // 2 - 20, H // 2 - 32, self.highscores.highscore_name, 8)
        else:
            pyxel.text(W // 2 - 56, H // 2 - 24, "push space to return to menu", 7)

        self.draw_scoreboard()

    def draw_scoreboard(self):
        pyxel.text(W // 2 - 24, H // 2, "HIGH SCORES", 7)
        for i, score in enumerate(self.highscores.ordered_score_list()):
            pyxel.text(
                W // 2 - 28,
                H // 2 + 8 + i * 8,
                f"{score['name']} ... {score['score']}",
                7,
            )


if __name__ == "__main__":
    Game().run(enable_profiling="--profile" in sys.argv)
