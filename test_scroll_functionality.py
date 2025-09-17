#!/usr/bin/env python3
"""
Тест функции прокрутки GUI колесиком мыши
"""

import pygame
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые классы
from guitar_life import TabPanel, Slider, Button, Dropdown, Label

def test_scroll_gui():
    """Тест прокрутки GUI"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Scroll GUI")
    clock = pygame.time.Clock()
    
    # Создаем TabPanel
    tab_panel = TabPanel(50, 50, 500, 400)
    
    # Создаем много элементов для тестирования прокрутки
    elements = []
    for i in range(20):
        y_offset = 80 + i * 35
        
        if i % 3 == 0:
            # Слайдеры
            slider = Slider(70, y_offset, 200, 20, 0, 100, 50, f"Param {i}")
            elements.append(slider)
        elif i % 3 == 1:
            # Кнопки
            button = Button(70, y_offset, 150, 25, f"Button {i}")
            elements.append(button)
        else:
            # Dropdown'ы
            dropdown = Dropdown(70, y_offset, 200, 25, ["Option 1", "Option 2", "Option 3"], 0, f"Dropdown {i}")
            elements.append(dropdown)
    
    # Добавляем вкладку с элементами
    tab_panel.add_tab("Test Scroll", elements)
    
    print("=== Тест прокрутки GUI ===")
    print("Используйте колесико мыши для прокрутки содержимого вкладки")
    print("Нажмите ESC для выхода")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Передаем события в TabPanel
            tab_panel.handle_event(event)
        
        # Отрисовка
        screen.fill((30, 30, 30))
        tab_panel.draw(screen)
        
        # Отображаем информацию о прокрутке
        font = pygame.font.Font(None, 24)
        scroll_text = f"Scroll Offset: {tab_panel.scroll_offset} / {tab_panel.max_scroll}"
        text_surface = font.render(scroll_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    test_scroll_gui()