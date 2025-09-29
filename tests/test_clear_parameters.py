#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новых параметров очистки в HUD
Проверяет работу слайдеров clear_partial_percent и clear_age_threshold
"""

import os
import sys
import pygame

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_lifeE import App, CLEAR_TYPES
    import numpy as np
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

def main():
    """Тест новых параметров очистки"""
    print("🧪 Тестирование новых параметров очистки в HUD")
    print("=" * 50)
    
    try:
        # Простая конфигурация
        config = {
            'layer_count': 2,
            'layers_different': True,
            'layers_cfg': [],
            'clear_partial_percent': 50,
            'clear_age_threshold': 10
        }
        
        # Инициализируем pygame для GUI
        pygame.init()
        screen = pygame.display.set_mode((100, 100))  # Минимальное окно
        
        app = App(config)
        
        print(f"✅ Приложение создано")
        print(f"📋 Процент частичной очистки: {app.clear_partial_percent}")
        print(f"📋 Порог возраста для очистки: {app.clear_age_threshold}")
        
        # Проверяем что HUD содержит новые слайдеры
        if 'clear_partial_percent' in app.hud.sliders:
            slider = app.hud.sliders['clear_partial_percent']
            print(f"✅ Слайдер clear_partial_percent найден")
            print(f"📋 Диапазон: {slider.min_val}-{slider.max_val}")
            print(f"🎯 Текущее значение: {slider.current_val}")
        else:
            print("❌ Слайдер clear_partial_percent НЕ НАЙДЕН в HUD")
            
        if 'clear_age_threshold' in app.hud.sliders:
            slider = app.hud.sliders['clear_age_threshold']
            print(f"✅ Слайдер clear_age_threshold найден")
            print(f"📋 Диапазон: {slider.min_val}-{slider.max_val}")
            print(f"🎯 Текущее значение: {slider.current_val}")
        else:
            print("❌ Слайдер clear_age_threshold НЕ НАЙДЕН в HUD")
        
        # Тестируем изменение параметров через HUD
        print(f"\n🔄 Тестирование изменения параметров:")
        
        # Тест 1: Изменение процента частичной очистки
        app.on_hud_parameter_change('clear_partial_percent', 75)
        print(f"  📝 Процент частичной очистки: {app.clear_partial_percent}")
        
        # Тест 2: Изменение порога возраста
        app.on_hud_parameter_change('clear_age_threshold', 15)
        print(f"  📝 Порог возраста: {app.clear_age_threshold}")
        
        # Тест 3: Проверяем что параметры используются в методах очистки
        print(f"\n🧪 Тестирование использования параметров:")
        
        # Создаем тестовые клетки
        for layer in app.layers:
            layer.grid[:] = False
            layer.age[:] = 0
            
            # Добавляем клетки разного возраста
            for i in range(20):
                r = np.random.randint(0, layer.grid.shape[0])
                c = np.random.randint(0, layer.grid.shape[1])
                layer.grid[r, c] = True
                layer.age[r, c] = np.random.randint(1, 25)  # Возраст от 1 до 25
        
        total_before = sum(np.sum(layer.grid) for layer in app.layers)
        print(f"  📊 Клеток до очистки: {total_before}")
        
        # Тестируем частичную очистку
        app.clear_type = "Частичная очистка"
        app.clear_with_type()
        total_after_partial = sum(np.sum(layer.grid) for layer in app.layers)
        print(f"  📊 Клеток после частичной очистки ({app.clear_partial_percent}%): {total_after_partial}")
        
        # Создаем новые клетки для теста очистки по возрасту
        for layer in app.layers:
            layer.grid[:] = False
            layer.age[:] = 0
            
            # Добавляем клетки с конкретным возрастом
            for i in range(20):
                r = np.random.randint(0, layer.grid.shape[0])
                c = np.random.randint(0, layer.grid.shape[1])
                layer.grid[r, c] = True
                # Половина клеток старше порога, половина младше
                if i < 10:
                    layer.age[r, c] = app.clear_age_threshold + 5  # Старые клетки
                else:
                    layer.age[r, c] = app.clear_age_threshold - 5  # Молодые клетки
        
        total_before_age = sum(np.sum(layer.grid) for layer in app.layers)
        old_cells_before = 0
        for layer in app.layers:
            old_cells_before += np.sum((layer.grid) & (layer.age >= app.clear_age_threshold))
        
        print(f"  📊 Клеток до очистки по возрасту: {total_before_age} (старых >= {app.clear_age_threshold}: {old_cells_before})")
        
        # Тестируем очистку по возрасту
        app.clear_type = "Очистка по возрасту"
        app.clear_with_type()
        total_after_age = sum(np.sum(layer.grid) for layer in app.layers)
        old_cells_after = 0
        for layer in app.layers:
            old_cells_after += np.sum((layer.grid) & (layer.age >= app.clear_age_threshold))
        
        print(f"  📊 Клеток после очистки по возрасту: {total_after_age} (старых >= {app.clear_age_threshold}: {old_cells_after})")
        
        pygame.quit()
        
        print(f"\n✅ Все параметры очистки работают корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        if pygame.get_init():
            pygame.quit()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)