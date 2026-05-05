import pygame
import math
import config
import model


def init_display():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE)
    return screen, clock, font


def draw_board(screen):
    screen.fill(config.BOARD_COLOR)

    for i in range(config.BOARD_SIZE):
        x = config.BOARD_LEFT + i * config.GRID_SIZE
        y = config.BOARD_TOP + i * config.GRID_SIZE

        pygame.draw.line(screen, config.LINE_COLOR, (x, config.BOARD_TOP), (x, config.BOARD_BOTTOM), 2)
        pygame.draw.line(screen, config.LINE_COLOR, (config.BOARD_LEFT, y), (config.BOARD_RIGHT, y), 2)

    star_points = [
        (3, 3), (9, 3), (15, 3),
        (3, 9), (9, 9), (15, 9),
        (3, 15), (9, 15), (15, 15)
    ]

    for gx, gy in star_points:
        x = config.BOARD_LEFT + gx * config.GRID_SIZE
        y = config.BOARD_TOP + gy * config.GRID_SIZE
        pygame.draw.circle(screen, config.LINE_COLOR, (x, y), 5)


def snap_to_grid(mx, my):
    gx = round((mx - config.BOARD_LEFT) / config.GRID_SIZE)
    gy = round((my - config.BOARD_TOP) / config.GRID_SIZE)

    if gx < 0 or gx >= config.BOARD_SIZE:
        return None
    if gy < 0 or gy >= config.BOARD_SIZE:
        return None

    x = config.BOARD_LEFT + gx * config.GRID_SIZE
    y = config.BOARD_TOP + gy * config.GRID_SIZE

    return x, y


def add_stone(stones: list[model.Stone], x: float, y: float, color: tuple[int, int, int]):
    stones.append(model.Stone(x=x, y=y, color=color))


def draw_stones(screen, stones: list[model.Stone]):
    for stone in stones:
        pygame.draw.circle(screen, stone.color, (int(stone.x), int(stone.y)), config.STONE_RADIUS)

        if stone.color == config.WHITE:
            pygame.draw.circle(screen, config.GRAY, (int(stone.x), int(stone.y)), config.STONE_RADIUS, 2)


def draw_aim_line(screen, state: model.GameState):
    if len(state.stones) >= 1 and not state.fired:
        black_stone = state.stones[0]
        rad = math.radians(state.angle_deg)
        start = (black_stone.x, black_stone.y)
        end = (
            black_stone.x + math.cos(rad) * config.AIM_LINE_LENGTH,
            black_stone.y + math.sin(rad) * config.AIM_LINE_LENGTH
        )
        pygame.draw.line(screen, config.BLUE, start, end, 3)


def draw_text(screen, font, state: model.GameState, momentum=None, energy=None):
    if len(state.stones) == 0:
        msg = "첫 번째 클릭: 검은돌 위치 선택"
    elif len(state.stones) == 1:
        msg = "두 번째 클릭: 첫 번째 흰돌 위치 선택"
    elif len(state.stones) == 2:
        msg = "세 번째 클릭: 두 번째 흰돌 위치 선택"
    else:
        msg = "↑↓: 각도 조절 | Space: 발사 | R: 초기화"

    text1 = font.render(msg, True, (0, 0, 0))
    screen.blit(text1, (30, 20))

    text2 = font.render(f"발사 각도: {state.angle_deg:.1f}도", True, (0, 0, 0))
    screen.blit(text2, (30, 735))

    text5 = font.render(f"마찰 감속도: {config.FRICTION_ACCEL:.1f} px/s²", True, (0, 0, 0))
    screen.blit(text5, (30, 765))

    if state.fired and len(state.stones) == 3 and momentum is not None and energy is not None:
        px, py = momentum
        text3 = font.render(f"총 운동량: ({px:.2f}, {py:.2f})", True, (0, 0, 0))
        text4 = font.render(f"총 운동에너지: {energy:.2f}", True, (0, 0, 0))

        screen.blit(text3, (330, 735))
        screen.blit(text4, (610, 735))


def render(screen, font, state: model.GameState, momentum=None, energy=None):
    draw_board(screen)
    draw_aim_line(screen, state)
    draw_stones(screen, state.stones)
    draw_text(screen, font, state, momentum, energy)
