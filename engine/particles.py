from random import randint as rand

import pyxel


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
