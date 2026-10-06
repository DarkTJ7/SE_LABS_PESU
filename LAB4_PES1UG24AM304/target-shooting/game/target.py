"""
Target: a circular target the player clicks on. (x, y) is the CENTER
of the circle - this matters for how it's drawn vs. how it's hit-tested.
"""

import pygame


class Target:
    def __init__(self, x, y, radius=28, color=(230, 90, 70), vx=0, vy=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = vx
        self.vy = vy

    def update(self, dt, width, height, top=0):
        """Move and bounce the circle while keeping it fully on screen."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < self.radius:
            self.x, self.vx = self.radius, abs(self.vx)
        elif self.x > width - self.radius:
            self.x, self.vx = width - self.radius, -abs(self.vx)
        if self.y < top + self.radius:
            self.y, self.vy = top + self.radius, abs(self.vy)
        elif self.y > height - self.radius:
            self.y, self.vy = height - self.radius, -abs(self.vy)

    def get_bounding_rect(self):
        """Return the circle's enclosing rectangle (x/y are its center)."""
        return pygame.Rect(round(self.x - self.radius), round(self.y - self.radius),
                           self.radius * 2, self.radius * 2)
