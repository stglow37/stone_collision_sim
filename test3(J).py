import pygame
import math

pygame.init()

# ---------------- 화면 설정 ----------------
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("마찰이 있는 바둑돌 완전탄성충돌 시뮬레이션")

clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)

# ---------------- 색상 ----------------
BOARD_COLOR = (205, 170, 100)
LINE_COLOR = (40, 25, 10)
BLACK = (10, 10, 10)
WHITE = (245, 245, 245)
GRAY = (120, 120, 120)
BLUE = (40, 80, 220)

# ---------------- 바둑판 설정 ----------------
BOARD_SIZE = 19
MARGIN = 70
GRID_SIZE = 36
STONE_RADIUS = 16

BOARD_LEFT = MARGIN
BOARD_TOP = MARGIN
BOARD_RIGHT = MARGIN + GRID_SIZE * (BOARD_SIZE - 1)
BOARD_BOTTOM = MARGIN + GRID_SIZE * (BOARD_SIZE - 1)

# ---------------- 물리 설정 ----------------
MASS = 1.0
SPEED = 420.0          # 검은돌 초기 속력
DT = 1 / 60.0
SUB_STEPS = 8          # 충돌 누락 방지를 줄이기 위한 세부 시간 분할

# 마찰 설정
# 실제 단위라기보다는 화면 시뮬레이션 단위에서의 일정한 감속도라고 보면 됨
FRICTION_ACCEL = 80.0  # px/s^2

angle_deg = -30.0
fired = False

# stones = [{"x":..., "y":..., "vx":..., "vy":..., "color":...}, ...]
stones = []


# ---------------- 벡터 함수 ----------------
def dot(ax, ay, bx, by):
    return ax * bx + ay * by


def length(x, y):
    return math.sqrt(x * x + y * y)


# ---------------- 바둑판 그리기 ----------------
def draw_board():
    screen.fill(BOARD_COLOR)

    for i in range(BOARD_SIZE):
        x = BOARD_LEFT + i * GRID_SIZE
        y = BOARD_TOP + i * GRID_SIZE

        pygame.draw.line(screen, LINE_COLOR, (x, BOARD_TOP), (x, BOARD_BOTTOM), 2)
        pygame.draw.line(screen, LINE_COLOR, (BOARD_LEFT, y), (BOARD_RIGHT, y), 2)

    # 화점
    star_points = [
        (3, 3), (9, 3), (15, 3),
        (3, 9), (9, 9), (15, 9),
        (3, 15), (9, 15), (15, 15)
    ]

    for gx, gy in star_points:
        x = BOARD_LEFT + gx * GRID_SIZE
        y = BOARD_TOP + gy * GRID_SIZE
        pygame.draw.circle(screen, LINE_COLOR, (x, y), 5)


# ---------------- 클릭 위치를 격자점에 맞춤 ----------------
def snap_to_grid(mx, my):
    gx = round((mx - BOARD_LEFT) / GRID_SIZE)
    gy = round((my - BOARD_TOP) / GRID_SIZE)

    if gx < 0 or gx >= BOARD_SIZE:
        return None
    if gy < 0 or gy >= BOARD_SIZE:
        return None

    x = BOARD_LEFT + gx * GRID_SIZE
    y = BOARD_TOP + gy * GRID_SIZE

    return x, y


# ---------------- 돌 추가 ----------------
def add_stone(x, y, color):
    stones.append({
        "x": float(x),
        "y": float(y),
        "vx": 0.0,
        "vy": 0.0,
        "color": color
    })


# ---------------- 돌 그리기 ----------------
def draw_stones():
    for s in stones:
        pygame.draw.circle(
            screen,
            s["color"],
            (int(s["x"]), int(s["y"])),
            STONE_RADIUS
        )

        if s["color"] == WHITE:
            pygame.draw.circle(
                screen,
                GRAY,
                (int(s["x"]), int(s["y"])),
                STONE_RADIUS,
                2
            )


# ---------------- 조준선 그리기 ----------------
def draw_aim_line():
    if len(stones) >= 1 and not fired:
        black_stone = stones[0]

        rad = math.radians(angle_deg)
        start = (black_stone["x"], black_stone["y"])
        end = (
            black_stone["x"] + math.cos(rad) * 120,
            black_stone["y"] + math.sin(rad) * 120
        )

        pygame.draw.line(screen, BLUE, start, end, 3)


# ---------------- 모든 돌에 동일한 마찰력 적용 ----------------
def apply_friction(s, dt):
    vx = s["vx"]
    vy = s["vy"]
    v = length(vx, vy)

    if v == 0:
        return

    # 이번 시간 간격 동안 마찰 때문에 줄어드는 속력
    dv = FRICTION_ACCEL * dt

    # 마찰 때문에 속도가 0을 지나쳐 방향이 바뀌면 안 됨
    if dv >= v:
        s["vx"] = 0.0
        s["vy"] = 0.0
    else:
        # 속도 방향의 단위벡터
        ux = vx / v
        uy = vy / v

        # 속도의 반대 방향으로 감속
        s["vx"] -= dv * ux
        s["vy"] -= dv * uy


