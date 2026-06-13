# ... existing code ...

def create_asr():
    asr = pygame.sprite.Sprite()
    # Ajustamos la escala del ASR para que sea más grande
    asr.image = pygame.transform.scale(asr.image, (80, 80))
    asr.rect = asr.image.get_rect()

# ... existing code ...

def draw_screen():
    screen.fill((255, 255, 255))  # Ajustamos el color de fondo para que no interfiera con los ASR
    # ... existing code ...
    for asr in asr_group:
        screen.blit(asr.image, asr.rect)
    # ... existing code ...

# ... rest of code ...