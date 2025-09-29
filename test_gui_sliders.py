# This file has been deleted.
#!/usr/bin/env python3
"""
Тест GUI с новыми процентными слайдерами
"""

import pygame
import sys
import os

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_sliders():
    """Тестирует отображение новых процентных слайдеров"""
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Тест процентных слайдеров")
    
    # Импортируем компоненты после инициализации pygame
    from guitar_life_patched import UISlider, SimpleColors
    
    # Создаем тестовые слайдеры
    spawn_slider = UISlider(50, 50, 200, 30, 0, 100, 30, "Spawn %", "{:.0f}%")
    cells_slider = UISlider(50, 100, 200, 30, 5, 50, 20, "Old Init", "{:.0f}")
    
    clock = pygame.time.Clock()
    running = True
    
    print("🎮 GUI тест запущен")
    print("📊 Новый слайдер: 'Spawn %' (0-100%)")
    print("📊 Старый слайдер: 'Old Init' (5-50)")
    print("❌ Закройте окно для завершения")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Обрабатываем события слайдеров
            spawn_slider.handle_event(event)
            cells_slider.handle_event(event)
        
        # Очищаем экран
        screen.fill(SimpleColors.GRAY_100)
        
        # Рисуем слайдеры
        font = pygame.font.Font(None, 24)
        spawn_slider.draw(screen, font)
        cells_slider.draw(screen, font)
        
        # Добавляем заголовки
        font = pygame.font.Font(None, 24)
        title1 = font.render("Новый формат (проценты):", True, SimpleColors.GRAY_700)
        title2 = font.render("Старый формат (количество):", True, SimpleColors.GRAY_700)
        
        screen.blit(title1, (50, 25))
        screen.blit(title2, (50, 75))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ GUI тест завершен")

if __name__ == "__main__":
    test_gui_sliders()