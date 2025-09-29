#!/usr/bin/env python3
"""
Тест исправленной обработки событий в CyberHUD
"""
import pygame
import sys
sys.path.append('c:\\REPOS\\Guitar-Life')

from guitar_lifeE import CyberHUD

pygame.init()
screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("CyberHUD Event Test")
clock = pygame.time.Clock()

# Создаем HUD
font = pygame.font.SysFont("courier new", 12)
hud = CyberHUD(font, 800, 3)

print("✅ CyberHUD создан успешно")
print(f"📊 Контролы созданы:")
print(f"  - Слайдеры: {len(hud.sliders)}")
print(f"  - Кнопки: {len(hud.buttons)}")
print(f"  - Комбо-боксы: {len(hud.comboboxes)}")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_h:
                hud.visible = not hud.visible
                print(f"HUD видимость: {hud.visible}")
        
        # Тестируем обработку событий HUD
        if hud.handle_event(event):
            print(f"✅ HUD обработал событие: {event.type}")
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"   Клик по позиции: {event.pos}")
                print(f"   Активная категория: {hud.active_category}")
    
    # Отрисовка
    screen.fill((5, 5, 10))
    
    # Рисуем HUD
    info = {'fps': 60, 'cells': 1000}
    hud.draw(screen, info)
    
    # Инструкции
    if hud.visible:
        font_help = pygame.font.SysFont("arial", 16)
        help_text = font_help.render("H - переключить HUD, клик по кнопкам/слайдерам для теста", True, (255, 255, 255))
        screen.blit(help_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Тест завершен")