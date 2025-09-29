#!/usr/bin/env python3
import pygame
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    pygame.init()
    print("Testing scroll functionality...")
    
    # Создаем окно
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("HUD Scroll Test")
    
    # Создаем тестовые слайдеры
    sliders = []
    for i in range(15):  # Создаем много слайдеров для тестирования скролла
        slider = type('TestSlider', (), {
            'x': 100,
            'y': 100 + i * 50,
            'width': 200,
            'height': 20,
            'rect': pygame.Rect(100, 100 + i * 50, 200, 20),
            'label': f'Test Slider {i+1}',
            'value': 50,
            'draw': lambda self, surface: pygame.draw.rect(surface, (100, 150, 200), self.rect)
        })()
        sliders.append(slider)
    
    scroll_offset = 0
    scroll_speed = 30
    max_scroll = max(0, (len(sliders) * 50) - 400)  # Простой расчет
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - scroll_speed)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    scroll_offset = min(max_scroll, scroll_offset + scroll_speed)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * scroll_speed
                scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        screen.fill((30, 30, 40))
        
        # Рисуем инструкции
        font = pygame.font.Font(None, 24)
        instructions = [
            "Test HUD Scrolling:",
            "W/S or Arrow Keys to scroll",
            "Mouse wheel to scroll",
            f"Scroll: {scroll_offset}/{max_scroll}"
        ]
        
        for i, text in enumerate(instructions):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, 10 + i * 25))
        
        # Создаем область обрезки
        content_rect = pygame.Rect(50, 150, 300, 400)
        pygame.draw.rect(screen, (50, 50, 60), content_rect, 2)
        
        # Сохраняем область обрезки и устанавливаем новую
        original_clip = screen.get_clip()
        screen.set_clip(content_rect)
        
        # Рисуем слайдеры с учетом скролла
        scroll_y = -scroll_offset
        for slider in sliders:
            original_y = slider.y
            original_rect_y = slider.rect.y
            
            slider.y += scroll_y
            slider.rect.y += scroll_y
            
            # Рисуем только видимые элементы
            if content_rect.top <= slider.y + slider.height <= content_rect.bottom:
                pygame.draw.rect(screen, (100, 150, 200), slider.rect)
                # Текст лейбла
                text_surface = font.render(slider.label, True, (255, 255, 255))
                screen.blit(text_surface, (slider.x, slider.y - 25))
            
            # Восстанавливаем позиции
            slider.y = original_y
            slider.rect.y = original_rect_y
        
        # Восстанавливаем область обрезки
        screen.set_clip(original_clip)
        
        # Рисуем полосу прокрутки
        if max_scroll > 0:
            scroll_progress = scroll_offset / max_scroll
            scroll_bar_height = 50
            scroll_bar_y = 150 + scroll_progress * (400 - scroll_bar_height)
            scroll_bar_rect = pygame.Rect(360, scroll_bar_y, 10, scroll_bar_height)
            pygame.draw.rect(screen, (100, 150, 200), scroll_bar_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    print("Test completed successfully")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()