# This file has been deleted.
#!/usr/bin/env python3
"""
Тест расположения элементов управления в HUD
Проверяет, что ползунок Palette Mix теперь находится в правой колонке под RMS Mode
"""

import pygame
import sys

# Импортируем классы из основного файла
try:
    from guitar_life_patched_HUD import HUD, SimpleColors
except ImportError:
    print("❌ Не удалось импортировать HUD из guitar_life_patched_HUD")
    print("Убедитесь, что файл существует и содержит класс HUD")
    sys.exit(1)

def main():
    pygame.init()
    
    # Создаем окно
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Тест расположения ползунка Palette Mix")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)
    
    # Создаем HUD с несколькими слоями для тестирования
    hud = HUD(font, 800, layer_count=3)
    hud.visible = True
    
    # Информация для отображения
    test_info = {
        "Layers": "3",
        "Alive": "150 cells",
        "RMS": "0.1234",
        "Pitch": "440.0 Hz"
    }
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    hud.visible = not hud.visible
            
            # Передаем события в HUD
            hud.handle_event(event)
        
        # Отрисовка
        screen.fill((40, 44, 52))
        
        # Заголовок
        title = font.render("Тест расположения Palette Mix ползунка", True, (255, 255, 255))
        screen.blit(title, (50, 20))
        
        # Инструкции
        instructions = [
            "Проверьте расположение элементов:",
            "• Левая колонка: Age Palette, Alpha Live, Alpha Old, Max Age, Rule, Blend Mode, Spawn Method",
            "• Правая колонка: RMS Palette, Initial Cells %, RMS Mode, Palette Mix ←← (должен быть здесь!)",
            "",
            "Клавиши:",
            "H - показать/скрыть HUD",
            "Esc - выход"
        ]
        
        for i, instruction in enumerate(instructions):
            color = (150, 255, 150) if "Palette Mix" in instruction else (200, 200, 200)
            text = font.render(instruction, True, color)
            screen.blit(text, (50, 60 + i * 25))
        
        # Отрисовка HUD
        hud.draw(screen, test_info)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()