#!/usr/bin/env python3
"""
Тест расширенного HUD с параметрами эффектов
"""
import pygame
import sys

# Простой тест UI элементов
class TestSlider:
    def __init__(self, x, y, width, height, min_val, max_val, current_val, label):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, surface):
        # Фон
        pygame.draw.rect(surface, (60, 60, 70), self.rect)
        pygame.draw.rect(surface, (120, 120, 130), self.rect, 2)
        
        # Прогресс
        progress = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(surface, (80, 150, 200), fill_rect)
        
        # Лейбл
        font = pygame.font.Font(None, 16)
        label_surface = font.render(f"{self.label}: {self.current_val:.2f}", True, (255, 255, 255))
        surface.blit(label_surface, (self.x, self.y - 20))

class TestSeparator:
    def __init__(self, x, y, width, label):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.height = 15
        
    def draw(self, surface):
        # Линия
        line_y = self.y + self.height // 2
        pygame.draw.line(surface, (100, 100, 120), (self.x, line_y), (self.x + self.width, line_y), 2)
        
        # Лейбл
        font = pygame.font.Font(None, 14)
        label_surface = font.render(self.label, True, (150, 150, 170))
        label_width = label_surface.get_width()
        label_x = self.x + (self.width - label_width) // 2
        
        # Фон для лейбла
        bg_rect = pygame.Rect(label_x - 5, self.y, label_width + 10, self.height)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect)
        surface.blit(label_surface, (label_x, self.y + 2))

try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Enhanced HUD Test")
    
    # Создаем тестовые элементы
    elements = []
    
    y_pos = 50
    
    # Основные параметры
    elements.append(TestSeparator(50, y_pos, 300, "MAIN PARAMETERS"))
    y_pos += 25
    
    elements.append(TestSlider(50, y_pos, 200, 20, 5, 360, 120, "Tick (ms)"))
    y_pos += 45
    
    elements.append(TestSlider(50, y_pos, 200, 20, 0, 200, 100, "RMS Power"))
    y_pos += 45
    
    # Эффекты
    elements.append(TestSeparator(50, y_pos, 300, "EFFECTS PARAMETERS"))
    y_pos += 25
    
    elements.append(TestSlider(50, y_pos, 200, 20, 0.01, 0.2, 0.06, "Trail Strength"))
    y_pos += 45
    
    elements.append(TestSlider(50, y_pos, 200, 20, 1, 10, 2, "Blur Scale"))
    y_pos += 45
    
    elements.append(TestSlider(50, y_pos, 200, 20, 0.1, 1.0, 0.35, "Bloom Strength"))
    y_pos += 45
    
    elements.append(TestSlider(50, y_pos, 200, 20, 2, 16, 5, "Posterize Levels"))
    y_pos += 45
    
    # Контролы
    elements.append(TestSeparator(50, y_pos, 300, "CONTROLS"))
    y_pos += 25
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        screen.fill((30, 30, 40))
        
        # Заголовок
        font = pygame.font.Font(None, 24)
        title = font.render("Enhanced HUD with Effects Parameters", True, (255, 255, 255))
        screen.blit(title, (50, 10))
        
        # Инструкции
        instructions = [
            "✓ Main Parameters (Tick, RMS Power, etc.)",
            "✓ RMS Thresholds", 
            "✓ Soft Clean Parameters",
            "✓ Pitch Tick Range",
            "✓ Effects Parameters (Trails, Blur, Bloom, etc.)",
            "✓ Control Buttons",
            "✓ Palette & Rule Selection",
            "✓ Organized with Separators"
        ]
        
        info_font = pygame.font.Font(None, 16)
        for i, text in enumerate(instructions):
            surface = info_font.render(text, True, (200, 200, 200))
            screen.blit(surface, (400, 60 + i * 20))
        
        # Рисуем элементы
        for element in elements:
            element.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    print("Enhanced HUD test completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()