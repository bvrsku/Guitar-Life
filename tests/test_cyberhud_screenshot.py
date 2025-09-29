#!/usr/bin/env python3
"""
Тестовый скрипт для создания скриншота нового CyberHUD
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
    pygame.display.set_caption("CyberHUD Screenshot Test")
    
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
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    # Сохраняем скриншот
                    pygame.image.save(screen, "cyberhud_screenshot.png")
                    print("Скриншот сохранен: cyberhud_screenshot.png")
            
            # Передаем события HUD
            hud.handle_event(event)
        
        # Очищаем экран
        screen.fill((0, 0, 0))
        
        # Рисуем фон симуляции (имитация)
        for x in range(0, 960, 20):
            for y in range(0, 800, 20):
                color = (0, 40, 20) if (x // 20 + y // 20) % 2 == 0 else (0, 60, 30)
                pygame.draw.rect(screen, color, (x, y, 20, 20))
        
        # Рисуем HUD
        hud.draw(screen, test_info)
        
        # Инструкции
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "CyberHUD Test - Нажмите клавиши:",
            "ESC - Выход",
            "S - Сохранить скриншот", 
            "Клик по вкладкам для переключения категорий",
            "Колесо мыши для скролла параметров"
        ]
        
        for i, text in enumerate(instructions):
            color = (0, 255, 100) if i == 0 else (0, 180, 80)
            text_surface = font_small.render(text, True, color)
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()