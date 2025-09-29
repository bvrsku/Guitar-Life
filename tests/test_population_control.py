#!/usr/bin/env python3
"""
Тест для проверки работы исправленной системы удаления клеток при перенаселении.
"""

import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Создаем упрощенную модель для тестирования
class MockLayer:
    def __init__(self, width, height):
        self.grid = np.zeros((height, width), dtype=bool)
        self.age = np.zeros((height, width), dtype=int)

class MockApp:
    def __init__(self):
        self.soft_clear_enable = True
        self.max_cells_percent = 50
        self.soft_clear_threshold = 70
        self.soft_kill_rate = 80
        self.age_bias = 80
        self.soft_mode = "Удалять клетки"
        self.layers = [MockLayer(100, 100)]  # Сетка 100x100

def test_population_control_logic():
    """Тестируем новую логику удаления клеток"""
    print("Тест новой логики контроля популяции:")
    print("=" * 50)
    
    app = MockApp()
    
    # Константы для расчетов (как в реальном коде)
    GRID_H, GRID_W = 100, 100
    total_grid_size = GRID_H * GRID_W
    max_allowed_cells = int(total_grid_size * app.max_cells_percent / 100.0)
    clear_threshold_cells = int(total_grid_size * app.soft_clear_threshold / 100.0)
    
    print(f"Размер сетки: {GRID_H}x{GRID_W} = {total_grid_size} клеток")
    print(f"Максимум разрешено: {max_allowed_cells} клеток ({app.max_cells_percent}%)")
    print(f"Порог очистки: {clear_threshold_cells} клеток ({app.soft_clear_threshold}%)")
    print(f"Интенсивность удаления: {app.soft_kill_rate}%")
    print()
    
    # Тестируем разные уровни заполнения
    test_scenarios = [
        (6000, "Ниже порога очистки"),
        (7500, "Превышение порога, но ниже максимума"),
        (6000, "Превышение максимума"),  # Это будет 6000, но мы проверим максимум 5500
    ]
    
    for scenario_idx, (total_cells, description) in enumerate(test_scenarios):
        if scenario_idx == 2:
            total_cells = 6000  # Превышение максимума
        
        print(f"Сценарий {scenario_idx + 1}: {description}")
        print(f"Количество клеток: {total_cells}")
        
        # Заполняем сетку случайными клетками
        app.layers[0].grid.fill(False)
        app.layers[0].age.fill(0)
        
        # Создаем живые клетки
        positions = np.random.choice(total_grid_size, size=total_cells, replace=False)
        rows = positions // GRID_W
        cols = positions % GRID_W
        app.layers[0].grid[rows, cols] = True
        app.layers[0].age[rows, cols] = np.random.randint(1, 50, size=total_cells)
        
        # Проверяем логику удаления
        if total_cells > clear_threshold_cells:
            if total_cells > max_allowed_cells:
                # Агрессивное удаление
                excess_ratio = (total_cells - max_allowed_cells) / total_cells
                removal_rate = max(10, int(total_cells * app.soft_kill_rate / 100.0 * (1.0 + excess_ratio)))
                print(f"  → Агрессивное удаление:")
                print(f"    excess_ratio = ({total_cells} - {max_allowed_cells}) / {total_cells} = {excess_ratio:.3f}")
                print(f"    removal_rate = max(10, {total_cells} * {app.soft_kill_rate}/100 * (1 + {excess_ratio:.3f})) = {removal_rate}")
            else:
                # Мягкое удаление
                threshold_ratio = (total_cells - clear_threshold_cells) / (max_allowed_cells - clear_threshold_cells)
                removal_rate = max(5, int(total_cells * app.soft_kill_rate / 100.0 * threshold_ratio * 0.5))
                print(f"  → Мягкое удаление:")
                print(f"    threshold_ratio = ({total_cells} - {clear_threshold_cells}) / ({max_allowed_cells} - {clear_threshold_cells}) = {threshold_ratio:.3f}")
                print(f"    removal_rate = max(5, {total_cells} * {app.soft_kill_rate}/100 * {threshold_ratio:.3f} * 0.5) = {removal_rate}")
            
            print(f"  → Будет удалено: {removal_rate} клеток ({removal_rate/total_cells*100:.1f}%)")
        else:
            print(f"  → Удаление не требуется (ниже порога)")
        
        print()

def test_old_vs_new_logic():
    """Сравниваем старую и новую логику"""
    print("Сравнение старой и новой логики:")
    print("=" * 40)
    
    # Параметры
    total_grid_size = 10000
    max_cells_percent = 50
    soft_clear_threshold = 70
    soft_kill_rate = 80
    
    max_allowed_cells = int(total_grid_size * max_cells_percent / 100.0)
    clear_threshold_cells = int(total_grid_size * soft_clear_threshold / 100.0)
    
    test_cases = [6000, 7500, 8000]
    
    for total_cells in test_cases:
        print(f"Клеток: {total_cells}")
        
        if total_cells > clear_threshold_cells:
            # СТАРАЯ логика (неправильная)
            old_excess_ratio = min(1.0, (total_cells - max_allowed_cells) / max_allowed_cells)
            old_removal_rate = max(5, int(soft_kill_rate * old_excess_ratio / 100.0))
            
            # НОВАЯ логика (исправленная)
            if total_cells > max_allowed_cells:
                new_excess_ratio = (total_cells - max_allowed_cells) / total_cells
                new_removal_rate = max(10, int(total_cells * soft_kill_rate / 100.0 * (1.0 + new_excess_ratio)))
                mode = "агрессивное"
            else:
                new_threshold_ratio = (total_cells - clear_threshold_cells) / (max_allowed_cells - clear_threshold_cells)
                new_removal_rate = max(5, int(total_cells * soft_kill_rate / 100.0 * new_threshold_ratio * 0.5))
                mode = "мягкое"
            
            print(f"  Старая логика: excess_ratio={old_excess_ratio:.3f}, removal_rate={old_removal_rate}")
            print(f"  Новая логика: {mode}, removal_rate={new_removal_rate}")
            print(f"  Разница: {new_removal_rate - old_removal_rate:+d} клеток")
        else:
            print(f"  Удаление не требуется")
        print()

if __name__ == "__main__":
    test_population_control_logic()
    print()
    test_old_vs_new_logic()