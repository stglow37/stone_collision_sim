import math
from typing import Tuple
import config
import model


def dot(ax, ay, bx, by):
    return ax * bx + ay * by


def length(x, y):
    return math.hypot(x, y)


def apply_friction(stone: model.Stone, dt: float):
    vx = stone.vx
    vy = stone.vy
    v = length(vx, vy)

    if v == 0:
        return

    dv = config.FRICTION_ACCEL * dt

    if dv >= v:
        stone.vx = 0.0
        stone.vy = 0.0
    else:
        ux = vx / v
        uy = vy / v
        stone.vx -= dv * ux
        stone.vy -= dv * uy


def handle_collision(a: model.Stone, b: model.Stone):
    dx = b.x - a.x
    dy = b.y - a.y
    dist = length(dx, dy)

    min_dist = 2 * config.STONE_RADIUS

    if dist == 0 or dist > min_dist:
        return

    nx = dx / dist
    ny = dy / dist

    rvx = a.vx - b.vx
    rvy = a.vy - b.vy

    approaching_speed = dot(rvx, rvy, nx, ny)

    if approaching_speed > 0:
        a.vx -= approaching_speed * nx
        a.vy -= approaching_speed * ny
        b.vx += approaching_speed * nx
        b.vy += approaching_speed * ny

    overlap = min_dist - dist
    a.x -= nx * overlap / 2
    a.y -= ny * overlap / 2
    b.x += nx * overlap / 2
    b.y += ny * overlap / 2


def update_physics(state: model.GameState):
    small_dt = config.DT / config.SUB_STEPS

    for _ in range(config.SUB_STEPS):
        for stone in state.stones:
            apply_friction(stone, small_dt)

        for stone in state.stones:
            stone.x += stone.vx * small_dt
            stone.y += stone.vy * small_dt

        for i in range(len(state.stones)):
            for j in range(i + 1, len(state.stones)):
                handle_collision(state.stones[i], state.stones[j])


def total_energy(state: model.GameState) -> float:
    e = 0.0
    for stone in state.stones:
        v2 = stone.vx ** 2 + stone.vy ** 2
        e += 0.5 * config.MASS * v2
    return e


def total_momentum(state: model.GameState) -> Tuple[float, float]:
    px = sum(config.MASS * stone.vx for stone in state.stones)
    py = sum(config.MASS * stone.vy for stone in state.stones)
    return px, py
