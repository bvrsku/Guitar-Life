import pygame
import sys

# Инициализация pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Simple Text Test")

# Создание шрифта
font = pygame.font.SysFont("consolas", 16, bold=True)

# Тестовые строки - только ASCII
test_texts = [
    "Tick (ms): 120",
    "RMS Power (%): 100", 
    "Max Age: 120",
    "CONTROL PANEL"
]

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    
    screen.fill((30, 30, 40))
    
    y = 50
    for text in test_texts:
        try:
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (20, y))
            y += 30
        except Exception as e:
            print(f"Error: {e}")
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Font test completed successfully")