#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новых типов очистки в Guitar Life
Проверяет работу различных вариантов очистки
"""

import os
import sys
import time
import numpy as np

# Добавляем путь к модулю guitar_lifeeq
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_lifeE import App, GRID_H, GRID_W, CLEAR_TYPES
    import pygame
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

def create_test_cells(app, num_cells=100):
    """Создает тестовые клетки различного возраста"""
    for layer in app.layers:
        layer.grid[:] = False
        layer.age[:] = 0
        
        # Добавляем клетки разного возраста
        for i in range(num_cells):
            r = np.random.randint(0, GRID_H)
            c = np.random.randint(0, GRID_W)
            layer.grid[r, c] = True
            # Случайный возраст от 1 до 20
            layer.age[r, c] = np.random.randint(1, 21)
    
    total_cells = sum(np.sum(layer.grid) for layer in app.layers)
    print(f"Создано {total_cells} тестовых клеток")
    return total_cells

def count_cells(app):
    """Подсчитывает общее количество живых клеток"""
    return sum(np.sum(layer.grid) for layer in app.layers)

def count_old_cells(app, age_threshold=10):
    """Подсчитывает количество старых клеток"""
    old_count = 0
    for layer in app.layers:
        old_cells = (layer.grid) & (layer.age >= age_threshold)
        old_count += np.sum(old_cells)
    return old_count

def test_clear_type(app, clear_type, description):
    """Тестирует конкретный тип очистки"""
    print(f"\n=== Тест: {description} ===")
    
    # Создаем тестовые клетки
    initial_cells = create_test_cells(app, 80)
    old_cells_before = count_old_cells(app, 10)
    
    print(f"До очистки: {initial_cells} клеток, {old_cells_before} старых (возраст >= 10)")
    
    # Устанавливаем тип очистки
    app.clear_type = clear_type
    
    # Выполняем очистку
    app.clear_with_type()
    
    # Подсчитываем результат
    cells_after = count_cells(app)
    old_cells_after = count_old_cells(app, 10)
    
    print(f"После очистки: {cells_after} клеток, {old_cells_after} старых")
    print(f"Удалено: {initial_cells - cells_after} клеток")
    
    return {
        'type': clear_type,
        'before': initial_cells,
        'after': cells_after,
        'removed': initial_cells - cells_after,
        'old_before': old_cells_before,
        'old_after': old_cells_after
    }

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование типов очистки Guitar Life")
    print("=" * 50)
    
    # Минимальная конфигурация для тестирования
    test_config = {
        'layer_count': 2,
        'clear_type': 'Полная очистка',
        'layers_different': True,
        'layers_cfg': []  # Пустой список, будет использоваться конфигурация по умолчанию
    }
    
    try:
        # Инициализируем pygame без окна
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        
        # Создаем приложение
        app = App(test_config)
        
        # Тестируем все типы очистки
        results = []
        
        # 1. Полная очистка
        result = test_clear_type(app, "Полная очистка", "Удаление всех клеток")
        results.append(result)
        
        # 2. Частичная очистка
        result = test_clear_type(app, "Частичная очистка", "Удаление 50% клеток")
        results.append(result)
        
        # 3. Очистка по возрасту
        result = test_clear_type(app, "Очистка по возрасту", "Удаление клеток старше 10")
        results.append(result)
        
        # 4. Случайная очистка
        result = test_clear_type(app, "Случайная очистка", "Удаление 30% случайных клеток")
        results.append(result)
        
        # Выводим сводку результатов
        print("\n" + "=" * 50)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        for result in results:
            efficiency = (result['removed'] / result['before'] * 100) if result['before'] > 0 else 0
            print(f"{result['type']:<20} | Удалено: {result['removed']:3d} ({efficiency:5.1f}%)")
        
        # Проверяем доступность типов очистки
        print(f"\nДоступные типы очистки: {CLEAR_TYPES}")
        
        print("\n✅ Все тесты выполнены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)