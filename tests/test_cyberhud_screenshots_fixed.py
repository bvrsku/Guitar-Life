#!/usr/bin/env python3
"""
Создание скриншота исправленного CyberHUD
"""
import pygame
import sys
import time
sys.path.append('c:\\REPOS\\Guitar-Life')

from guitar_lifeE import CyberHUD

pygame.init()
screen = pygame.display.set_mode((1400, 800))

# Создаем HUD
font = pygame.font.SysFont("courier new", 12)
hud = CyberHUD(font, 800, 3)

print("📸 Создание скриншотов исправленного CyberHUD...")

categories = ['AUDIO', 'VISUAL', 'LAYERS', 'EFFECTS', 'PERF', 'ACTIONS']

for category in categories:
    # Переключаем категорию
    hud.active_category = category
    
    # Заполняем экран
    screen.fill((5, 5, 10))
    
    # Информация для отображения
    info = {
        'fps': 60,
        'cells_alive': 5000,
        'rms': 0.025,
        'pitch': 440.0,
        'births': 35,
        'gain': 150,
        'rms_strength': 85,
        'aging_speed': 2.3,
        'max_age': 180,
        'global_v_mul': 1.2,
        'fade_start': 60,
        'fade_sat_drop': 70
    }
    
    # Рисуем HUD
    hud.draw(screen, info)
    
    # Добавляем заголовок категории
    title_font = pygame.font.SysFont("arial", 24, bold=True)
    title_text = title_font.render(f"CyberHUD - {category} (Fixed)", True, (0, 255, 100))
    screen.blit(title_text, (10, 10))
    
    # Сохраняем скриншот
    screenshot_path = f"cyberhud_fixed_{category.lower()}_screenshot.png"
    pygame.image.save(screen, screenshot_path)
    print(f"✅ {category}: {screenshot_path}")

pygame.quit()
print("🎉 Все скриншоты созданы!")