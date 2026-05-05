# model.py - Data models for the stone collision simulation

from dataclasses import dataclass, field
from typing import List, Tuple
import config


@dataclass
class Stone:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    color: Tuple[int, int, int] = config.BLACK


@dataclass
class GameState:
    stones: List[Stone] = field(default_factory=list)
    fired: bool = False
    angle_deg: float = -30.0
    running: bool = True