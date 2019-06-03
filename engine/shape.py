import math

import pyxel

from engine.constants import W, H
from engine import state


class Shape:
    def __init__(self, segment, depth, thickness, colour):
        self.segment = segment
        self.depth = depth
        self.thickness = thickness
        self.colour = colour

    def draw(self, arc, angle):
        a = arc * self.segment + angle
        b = arc * (self.segment + 1) + angle

        ax = math.cos(a)
        ay = math.sin(a)
        bx = math.cos(b)
        by = math.sin(b)

        p0x = W // 2 + ax * self.depth
        p1x = W // 2 + ax * (self.depth + self.thickness)
        p2x = W // 2 + bx * (self.depth + self.thickness)
        p3x = W // 2 + bx * self.depth

        p0y = H // 2 + ay * self.depth
        p1y = H // 2 + ay * (self.depth + self.thickness)
        p2y = H // 2 + by * (self.depth + self.thickness)
        p3y = H // 2 + by * self.depth

        lines = [
            (p0x, p0y, p1x, p1y),
            (p1x, p1y, p2x, p2y),
            (p2x, p2y, p3x, p3y),
            (p3x, p3y, p0x, p0y),
        ]

        for x0, y0, x1, y1 in lines:
            pyxel.line(
                x0 - state.cam_x,
                y0 - state.cam_y,
                x1 - state.cam_x,
                y1 - state.cam_y,
                self.colour,
            )
