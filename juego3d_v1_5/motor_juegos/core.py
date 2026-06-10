import pygame
from pygame.locals import *
from OpenGL.GL import *
from motor_juegos.runtime_perf import perf_tracker

class GameEngine:
    def __init__(self, width=800, height=600, title="Mi Motor 3D/2D"):
        pygame.init()
        self.width = width
        self.height = height
        
        pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)
        
        self.screen = pygame.display.set_mode(
            (width, height), DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.dt = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.is_running = False

    def run(self, update_func, render_2d_func, render_3d_func):
        while self.is_running:
            self.dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            
            if not self.is_running:
                break
                
            with perf_tracker.measure("update"):
                update_func(self.dt)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # --- 1. GRÁFICOS 3D (Se activa la profundidad) ---
            glEnable(GL_DEPTH_TEST)
            glViewport(0, 0, self.width, self.height)
            with perf_tracker.measure("render3d"):
                render_3d_func()
            
            # --- 2. GRÁFICOS 2D (Fuerza primer plano absoluto) ---
            glViewport(0, 0, self.width, self.height)
            with perf_tracker.measure("render2d"):
                render_2d_func()
            
            with perf_tracker.measure("flip"):
                pygame.display.flip()
            perf_tracker.finish_frame(self.dt, self.clock.get_fps())
            
        pygame.quit()
