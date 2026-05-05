# config.py - Shared constants for the stone collision simulation

# Display settings
WIDTH = 900
HEIGHT = 800
TITLE = "마찰이 있는 바둑돌 완전탄성충돌 시뮬레이션"

# Board settings
BOARD_SIZE = 19
MARGIN = 70
GRID_SIZE = 36
STONE_RADIUS = 16
BOARD_LEFT = MARGIN
BOARD_TOP = MARGIN
BOARD_RIGHT = MARGIN + GRID_SIZE * (BOARD_SIZE - 1)
BOARD_BOTTOM = MARGIN + GRID_SIZE * (BOARD_SIZE - 1)

# Colors
BOARD_COLOR = (205, 170, 100)
LINE_COLOR = (40, 25, 10)
BLACK = (10, 10, 10)
WHITE = (245, 245, 245)
GRAY = (120, 120, 120)
BLUE = (40, 80, 220)

# Physics settings
MASS = 1.0
SPEED = 420.0
DT = 1 / 60.0
SUB_STEPS = 8
FRICTION_ACCEL = 80.0  # px/s^2

# UI settings
FONT_NAME = "malgungothic"
FONT_SIZE = 24
AIM_LINE_LENGTH = 120