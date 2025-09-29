# This file has been deleted.
#!/usr/bin/env python3
"""
Тест улучшенной навигации по контекстному меню
Клавиши для тестирования:
- ↑/↓ - навигация по элементам
- Enter/Space - выбор элемента
- Escape - закрытие без изменений
- Home/End - к первому/последнему элементу
- Page Up/Page Down - прокрутка страницами
- Колесо мыши - прокрутка в открытом меню
"""

import pygame
import sys

# Импортируем класс из основного файла
try:
    from guitar_life_patched_HUD import UIComboBox, SimpleColors
except ImportError:
    print("❌ Не удалось импортировать UIComboBox из guitar_life_patched_HUD")
    print("Убедитесь, что файл существует и содержит класс UIComboBox")
    sys.exit(1)

def main():
    pygame.init()
    
    # Создаем окно
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест навигации в контекстном меню")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)
    
    # Создаем тестовые комбобоксы
    palettes = [
        "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth",
        "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
        "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
        "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight",
        "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black"
    ]
    
    rules = ["Conway", "HighLife", "Day&Night", "Replicator", "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"]
    
    combo1 = UIComboBox(50, 100, 200, 30, "Age Palette", palettes, 0)
    combo2 = UIComboBox(300, 100, 200, 30, "RMS Palette", palettes, 5)
    combo3 = UIComboBox(50, 200, 200, 30, "CA Rule", rules, 0)
    
    combos = [combo1, combo2, combo3]
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Обрабатываем события для каждого комбобокса
            for combo in combos:
                combo.handle_event(event)
        
        # Отрисовка
        screen.fill((40, 44, 52))
        
        # Заголовок
        title = font.render("Тест навигации в контекстном меню", True, (255, 255, 255))
        screen.blit(title, (50, 20))
        
        # Инструкции
        instructions = [
            "Клавиши навигации:",
            "↑/↓ - навигация по элементам",
            "Enter/Space - выбор элемента", 
            "Escape - закрытие без изменений",
            "Home/End - к первому/последнему",
            "Page Up/Down - прокрутка страницами",
            "Колесо мыши - прокрутка в меню",
            "Ввод текста - быстрый поиск",
            "Backspace - удаление символа поиска"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 300 + i * 25))
        
        # Отрисовка комбобоксов
        for combo in combos:
            # Рисуем подпись
            label_text = font.render(combo.label + ":", True, (255, 255, 255))
            screen.blit(label_text, (combo.x, combo.y - 25))
            
            # Рисуем комбобокс
            combo.draw(screen, font)
            
            # Показываем текущее значение
            value_text = font.render(f"Выбрано: {combo.current_value}", True, (150, 255, 150))
            screen.blit(value_text, (combo.x, combo.y + 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()