import pygame
import random
from constants import *
from class_sonidos import Sonidos
from functions import build_shields, spawn_explosion, update_particles, draw_particles, draw_centered

class Game:
    def __init__(self):
        self.sonidos = Sonidos()
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
        self.sonidos.reproducir("inicio-nivel")
        self.enemies = {(c, r) for r in range(ENEMY_ROWS) for c in range(ENEMY_COLS)}
        self.total_enemies = len(self.enemies)
        self.form_x = float(FORMATION_START_X)
        self.form_y = float(FORMATION_START_Y)
        self.form_dir = 1
        self.anim_enemies_timer = 0.0
        self.respawn_player_timer = 0.0
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
        if self.state == "playing" and len(self.player_bullets) < MAX_PLAYER_BULLETS and self.respawn_player_timer == 0.0:
            self.sonidos.reproducir("fire")
            self.player_bullets.append([self.player_x - BULLET_W / 2, float(PLAYER_Y - 10)])

    def damage_shields(self, center):
        r2 = SHIELD_HIT_RADIUS ** 2
        self.shields = [
            b for b in self.shields
            if (b.centerx - center[0]) ** 2 + (b.centery - center[1]) ** 2 > r2
        ]

    def lose_life(self):
        spawn_explosion(self.particles, (self.player_x, PLAYER_Y))
        self.sonidos.reproducir("jugador-explota")
        self.respawn_player_timer = RESPAWN_PLAYER_DURATION
        self.lives -= 1
        self.enemy_bullets = []
        self.player_bullets = []
        if self.lives <= 0:
            self.sonidos.reproducir("gameover")
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
                    self.sonidos.reproducir("explo-enemy")
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

        if self.respawn_player_timer > 0.0:
            self.respawn_player_timer -= dt
            if self.respawn_player_timer < 0.0:
                self.respawn_player_timer = 0.0

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
            self.sonidos.reproducir("level-up")
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
            if self.respawn_player_timer > 0.0:
                pass
            else:
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




