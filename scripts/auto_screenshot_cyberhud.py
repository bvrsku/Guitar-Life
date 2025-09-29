#!/usr/bin/env python3
"""
Автоматический скриншот CyberHUD без интерактивности
"""

import pygame
import sys
import os

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeeq import CyberHUD

def main():
    pygame.init()
    
    # Создаем окно
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("CyberHUD Auto Screenshot")
    
    # Создаем шрифт
    font = pygame.font.SysFont("courier new", 12, bold=True)
    
    # Создаем CyberHUD
    hud = CyberHUD(font, 800, 3)
    
    # Тестовая информация
    test_info = {
        'fps': 60,
        'cells': 15000,
        'rms': 0.0275,
        'layers': 3
    }
    
    # Очищаем экран
    screen.fill((0, 0, 0))
    
    # Рисуем фон симуляции (имитация)
    for x in range(0, 960, 20):
        for y in range(0, 800, 20):
            color = (0, 40, 20) if (x // 20 + y // 20) % 2 == 0 else (0, 60, 30)
            pygame.draw.rect(screen, color, (x, y, 20, 20))
    
    # Рисуем HUD
    try:
        hud.draw(screen, test_info)
        print("✅ CyberHUD отрисован успешно!")
    except Exception as e:
        print(f"❌ Ошибка при отрисовке HUD: {e}")
        return
    
    # Инструкции
    font_small = pygame.font.Font(None, 24)
    instructions = [
        "🎯 CyberHUD Successfully Rendered!",
        f"📊 Active Category: {hud.active_category}",
        f"🔧 Categories: {', '.join(hud.categories)}",
        f"📐 Position: {hud.x}x{hud.y}, Size: {hud.width}x{hud.height}",
        "💾 Screenshot saved automatically"
    ]
    
    for i, text in enumerate(instructions):
        color = (0, 255, 100) if i == 0 else (0, 180, 80)
        text_surface = font_small.render(text, True, color)
        screen.blit(text_surface, (10, 10 + i * 25))
    
    pygame.display.flip()
    
    # Сохраняем скриншот
    try:
        pygame.image.save(screen, "cyberhud_screenshot.png")
        print("📸 Скриншот сохранен: cyberhud_screenshot.png")
    except Exception as e:
        print(f"❌ Ошибка сохранения скриншота: {e}")
    
    # Ждем 2 секунды чтобы увидеть результат
    pygame.time.wait(2000)
    
    pygame.quit()
    print("🎉 Тест завершен успешно!")

if __name__ == "__main__":
    main()