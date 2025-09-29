#!/usr/bin/env python3
"""
Тест параметров очистки clear_type и soft_mode в HUD
"""

import os
import sys
import time
import pygame

# Добавляем папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import App

def test_clear_parameters():
    """Тестирует параметры очистки в HUD"""
    print("🎯 Тестирование параметров clear_type и soft_mode в HUD...")
    
    # Инициализация pygame
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    
    # Создаем минимальные настройки
    sel = {
        'device': 0,
        'layer_count': 3,
        'layers': [
            {'solo': False, 'mute': False},
            {'solo': False, 'mute': False},
            {'solo': False, 'mute': False}
        ]
    }
    
    # Создаем приложение
    app = App(sel)
    
    # Тестируем clear_type
    print("\n🧹 Тестирование clear_type:")
    clear_types = ['Полная очистка', 'Частичная очистка', 'По возрасту клеток', 'Случайная очистка']
    
    for clear_type in clear_types:
        print(f"  ✓ Устанавливаем clear_type = '{clear_type}'")
        app.on_hud_parameter_change('clear_type', clear_type)
        print(f"    ✓ Установлено: app.clear_type = '{app.clear_type}'")
        assert app.clear_type == clear_type, f"Clear type не изменился: {app.clear_type} != {clear_type}"
    
    # Тестируем soft_mode
    print("\n💫 Тестирование soft_mode:")
    # Используем значения комбобокса (английские)
    soft_modes_combo = ['Kill', 'Fade', 'Fade+Kill']
    # Ожидаемые русские значения
    soft_modes_expected = ['Удалять клетки', 'Затухание клеток', 'Затухание + удаление']
    
    for i, soft_mode in enumerate(soft_modes_combo):
        expected = soft_modes_expected[i]
        print(f"  ✓ Устанавливаем soft_mode = '{soft_mode}'")
        app.on_hud_parameter_change('soft_mode', soft_mode)
        print(f"    ✓ Установлено: app.soft_mode = '{app.soft_mode}'")
        assert app.soft_mode == expected, f"Soft mode не изменился: {app.soft_mode} != {expected}"
    
    # Проверяем HUD комбобоксы
    print("\n🎛️ Проверка HUD комбобоксов:")
    if hasattr(app, 'hud') and app.hud:
        # Проверяем clear_type комбобокс
        if 'clear_type' in app.hud.comboboxes:
            clear_combo = app.hud.comboboxes['clear_type']
            print(f"  ✓ Clear type комбобокс найден")
            print(f"    Опции: {clear_combo.options}")
            print(f"    Текущий индекс: {clear_combo.current_index}")
            print(f"    Текущее значение: {clear_combo.options[clear_combo.current_index]}")
        else:
            print("  ❌ Clear type комбобокс не найден")
        
        # Проверяем soft_mode комбобокс
        if 'soft_mode' in app.hud.comboboxes:
            soft_combo = app.hud.comboboxes['soft_mode']
            print(f"  ✓ Soft mode комбобокс найден")
            print(f"    Опции: {soft_combo.options}")
            print(f"    Текущий индекс: {soft_combo.current_index}")
            print(f"    Текущее значение: {soft_combo.options[soft_combo.current_index]}")
        else:
            print("  ❌ Soft mode комбобокс не найден")
    
    # Тестируем функции очистки
    print("\n🧹 Тестирование функций очистки:")
    
    # Создаем тестовые клетки
    for layer in app.layers:
        for x in range(10, 20):
            for y in range(10, 20):
                layer.grid[y][x] = 10
                layer.age[y][x] = 15
    
    print("  ✓ Создали тестовые клетки (10x10 область)")
    
    # Тестируем каждый тип очистки
    for clear_type in clear_types:
        app.clear_type = clear_type
        print(f"  🧹 Тестируем очистку: {clear_type}")
        
        # Создаем клетки заново
        for layer in app.layers:
            for x in range(10, 20):
                for y in range(10, 20):
                    layer.grid[y][x] = 10
                    layer.age[y][x] = 15
        
        # Выполняем очистку
        app.clear_with_type()
        
        # Проверяем результат
        total_cells = sum(sum(sum(row) for row in layer.grid) for layer in app.layers)
        print(f"    Клеток после очистки: {total_cells}")
    
    print("\n✅ Все тесты параметров очистки пройдены успешно!")
    
    pygame.quit()

if __name__ == "__main__":
    test_clear_parameters()