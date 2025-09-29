# This file has been deleted.
#!/usr/bin/env python3
"""
Тест процентного спавна клеток
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем константы и функции из основного файла
from guitar_life_patched import SPAWN_BASE, SPAWN_SCALE

def test_spawn_percentage():
    """Тестирует расчет процентного спавна"""
    
    print("🧪 Тестирование процентного спавна клеток")
    print(f"📊 Максимальное количество клеток от RMS: {SPAWN_BASE + SPAWN_SCALE}")
    print()
    
    # Тестируем различные значения RMS и проценты
    test_births_values = [50, 100, 200, 361]  # Различные значения births
    test_percentages = [0, 25, 50, 75, 100]   # Различные проценты
    
    print("RMS births | Процент | Результат")
    print("-" * 35)
    
    for births in test_births_values:
        for percent in test_percentages:
            result = int(births * (percent / 100.0))
            print(f"{births:9d} | {percent:6d}% | {result:8d}")
    
    print()
    print("✅ Формула: layer_births = int(births * (layer_percent / 100.0))")
    print("💡 births - количество клеток от уровня звука")
    print("💡 layer_percent - процент от 0 до 100% для каждого слоя")
    print("💡 layer_births - итоговое количество клеток для данного слоя")

if __name__ == "__main__":
    test_spawn_percentage()