#!/usr/bin/env python3
"""
Интерактивный тест CyberHUD с исправленными позициями
"""
import pygame
import sys
sys.path.append('c:\\REPOS\\Guitar-Life')

from guitar_lifeE import CyberHUD

pygame.init()
screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("CyberHUD Fixed Positions Test")
clock = pygame.time.Clock()

# Создаем HUD
font = pygame.font.SysFont("courier new", 12)
hud = CyberHUD(font, 800, 3)

print("🎮 CyberHUD Test запущен!")
print("📋 Инструкции:")
print("  - Клик по вкладкам для переключения категорий")
print("  - Клик и перетаскивание слайдеров")
print("  - Клик по кнопкам для переключения")
print("  - H для скрытия/показа HUD")
print("  - ESC для выхода")

print(f"\n📊 Контролы:")
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"✅ Клик обработан! Позиция: {event.pos}, Категория: {hud.active_category}")
    
    # Отрисовка
    screen.fill((5, 5, 10))
    
    # Рисуем HUD
    info = {
        'fps': 60,
        'cells_alive': 5000,
        'rms': 0.025,
        'pitch': 440.0,
        'births': 35,
        'gain': 150,
        'rms_strength': 85,
        'aging_speed': 2.3,
        'max_age': 180
    }

    hud.draw(screen, info)
    
    # Показываем инструкции
    if hud.visible:
        instructions = [
            "H - toggle HUD | Click tabs to switch categories",
            "Drag sliders | Click buttons | ESC to exit"
        ]
        font_help = pygame.font.SysFont("arial", 14)
        for i, instruction in enumerate(instructions):
            help_text = font_help.render(instruction, True, (200, 200, 200))
            screen.blit(help_text, (10, 10 + i * 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("✅ Тест завершен")