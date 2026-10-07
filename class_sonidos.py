import pygame
import os
from constants import ASSETS_DIR

# ====================================================================================
class Sonidos:
    """Funcion constructora"""
    def __init__(self):
        pygame.mixer.init()
        self.sonidos = self.cargar_sonidos()
    
    # -------------------------------------------------------------------------
    def cargar_sonidos(self):
        """Cargar todos los sonidos en un diccionario."""
        return {
            "level-up": self.cargar_sonido("alien-atmos-dark.mp3", 0.7),
            "fire": self.cargar_sonido("disparo-corto.mp3", 0.5),
            "explo-enemy": self.cargar_sonido("explosion.wav", 0.6),
            "gameover": self.cargar_sonido("game-over-arcade-retro.mp3"),
            "inicio-nivel": self.cargar_sonido("invaders-are-here.mp3", 0.8),
            "jugador-explota": self.cargar_sonido("navexplota.mp3", 0.7),
            "level-passed": self.cargar_sonido("level-passed.mp3", 0.6)
        }
    
    # -------------------------------------------------------------------------
    def cargar_sonido(self, filename, volumen=1.0):
        """Carga un sonido específico con el volumen indicado."""
        path = os.path.join(ASSETS_DIR, filename)

        if os.path.isfile(path):
            try:
                sonido = pygame.mixer.Sound(path)
                sonido.set_volume(volumen)
                return sonido
            except pygame.error:
                return None
        
        return None
    
    # -------------------------------------------------------------------------
    def reproducir(self, nombre, duracion=None):
        """Reproduce un sonido si está en el diccionario."""
        if nombre in self.sonidos:
            if duracion == None:
                self.sonidos[nombre].play()
            else:
                self.sonidos[nombre].play(maxtime=duracion)



