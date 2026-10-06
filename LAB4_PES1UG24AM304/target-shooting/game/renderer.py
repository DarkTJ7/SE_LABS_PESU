"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (25, 25, 35)
COLOR_TEXT = (255, 255, 255)


def draw_scene(surface, targets):
    surface.fill(COLOR_BG)
    for target in targets:
        pygame.draw.circle(surface, target.color, (int(target.x), int(target.y)), target.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(target.x), int(target.y)), target.radius, 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(target.x), int(target.y)), 5)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)


def draw_hud(surface, font, engine):
    pygame.draw.rect(surface, (17, 18, 29), (0, 0, WIDTH, 48))
    draw_text(surface, font, f"SCORE {engine.score}", (16, 13), (255, 220, 100))
    draw_text(surface, font, f"COMBO x{max(1, engine.combo)}", (220, 13))
    draw_text(surface, font, f"HITS {engine.hits}  MISSES {engine.misses}", (390, 13))
    remaining = max(0, int(engine.time_left + 0.999))
    color = (255, 110, 100) if remaining <= 10 else (255, 255, 255)
    draw_text(surface, font, f"{remaining:02d}s", (WIDTH - 64, 13), color)


def draw_game_over(surface, font, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 20, 205))
    surface.blit(overlay, (0, 0))
    title = pygame.font.SysFont("consolas", 42, bold=True)
    heading = title.render("ROUND OVER", True, (255, 220, 80))
    surface.blit(heading, heading.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 34)))
    result = font.render(f"FINAL SCORE  {score}", True, COLOR_TEXT)
    surface.blit(result, result.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 12)))
    msg = font.render("Press R to play again", True, (190, 205, 225))
    surface.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 46)))
