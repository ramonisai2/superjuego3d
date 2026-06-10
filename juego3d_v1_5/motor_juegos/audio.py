import pygame

class AudioManager:
    def __init__(self):
        # Inicializamos el mezclador de Pygame si no se ha hecho antes
        if not pygame.mixer.get_init():
            # Configuraciones estándar para audio digital limpio y sin lag
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}

    def load_music(self, file_path):
        """Carga la pista de música de fondo (Streaming desde el disco)."""
        try:
            pygame.mixer.music.load(file_path)
        except Exception as e:
            print(f"[AUDIO ERROR] No se pudo cargar la música '{file_path}': {e}")

    def play_music(self, loops=-1, volume=0.3):
        """Reproduce la música cargada (-1 para bucle infinito)."""
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def load_sound_effect(self, name, file_path):
        """Carga un efecto de sonido corto en la memoria RAM (ej. disparo, salto)."""
        try:
            self.sounds[name] = pygame.mixer.Sound(file_path)
        except Exception as e:
            print(f"[AUDIO ERROR] No se pudo cargar el efecto '{file_path}': {e}")

    def play_sound(self, name, volume=0.6):
        """Reproduce un efecto de sonido de forma segura si existe."""
        try:
            if name in self.sounds:
                self.sounds[name].set_volume(volume)
                self.sounds[name].play()
        except Exception:
            pass # Si el sonido falla o no está cargado, lo ignora silenciosamente

