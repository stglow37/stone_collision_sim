import math
from enum import Enum
from typing import Optional
import pygame

import config
import graphics
import model
import physics


class Action(Enum):
    QUIT = "quit"
    PLACE_STONE = "place_stone"
    RESET = "reset"
    ADJUST_ANGLE_UP = "adjust_angle_up"
    ADJUST_ANGLE_DOWN = "adjust_angle_down"
    SHOOT = "shoot"


def interpret_event(event: pygame.event.EventType, state: model.GameState) -> Optional[Action]:
    if event.type == pygame.QUIT:
        return Action.QUIT

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and not state.fired and len(state.stones) < 3:
            return Action.PLACE_STONE

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            return Action.RESET

        if len(state.stones) == 3 and not state.fired:
            if event.key == pygame.K_UP:
                return Action.ADJUST_ANGLE_UP
            elif event.key == pygame.K_DOWN:
                return Action.ADJUST_ANGLE_DOWN
            elif event.key == pygame.K_SPACE:
                return Action.SHOOT

    return None


def handle_action(action: Action, state: model.GameState, event: Optional[pygame.event.EventType] = None):
    if action == Action.QUIT:
        state.running = False

    elif action == Action.PLACE_STONE and event:
        result = graphics.snap_to_grid(event.pos[0], event.pos[1])
        if result is not None:
            x, y = result
            color = config.BLACK if len(state.stones) == 0 else config.WHITE
            graphics.add_stone(state.stones, x, y, color)

    elif action == Action.RESET:
        reset(state)

    elif action == Action.ADJUST_ANGLE_UP:
        state.angle_deg -= 1.0

    elif action == Action.ADJUST_ANGLE_DOWN:
        state.angle_deg += 1.0

    elif action == Action.SHOOT:
        rad = math.radians(state.angle_deg)
        state.stones[0].vx = config.SPEED * math.cos(rad)
        state.stones[0].vy = config.SPEED * math.sin(rad)
        state.fired = True


def reset(state: model.GameState):
    state.stones.clear()
    state.fired = False
    state.angle_deg = -30.0


def handle_events(state: model.GameState):
    for event in pygame.event.get():
        action = interpret_event(event, state)
        if action:
            handle_action(action, state, event)


def update(state: model.GameState):
    if state.fired:
        physics.update_physics(state)


def render(screen, font, state: model.GameState):
    momentum = None
    energy = None
    if state.fired and len(state.stones) == 3:
        momentum = physics.total_momentum(state)
        energy = physics.total_energy(state)

    graphics.render(screen, font, state, momentum, energy)


def main():
    screen, clock, font = graphics.init_display()
    state = model.GameState()

    try:
        while state.running:
            handle_events(state)
            update(state)
            render(screen, font, state)
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
