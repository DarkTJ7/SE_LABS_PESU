"""
GameEngine: owns the targets, round timer, score, and click handling.
"""

import random
import math

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import WIDTH, HEIGHT

NUM_TARGETS = 3
TARGET_RADIUS = 28
ROUND_SECONDS = 30.0
HUD_HEIGHT = 48


class GameEngine:
    def __init__(self):
        self.start_round()

    def start_round(self):
        self.targets = [self._random_target() for _ in range(NUM_TARGETS)]
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo = 0
        self.time_left = ROUND_SECONDS
        self.game_over = False

    def _random_target(self):
        x = random.randint(TARGET_RADIUS + 10, WIDTH - TARGET_RADIUS - 10)
        y = random.randint(HUD_HEIGHT + TARGET_RADIUS + 10, HEIGHT - TARGET_RADIUS - 10)
        speed = random.choice((105, 165, 225))
        angle = random.uniform(0, 6.283185307)
        return Target(x, y, radius=TARGET_RADIUS,
                      color=random.choice(((255, 105, 92), (72, 190, 255), (255, 190, 76))),
                      vx=speed * math.cos(angle),
                      vy=speed * math.sin(angle))

    def handle_click(self, pos):
        if self.game_over:
            return
        target = check_hit(self.targets, pos)
        if target is not None:
            self.hits += 1
            self.combo += 1
            self.score += 10 * self.combo
            self.targets.remove(target)
            self.targets.append(self._random_target())
        else:
            self.misses += 1
            self.combo = 0

    def update(self, dt=1 / 60):
        if self.game_over:
            return
        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left == 0:
            self.game_over = True
            return
        for target in self.targets:
            target.update(dt, WIDTH, HEIGHT, top=HUD_HEIGHT)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.targets)
        renderer.draw_hud(surface, font, self)
        if self.game_over:
            renderer.draw_game_over(surface, font, self.score)
