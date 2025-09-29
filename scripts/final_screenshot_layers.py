#!/usr/bin/env python3
"""
Создает финальный скриншот CyberHUD с новым функционалом управления слоями
"""

import pygame
import sys
import time
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_final_screenshot():
    """Создает финальный скриншот"""
    print("📸 Создаем финальный скриншот Guitar Life с управлением слоями...")
    
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("Guitar Life - Layer Management Complete")
    
    # Создаем шрифт
    font = pygame.font.SysFont("times new roman", 16)
    
    try:
        # Запускаем демонстрацию
        from demo_layer_management import create_demo_hud, create_mock_app
        
        hud = create_demo_hud(font)
        app = create_mock_app()
        
        # Устанавливаем режим LAYERS
        hud.active_category = 'LAYERS'
        
        # Имитируем различные состояния слоев
        app.layers[0].solo = True
        app.layers[1].mute = True
        app.layers[2].grid = app.layers[2].grid * 0  # Очищаем слой
        
        # Добавляем клетки для демонстрации
        for i, layer in enumerate(app.layers):
            if not layer.mute:
                # Добавляем случайные клетки
                import numpy as np
                for _ in range(50 + i * 30):
                    x = np.random.randint(0, 96)
                    y = np.random.randint(0, 60)
                    layer.grid[y, x] = 1
        
        # Обновляем информацию
        app.layers[0].cell_count = int(app.layers[0].grid.sum())
        app.layers[1].cell_count = int(app.layers[1].grid.sum())
        app.layers[2].cell_count = int(app.layers[2].grid.sum())
        
        # Отрисовка
        screen.fill((5, 5, 15))
        
        # Рисуем игровое поле
        game_rect = pygame.Rect(10, 10, 960, 560)
        pygame.draw.rect(screen, (20, 25, 35), game_rect)
        pygame.draw.rect(screen, (40, 50, 70), game_rect, 2)
        
        # Добавляем заголовок
        title_font = pygame.font.SysFont("arial", 24, bold=True)
        title = title_font.render("Guitar Life - Layer Management Complete ✅", True, (100, 255, 100))
        screen.blit(title, (20, 20))
        
        # Добавляем описание
        desc_font = pygame.font.SysFont("arial", 16)
        descriptions = [
            "🚀 Новые возможности управления слоями:",
            "   ➕ Add Layer - добавление новых слоев",
            "   ➖ Remove - удаление слоев", 
            "   🧹 Clear - очистка выбранного слоя",
            "   🎭 Solo All / Unsolo All - управление solo режимом",
            "   🔇 Mute All / Unmute All - управление звуком слоев",
            "📊 Расширенная визуализация состояния каждого слоя",
            "🎛️ Полная интеграция с системой событий CyberHUD"
        ]
        
        for i, desc in enumerate(descriptions):
            text = desc_font.render(desc, True, (180, 180, 200))
            screen.blit(text, (20, 60 + i * 22))
        
        # Информация для HUD
        info = {
            'fps': 60,
            'cells': sum(layer.cell_count for layer in app.layers),
            'layers': len(app.layers)
        }
        
        # Рисуем HUD
        hud.draw(screen, info)
        
        # Добавляем аннотации
        annotation_font = pygame.font.SysFont("arial", 14, bold=True)
        
        # Стрелка к кнопкам управления
        pygame.draw.circle(screen, (255, 100, 100), (1050, 300), 8)
        arrow_text = annotation_font.render("← Новые кнопки", True, (255, 100, 100))
        screen.blit(arrow_text, (950, 295))
        
        # Стрелка к визуализации слоев
        pygame.draw.circle(screen, (100, 255, 100), (1050, 450), 8)
        status_text = annotation_font.render("← Статус слоев", True, (100, 255, 100))
        screen.blit(status_text, (950, 445))
        
        pygame.display.flip()
        
        # Сохраняем скриншот
        timestamp = int(time.time())
        filename = f"guitar_life_layer_management_complete_{timestamp}.png"
        pygame.image.save(screen, filename)
        
        print(f"✅ Скриншот сохранен: {filename}")
        print("📋 Функциональность управления слоями полностью интегрирована!")
        
        # Показываем скриншот немного
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Ошибка создания скриншота: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    create_final_screenshot()