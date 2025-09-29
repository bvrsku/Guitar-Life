#!/usr/bin/env python3
"""
Тест навигации по категориям CyberHUD
"""

import pygame
import sys
import os

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

def main():
    pygame.init()
    
    # Создаем окно
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("CyberHUD Category Navigation Test")
    
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
    
    print("🎯 Начинаем тест навигации по категориям...")
    print(f"📂 Доступные категории: {hud.categories}")
    print(f"🔄 Начальная категория: {hud.active_category}")
    
    # Тестируем каждую категорию
    for i, category in enumerate(hud.categories):
        print(f"\n📋 Тестируем категорию {i+1}/{len(hud.categories)}: {category}")
        
        # Переключаемся на категорию
        hud.active_category = category
        hud.scroll_offset = 0
        
        # Получаем параметры для этой категории
        params = hud.category_params.get(category, [])
        print(f"⚙️  Параметры в категории '{category}': {len(params)} шт.")
        for param in params:
            param_info = hud._get_param_info(param)
            if param_info:
                print(f"   • {param_info['label']} ({param_info['type']})")
            else:
                print(f"   • {param} (не настроен)")
        
        # Рисуем HUD для этой категории
        screen.fill((0, 0, 0))
        
        # Фон симуляции
        for x in range(0, 960, 40):
            for y in range(0, 800, 40):
                color = (0, 30, 15) if (x // 40 + y // 40) % 2 == 0 else (0, 50, 25)
                pygame.draw.rect(screen, color, (x, y, 40, 40))
        
        # Рисуем HUD
        try:
            hud.draw(screen, test_info)
            
            # Добавляем статус информацию
            status_font = pygame.font.Font(None, 24)
            status_lines = [
                f"Testing Category: {category}",
                f"Parameters: {len(params)}",
                f"Scroll: {hud.scroll_offset}",
                f"Category {i+1}/{len(hud.categories)}"
            ]
            
            for j, line in enumerate(status_lines):
                color = (255, 255, 255) if j == 0 else (200, 200, 200)
                text_surface = status_font.render(line, True, color)
                screen.blit(text_surface, (10, 10 + j * 25))
            
            pygame.display.flip()
            
            # Сохраняем скриншот для каждой категории
            filename = f"cyberhud_{category.lower()}_screenshot.png"
            pygame.image.save(screen, filename)
            print(f"📸 Скриншот сохранен: {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка при отрисовке категории '{category}': {e}")
        
        # Небольшая пауза
        pygame.time.wait(500)
    
    print("\n🎉 Тест навигации завершен!")
    print("📁 Созданы скриншоты для всех категорий:")
    for category in hud.categories:
        print(f"   • cyberhud_{category.lower()}_screenshot.png")
    
    pygame.quit()

if __name__ == "__main__":
    main()