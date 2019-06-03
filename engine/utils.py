import math

import pyxel


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
    if a > math.tau:
        a -= math.tau
    if a < 0:
        a += math.tau
    return a
