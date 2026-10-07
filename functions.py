import pygame
import random
import math
from constants import *

def make_player(size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    pygame.draw.rect(surface, PLAYER_COLOR, (0, 8, w, h - 8))
    pygame.draw.rect(surface, PLAYER_COLOR, (w // 2 - 4, 0, 8, 10))
    return surface


def make_enemy(size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    pygame.draw.rect(surface, color, (0, 0, w, h))
    pygame.draw.rect(surface, BG_COLOR, (9, 8, 6, 6))
    pygame.draw.rect(surface, BG_COLOR, (w - 15, 8, 6, 6))
    return surface


def make_block(size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


# key: (png file inside assets/, size in pixels, function that draws the placeholder)
SPRITE_SPECS = {
    "player": ("player.png", (PLAYER_W, PLAYER_H), make_player),
    "enemy_0": ("enemy_0.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (230, 90, 230))),
    "enemy_1": ("enemy_1.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (90, 200, 230))),
    "enemy_2": ("enemy_2.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (110, 230, 110))),
    "enemy_00": ("enemy_00.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (230, 90, 230))),
    "enemy_11": ("enemy_11.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (90, 200, 230))),
    "enemy_22": ("enemy_22.png", (ENEMY_W, ENEMY_H), lambda s: make_enemy(s, (110, 230, 110))),
    "player_bullet": ("player_bullet.png", (BULLET_W, BULLET_H), lambda s: make_block(s, PLAYER_BULLET_COLOR)),
    "enemy_bullet": ("enemy_bullet.png", (BULLET_W, BULLET_H), lambda s: make_block(s, ENEMY_BULLET_COLOR)),
    "shield_block": ("shield_block.png", (SHIELD_BLOCK, SHIELD_BLOCK), lambda s: make_block(s, SHIELD_COLOR)),
    "bg": ("background.png", (WIDTH, HEIGHT), None),
}


def load_image(filename, size, fallback):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.isfile(path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)
        except pygame.error:
            pass
    return fallback(size)


def load_sprites():
    return {key: load_image(f, size, fb) for key, (f, size, fb) in SPRITE_SPECS.items()}

def spawn_explosion(particles, pos):
    for _ in range(random.randint(*EXPLOSION_PARTICLES)):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*PARTICLE_SPEED)
        life = random.uniform(*PARTICLE_LIFE)
        particles.append({
            "x": float(pos[0]),
            "y": float(pos[1]),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "size": random.uniform(*PARTICLE_SIZE),
            "life": life,
            "max_life": life,
            "color": random.choice(EXPLOSION_COLORS),
        })

def update_particles(particles, dt):
    for p in particles:
        p["life"] -= dt
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        drag = max(0.0, 1 - PARTICLE_DRAG * dt)
        p["vx"] *= drag
        p["vy"] *= drag
    particles[:] = [p for p in particles if p["life"] > 0]


def draw_particles(surface, particles):
    for p in particles:
        size = max(1, round(p["size"] * p["life"] / p["max_life"]))
        pygame.draw.rect(surface, p["color"], (round(p["x"] - size / 2), round(p["y"] - size / 2), size, size))


def build_shields():
    blocks = []
    pattern_w = len(SHIELD_PATTERN[0]) * SHIELD_BLOCK
    for i in range(SHIELD_COUNT):
        center_x = WIDTH * (2 * i + 1) / (2 * SHIELD_COUNT)
        left = round(center_x - pattern_w / 2)
        for row, line in enumerate(SHIELD_PATTERN):
            for col, char in enumerate(line):
                if char == "#":
                    blocks.append(
                        pygame.Rect(left + col * SHIELD_BLOCK, SHIELD_Y + row * SHIELD_BLOCK, SHIELD_BLOCK, SHIELD_BLOCK)
                    )
    return blocks


def draw_centered(surface, font, text, y):
    if text.startswith("GAME OV"):
        color_txt = GAMEOVER_COLOR
    elif text.endswith("SUPERADO"):
        color_txt = NIVELSUPERADO_COLOR
    else:
        color_txt = TEXT_COLOR
    
    img = font.render(text, True, color_txt)
    surface.blit(img, img.get_rect(center=(WIDTH // 2, y)))




