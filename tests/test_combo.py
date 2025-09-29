#!/usr/bin/env python3
import pygame
import sys

# Простой тест комбобокса
class TestComboBox:
    def __init__(self, x, y, width, height, label, options, current_index=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.options = options
        self.current_index = current_index
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = False
        self.hover_index = -1
        
    @property
    def current_value(self):
        if 0 <= self.current_index < len(self.options):
            return self.options[self.current_index]
        return ""
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            if self.rect.collidepoint(event.pos):
                if not self.is_open:
                    self.is_open = True
                    return True
                else:
                    relative_y = mouse_y - (self.y + self.height)
                    if relative_y >= 0:
                        option_index = relative_y // self.height
                        if 0 <= option_index < len(self.options):
                            self.current_index = option_index
                            self.is_open = False
                            return True
            else:
                if self.is_open:
                    self.is_open = False
                    return True
        elif event.type == pygame.MOUSEMOTION and self.is_open:
            mouse_x, mouse_y = event.pos
            relative_y = mouse_y - (self.y + self.height)
            if relative_y >= 0:
                option_index = relative_y // self.height
                if 0 <= option_index < len(self.options):
                    self.hover_index = option_index
                else:
                    self.hover_index = -1
            else:
                self.hover_index = -1
        return False
    
    def draw(self, surface):
        # Основная область
        bg_color = (70, 70, 80) if self.is_open else (60, 60, 70)
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, (120, 120, 130), self.rect, 2)
        
        font = pygame.font.Font(None, 20)
        
        # Лейбл
        label_surface = font.render(self.label, True, (255, 255, 255))
        surface.blit(label_surface, (self.x, self.y - 25))
        
        # Текущее значение
        current_text = self.current_value[:15] + "..." if len(self.current_value) > 15 else self.current_value
        text_surface = font.render(current_text, True, (255, 255, 255))
        surface.blit(text_surface, (self.x + 5, self.y + 3))
        
        # Стрелка
        arrow_x = self.x + self.width - 15
        arrow_y = self.y + self.height // 2
        if self.is_open:
            pygame.draw.polygon(surface, (200, 200, 200), [
                (arrow_x, arrow_y + 3), (arrow_x + 8, arrow_y + 3), (arrow_x + 4, arrow_y - 3)
            ])
        else:
            pygame.draw.polygon(surface, (200, 200, 200), [
                (arrow_x, arrow_y - 3), (arrow_x + 8, arrow_y - 3), (arrow_x + 4, arrow_y + 3)
            ])
        
        # Выпадающий список
        if self.is_open:
            dropdown_height = len(self.options) * self.height
            dropdown_rect = pygame.Rect(self.x, self.y + self.height, self.width, dropdown_height)
            pygame.draw.rect(surface, (50, 50, 60), dropdown_rect)
            pygame.draw.rect(surface, (120, 120, 130), dropdown_rect, 2)
            
            for i, option in enumerate(self.options):
                option_y = self.y + self.height + i * self.height
                option_rect = pygame.Rect(self.x, option_y, self.width, self.height)
                
                if i == self.hover_index:
                    pygame.draw.rect(surface, (80, 80, 90), option_rect)
                elif i == self.current_index:
                    pygame.draw.rect(surface, (60, 80, 60), option_rect)
                
                option_text = option[:15] + "..." if len(option) > 15 else option
                option_surface = font.render(option_text, True, (255, 255, 255))
                surface.blit(option_surface, (self.x + 5, option_y + 3))

try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("ComboBox Test")
    
    # Создаем тестовые комбобоксы
    palette_options = ["Blue->Green->Yellow->Red", "Fire", "Ocean", "Neon", "Ukraine"]
    rule_options = ["Conway", "HighLife", "Day&Night", "Replicator"]
    
    palette_combo = TestComboBox(50, 100, 200, 25, "Palette", palette_options)
    rule_combo = TestComboBox(300, 100, 150, 25, "Rule", rule_options)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                palette_combo.handle_event(event)
                rule_combo.handle_event(event)
        
        screen.fill((30, 30, 40))
        
        # Инструкции
        font = pygame.font.Font(None, 24)
        instructions = [
            "ComboBox Test",
            f"Selected Palette: {palette_combo.current_value}",
            f"Selected Rule: {rule_combo.current_value}",
            "Click on comboboxes to test"
        ]
        
        for i, text in enumerate(instructions):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (50, 20 + i * 25))
        
        palette_combo.draw(screen)
        rule_combo.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    print("ComboBox test completed successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()