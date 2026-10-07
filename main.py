# ==================================================================
#                INVADERS (Space Invaders clon)
#  
#                     By Juan Eguia, 2026
# ==================================================================
import pygame
import sys
from constants import *
from class_game import Game
from functions import load_sprites

# ==================================================================
#   Main function
# ==================================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 72)
    big_font.set_bold(True)
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

# ==========================================
#  Invoke main() function
# ==========================================
if __name__ == "__main__":
    main()




