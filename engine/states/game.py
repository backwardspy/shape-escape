from random import randint as rand, random as randf
import math

import pyxel

from engine import state
from engine.object_pool import ObjectPool
from engine.shape import Shape
from engine.particles import Particle, TextParticle
from engine.constants import W, H, STATE_DEAD
from engine.utils import sgnz, lerpi, wrap_ang, btni


MUSIC_GAME = 0


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        pyxel.pal()
        pyxel.playm(MUSIC_GAME, loop=True)

        try:
            state.high_score = state.scoreboard.ordered_score_list()[0]["score"]
        except TypeError:
            state.high_score = 0
        state.has_set_high_score = False
        state.score = 0
        self.display_score = 0

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

        self.cam_punch = 0

        self.segment_line_cycle = 0
        self.segment_line_cycle_timer = 0

    def update(self):
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
            state.cam_x = -self.cam_punch + randf() * self.cam_punch * 2
            state.cam_y = -self.cam_punch + randf() * self.cam_punch * 2
            self.cam_punch -= 1
        else:
            state.cam_x = 0
            state.cam_y = 0
            self.cam_punch = 0

        score_diff = state.score - self.display_score
        self.display_score += math.ceil(score_diff / 8)

        player_seg = int(self.segments * self.player_ang / math.tau)
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
            if state.scoreboard.check_highscores(state.score):
                self.has_set_high_score = True
            state.game.set_state(STATE_DEAD)
            return
        elif scored:
            self.increment_score()
            pyxel.play(3, 0)

        self.rotation += self.rotation_speed
        if self.rotation > math.tau:
            self.rotation -= math.tau

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

    def draw(self):
        pyxel.cls(0)

        arc = math.tau / self.segments

        player_seg = int(self.segments * self.player_ang / math.tau)
        for seg in range(0, self.segments):
            if player_seg == seg or ((player_seg + 1) % self.segments) == seg:
                col = 2
            else:
                col = 1
            x = W // 2 - state.cam_x
            y = H // 2 - state.cam_y
            end_x = W // 2 + math.cos(self.rotation + arc * seg) * 256 - state.cam_x
            end_y = H // 2 + math.sin(self.rotation + arc * seg) * 256 - state.cam_y
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
            shape.draw(arc, self.rotation)

        for _, p in self.particles.each():
            p.draw(state.cam_x, state.cam_y)

        vx = math.cos(self.player_ang + self.rotation)
        vy = math.sin(self.player_ang + self.rotation)
        top_x = W // 2 + vx * 14 - state.cam_x
        top_y = H // 2 + vy * 14 - state.cam_y
        left_x = W // 2 + vx * 8 + vy * 2 - state.cam_x
        left_y = H // 2 + vy * 8 - vx * 2 - state.cam_y
        right_x = W // 2 + vx * 8 - vy * 2 - state.cam_x
        right_y = H // 2 + vy * 8 + vx * 2 - state.cam_y
        pyxel.line(left_x, left_y, top_x, top_y, 8)
        pyxel.line(right_x, right_y, top_x, top_y, 8)
        pyxel.line(left_x, left_y, right_x, right_y, 8)
        pyxel.circ(W // 2 - state.cam_x, H // 2 - state.cam_y, 2, 7)

        for _, sp in self.score_particles.each():
            sp.draw(state.cam_x, state.cam_y)

        pyxel.text(5, 5, f"{self.display_score:010} pts", 7)
        pyxel.text(145, 5, f"HIGH SCORE: {state.high_score:010} pts", 7)

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
        state.score += points
        if state.score > state.high_score:
            state.has_set_high_score = True
            state.high_score = state.score

        self.score_particles.insert(TextParticle(W // 2 + 24, H // 2, f"{points} pts"))

        for _ in range(30):
            ang = randf() * math.tau
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
