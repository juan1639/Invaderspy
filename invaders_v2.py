import pygame
import os
import random
import math
import sys

WIDTH = 1000
HEIGHT = 700
FPS = 60

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

PLAYER_W = 50
PLAYER_H = 20
PLAYER_Y = HEIGHT - 50
PLAYER_SPEED = 350
PLAYER_BULLET_SPEED = 520
MAX_PLAYER_BULLETS = 3
BULLET_W = 4
BULLET_H = 14

ENEMY_W = 40
ENEMY_H = 28
ENEMY_COLS = 11
ENEMY_ROWS = 5
ENEMY_GAP_X = 16
ENEMY_GAP_Y = 14
FORMATION_START_X = 60
FORMATION_START_Y = 80
FORMATION_MARGIN = 20
ENEMY_BASE_SPEED = 80
ENEMY_SPEED_BONUS = 180
ENEMY_DROP = 24
ENEMY_BULLET_SPEED = 450
ENEMY_SHOT_MIN = [0.6, 0.5, 0.4, 0.3, 0.2, 0.1] #0.6
ENEMY_SHOT_MAX = [0.9, 0.7, 0.5, 0.4, 0.4, 0.2] #1.6
ENEMY_SAFE_GAP = 40
ENEMY_ANIM_DURATION = 0.7

SHIELD_COUNT = 4
SHIELD_BLOCK = 8
SHIELD_Y = PLAYER_Y - 100
SHIELD_HIT_RADIUS = 10
SHIELD_PATTERN = [
    "..#######..",
    ".#########.",
    "###########",
    "###########",
    "###########",
    "###########",
    "####...####",
    "###.....###",
]

START_LIVES = 3
ROW_POINTS = [30, 20, 20, 10, 10]
ROW_SPRITES = ["enemy_0", "enemy_1", "enemy_1", "enemy_2", "enemy_2"]
ROW_SPRITES_2 = ["enemy_00", "enemy_11", "enemy_11", "enemy_22", "enemy_22"]
LEVEL_CLEAR_TIME = 4.8
INVULNERABLE_TIME = 2.8

EXPLOSION_PARTICLES = (18, 28)
PARTICLE_SPEED = (60, 260)
PARTICLE_SIZE = (2, 5)
PARTICLE_LIFE = (0.35, 0.8)
PARTICLE_DRAG = 2.5
EXPLOSION_COLORS = [(255, 255, 255), (255, 225, 90), (255, 150, 40), (255, 80, 60)]

BG_COLOR = (8, 8, 20)
PLAYER_COLOR = (80, 255, 120)
PLAYER_BULLET_COLOR = (254, 254, 254)
ENEMY_BULLET_COLOR = (255, 90, 90)
SHIELD_COLOR = (95, 80, 60)
TEXT_COLOR = (240, 240, 240)
GAMEOVER_COLOR = (242, 27, 27)
NIVELSUPERADO_COLOR = (21, 216, 242)


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