# ---------------- 완전탄성충돌 처리 ----------------
def handle_collision(a, b):
    dx = b["x"] - a["x"]
    dy = b["y"] - a["y"]
    dist = length(dx, dy)

    min_dist = 2 * STONE_RADIUS

    if dist == 0:
        return

    if dist > min_dist:
        return

    # 두 돌 중심을 잇는 단위 법선벡터
    nx = dx / dist
    ny = dy / dist

    # 상대속도
    rvx = a["vx"] - b["vx"]
    rvy = a["vy"] - b["vy"]

    # 법선 방향 상대속도
    approaching_speed = dot(rvx, rvy, nx, ny)

    # approaching_speed > 0이면 서로 가까워지는 중
    if approaching_speed > 0:
        # 같은 질량, 완전탄성충돌
        # 법선 방향 속도 성분만 교환됨
        a["vx"] -= approaching_speed * nx
        a["vy"] -= approaching_speed * ny

        b["vx"] += approaching_speed * nx
        b["vy"] += approaching_speed * ny

    # 겹침 보정
    overlap = min_dist - dist
    a["x"] -= nx * overlap / 2
    a["y"] -= ny * overlap / 2
    b["x"] += nx * overlap / 2
    b["y"] += ny * overlap / 2


# ---------------- 물리 업데이트 ----------------
def update_physics(dt):
    small_dt = dt / SUB_STEPS

    for _ in range(SUB_STEPS):
        # 1. 마찰 적용
        for s in stones:
            apply_friction(s, small_dt)

        # 2. 위치 업데이트
        for s in stones:
            s["x"] += s["vx"] * small_dt
            s["y"] += s["vy"] * small_dt

        # 3. 충돌 검사
        for i in range(len(stones)):
            for j in range(i + 1, len(stones)):
                handle_collision(stones[i], stones[j])


# ---------------- 물리량 계산 ----------------
def total_energy():
    e = 0.0
    for s in stones:
        v2 = s["vx"] ** 2 + s["vy"] ** 2
        e += 0.5 * MASS * v2
    return e


def total_momentum():
    px = 0.0
    py = 0.0
    for s in stones:
        px += MASS * s["vx"]
        py += MASS * s["vy"]
    return px, py


# ---------------- 글자 표시 ----------------
def draw_text():
    if len(stones) == 0:
        msg = "첫 번째 클릭: 검은돌 위치 선택"
    elif len(stones) == 1:
        msg = "두 번째 클릭: 첫 번째 흰돌 위치 선택"
    elif len(stones) == 2:
        msg = "세 번째 클릭: 두 번째 흰돌 위치 선택"
    else:
        msg = "↑↓: 각도 조절 | Space: 발사 | R: 초기화"

    text1 = font.render(msg, True, (0, 0, 0))
    screen.blit(text1, (30, 20))

    text2 = font.render(f"발사 각도: {angle_deg:.1f}도", True, (0, 0, 0))
    screen.blit(text2, (30, 735))

    text5 = font.render(f"마찰 감속도: {FRICTION_ACCEL:.1f} px/s²", True, (0, 0, 0))
    screen.blit(text5, (30, 765))

    if fired and len(stones) == 3:
        px, py = total_momentum()
        e = total_energy()

        text3 = font.render(f"총 운동량: ({px:.2f}, {py:.2f})", True, (0, 0, 0))
        text4 = font.render(f"총 운동에너지: {e:.2f}", True, (0, 0, 0))

        screen.blit(text3, (330, 735))
        screen.blit(text4, (610, 735))


# ---------------- 초기화 ----------------
def reset():
    global fired, angle_deg
    stones.clear()
    fired = False
    angle_deg = -30.0


# ---------------- 메인 루프 ----------------
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 마우스 클릭으로 돌 배치
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not fired and len(stones) < 3:
                result = snap_to_grid(event.pos[0], event.pos[1])

                if result is not None:
                    x, y = result

                    if len(stones) == 0:
                        add_stone(x, y, BLACK)
                    else:
                        add_stone(x, y, WHITE)

        # 키보드 조작
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset()

            if len(stones) == 3 and not fired:
                if event.key == pygame.K_UP:
                    angle_deg -= 1.0

                elif event.key == pygame.K_DOWN:
                    angle_deg += 1.0

                elif event.key == pygame.K_SPACE:
                    rad = math.radians(angle_deg)

                    stones[0]["vx"] = SPEED * math.cos(rad)
                    stones[0]["vy"] = SPEED * math.sin(rad)

                    fired = True

    if fired:
        update_physics(DT)

    draw_board()
    draw_aim_line()
    draw_stones()
    draw_text()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()