class Game:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.lives = START_LIVES
        self.state = "playing"
        self.player_x = WIDTH / 2
        self.invulnerable = 0.0
        self.level_timer = 0.0
        self.particles = []
        self.build_level()

    def build_level(self):
        self.enemies = {(c, r) for r in range(ENEMY_ROWS) for c in range(ENEMY_COLS)}
        self.total_enemies = len(self.enemies)
        self.form_x = float(FORMATION_START_X)
        self.form_y = float(FORMATION_START_Y)
        self.form_dir = 1
        self.anim_enemies_timer = 0.0
        self.shields = build_shields()
        self.player_bullets = []
        self.enemy_bullets = []
        if self.level >= len(ENEMY_SHOT_MIN):
            self.shot_timer = random.uniform(ENEMY_SHOT_MIN[-1], ENEMY_SHOT_MAX[-1])
        else:
            self.shot_timer = random.uniform(ENEMY_SHOT_MIN[self.level], ENEMY_SHOT_MAX[self.level])

    def player_rect(self):
        return pygame.Rect(round(self.player_x - PLAYER_W / 2), PLAYER_Y, PLAYER_W, PLAYER_H)

    def enemy_rect(self, c, r):
        x = self.form_x + c * (ENEMY_W + ENEMY_GAP_X)
        y = self.form_y + r * (ENEMY_H + ENEMY_GAP_Y)
        return pygame.Rect(round(x), round(y), ENEMY_W, ENEMY_H)

    def lowest_enemy_bottom(self):
        last_row = max(r for _, r in self.enemies)
        return self.form_y + last_row * (ENEMY_H + ENEMY_GAP_Y) + ENEMY_H

    def fire(self):
        if self.state == "playing" and len(self.player_bullets) < MAX_PLAYER_BULLETS:
            self.player_bullets.append([self.player_x - BULLET_W / 2, float(PLAYER_Y - 10)])

    def damage_shields(self, center):
        r2 = SHIELD_HIT_RADIUS ** 2
        self.shields = [
            b for b in self.shields
            if (b.centerx - center[0]) ** 2 + (b.centery - center[1]) ** 2 > r2
        ]

    def lose_life(self):
        self.lives -= 1
        self.enemy_bullets = []
        self.player_bullets = []
        if self.lives <= 0:
            self.state = "game_over"
            return
        limit = PLAYER_Y - ENEMY_SAFE_GAP
        lowest = self.lowest_enemy_bottom()
        if lowest > limit:
            self.form_y -= lowest - limit
        self.player_x = WIDTH / 2
        self.invulnerable = INVULNERABLE_TIME

    def update_formation(self, dt):
        alive = len(self.enemies)
        speed = ENEMY_BASE_SPEED + ENEMY_SPEED_BONUS * (1 - alive / self.total_enemies)
        self.form_x += self.form_dir * speed * dt
        cols = [c for c, _ in self.enemies]
        step = ENEMY_W + ENEMY_GAP_X
        left = self.form_x + min(cols) * step
        right = self.form_x + max(cols) * step + ENEMY_W
        if self.form_dir > 0 and right >= WIDTH - FORMATION_MARGIN:
            self.form_x -= right - (WIDTH - FORMATION_MARGIN)
            self.form_dir = -1
            self.form_y += ENEMY_DROP
        elif self.form_dir < 0 and left <= FORMATION_MARGIN:
            self.form_x += FORMATION_MARGIN - left
            self.form_dir = 1
            self.form_y += ENEMY_DROP

    def erode_shields_with_enemies(self):
        if self.lowest_enemy_bottom() < SHIELD_Y:
            return
        for c, r in self.enemies:
            rect = self.enemy_rect(c, r)
            self.shields = [b for b in self.shields if not rect.colliderect(b)]

    def enemy_shoot(self):
        columns = {}
        for c, r in self.enemies:
            if c not in columns or r > columns[c]:
                columns[c] = r
        c = random.choice(list(columns))
        rect = self.enemy_rect(c, columns[c])
        self.enemy_bullets.append([rect.centerx - BULLET_W / 2, float(rect.bottom)])

    def update_player_bullets(self, dt):
        alive = []
        for bullet in self.player_bullets:
            bullet[1] -= PLAYER_BULLET_SPEED * dt
            rect = pygame.Rect(round(bullet[0]), round(bullet[1]), BULLET_W, BULLET_H)
            if rect.bottom < 0:
                continue
            idx = rect.collidelist(self.shields)
            if idx != -1:
                self.damage_shields(self.shields[idx].center)
                continue
            hit = None
            for c, r in self.enemies:
                if rect.colliderect(self.enemy_rect(c, r)):
                    hit = (c, r)
                    break
            if hit is not None:
                spawn_explosion(self.particles, self.enemy_rect(*hit).center)
                self.enemies.discard(hit)
                self.score += ROW_POINTS[hit[1]]
                continue
            alive.append(bullet)
        self.player_bullets = alive

    def update_enemy_bullets(self, dt):
        player = self.player_rect()
        alive = []
        for bullet in self.enemy_bullets:
            bullet[1] += ENEMY_BULLET_SPEED * dt
            if bullet[1] >= HEIGHT:
                continue
            rect = pygame.Rect(round(bullet[0]), round(bullet[1]), BULLET_W, BULLET_H)
            idx = rect.collidelist(self.shields)
            if idx != -1:
                self.damage_shields(self.shields[idx].center)
                continue
            if self.invulnerable <= 0 and rect.colliderect(player):
                return True
            alive.append(bullet)
        self.enemy_bullets = alive
        return False

    def update(self, dt, move):
        update_particles(self.particles, dt)
        if self.state == "level_clear":
            self.level_timer -= dt
            if self.level_timer <= 0:
                self.level += 1
                self.build_level()
                self.state = "playing"
            return
        if self.state != "playing":
            return

        self.anim_enemies_timer += dt
        if self.anim_enemies_timer >= ENEMY_ANIM_DURATION:
            self.anim_enemies_timer = 0.0

        self.player_x += move * PLAYER_SPEED * dt
        self.player_x = max(PLAYER_W / 2, min(WIDTH - PLAYER_W / 2, self.player_x))
        if self.invulnerable > 0:
            self.invulnerable = max(0.0, self.invulnerable - dt)

        self.update_formation(dt)
        self.erode_shields_with_enemies()

        self.shot_timer -= dt
        if self.shot_timer <= 0:
            self.enemy_shoot()

            if self.level >= len(ENEMY_SHOT_MIN):
                self.shot_timer = random.uniform(ENEMY_SHOT_MIN[-1], ENEMY_SHOT_MAX[-1])
            else:
                self.shot_timer = random.uniform(ENEMY_SHOT_MIN[self.level], ENEMY_SHOT_MAX[self.level])

        self.update_player_bullets(dt)
        if self.update_enemy_bullets(dt):
            self.lose_life()
            return

        if not self.enemies:
            self.state = "level_clear"
            self.level_timer = LEVEL_CLEAR_TIME
            self.enemy_bullets = []
            self.player_bullets = []
            return

        if self.invulnerable <= 0:
            player = self.player_rect()
            for c, r in self.enemies:
                rect = self.enemy_rect(c, r)
                if rect.colliderect(player) or rect.bottom >= PLAYER_Y:
                    self.lose_life()
                    return

    def draw(self, surface, font, big_font, sprites):
        surface.fill(BG_COLOR)
        surface.blit(sprites["bg"], (0, 0))

        for c, r in self.enemies:
            if self.anim_enemies_timer < ENEMY_ANIM_DURATION / 2:
                surface.blit(sprites[ROW_SPRITES[r]], self.enemy_rect(c, r).topleft)
            else:
                surface.blit(sprites[ROW_SPRITES_2[r]], self.enemy_rect(c, r).topleft)
        
        for block in self.shields:
            surface.blit(sprites["shield_block"], block.topleft)
        if self.state != "game_over":
            blink_off = self.invulnerable > 0 and int(self.invulnerable * 10) % 2 == 0
            if not blink_off:
                surface.blit(sprites["player"], self.player_rect().topleft)
        for x, y in self.player_bullets:
            surface.blit(sprites["player_bullet"], (round(x), round(y)))
        for x, y in self.enemy_bullets:
            surface.blit(sprites["enemy_bullet"], (round(x), round(y)))
        draw_particles(surface, self.particles)

        surface.blit(font.render(f"Puntos: {self.score}", True, TEXT_COLOR), (15, 10))
        level_img = font.render(f"Nivel: {self.level}", True, TEXT_COLOR)
        surface.blit(level_img, level_img.get_rect(midtop=(WIDTH // 2, 10)))
        lives_img = font.render(f"Vidas: {max(self.lives, 0)}", True, TEXT_COLOR)
        surface.blit(lives_img, lives_img.get_rect(topright=(WIDTH - 15, 10)))

        if self.state == "level_clear":
            draw_centered(surface, big_font, f"NIVEL {self.level} SUPERADO", HEIGHT // 2)
        elif self.state == "game_over":
            draw_centered(surface, big_font, "GAME OVER", HEIGHT // 2 - 20)
            draw_centered(surface, font, f"Puntuación final: {self.score}", HEIGHT // 2 + 30)
            draw_centered(surface, font, "Espacio para reiniciar", HEIGHT // 2 + 65)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 72)
    sprites = load_sprites()

    game = Game()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game.state == "game_over":
                    game = Game()
                else:
                    game.fire()

        keys = pygame.key.get_pressed()
        move = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        game.update(dt, move)
        game.draw(screen, font, big_font, sprites)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()




