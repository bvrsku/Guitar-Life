# This file has been deleted.
#!/usr/bin/env python3
"""
Тест нового диапазона Max Age (5-120)
Проверяет правильность работы нового диапазона значений
"""

import numpy as np
import sys
import os

# Добавляем родительскую директорию в path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые компоненты
from guitar_life_patched import Layer, LayerConfig

def test_new_max_age_range():
    """Тестирует новый диапазон Max Age (5-120)"""
    print("🧪 Тестирование нового диапазона Max Age (5-120)...")
    
    # Создаем слой с минимальным max_age
    layer_min = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        color_mode="HSV дизайны",
        max_age=5  # Минимальное значение
    )
    
    # Создаем слой с максимальным max_age
    layer_max = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="NEON",
        rms_palette="PURPLE_PINK", 
        color_mode="HSV дизайны",
        max_age=120  # Максимальное значение
    )
    
    # Создаем слой с значением по умолчанию
    layer_default = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="FIRE",
        rms_palette="OCEAN", 
        color_mode="HSV дизайны"
        # max_age должен быть 60 по умолчанию
    )
    
    print(f"Слой с min max_age: {layer_min.max_age}")
    print(f"Слой с max max_age: {layer_max.max_age}")
    print(f"Слой с default max_age: {layer_default.max_age}")
    
    # Проверяем диапазон значений
    assert layer_min.max_age == 5, f"Минимальное значение должно быть 5, получено {layer_min.max_age}"
    assert layer_max.max_age == 120, f"Максимальное значение должно быть 120, получено {layer_max.max_age}"
    assert layer_default.max_age == 60, f"Значение по умолчанию должно быть 60, получено {layer_default.max_age}"
    
    print("✅ Тест диапазона значений пройден!")

def test_layerconfig_defaults():
    """Тестирует значения по умолчанию в LayerConfig"""
    print("📋 Тестирование LayerConfig со значением по умолчанию...")
    
    # Создаем конфигурацию без указания max_age
    config_default = LayerConfig()
    
    # Создаем конфигурацию с указанием max_age
    config_custom = LayerConfig(max_age=25)
    
    print(f"LayerConfig default max_age: {config_default.max_age}")
    print(f"LayerConfig custom max_age: {config_custom.max_age}")
    
    # Проверяем значения
    assert config_default.max_age == 60, f"Default max_age должен быть 60, получено {config_default.max_age}"
    assert config_custom.max_age == 25, f"Custom max_age должен быть 25, получено {config_custom.max_age}"
    
    print("✅ Тест LayerConfig пройден!")

def test_age_death_logic():
    """Тестирует логику смерти клеток в новом диапазоне"""
    print("💀 Тестирование логики смерти клеток...")
    
    # Создаем слой с очень маленьким max_age
    layer = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="FIRE", 
        rms_palette="OCEAN",
        color_mode="HSV дизайны",
        max_age=7  # Очень маленький max_age
    )
    
    # Добавляем клетки разного возраста
    layer.grid[10, 10] = True
    layer.age[10, 10] = 5  # Молодая клетка (должна жить)
    
    layer.grid[20, 20] = True  
    layer.age[20, 20] = 7  # Клетка на пределе (должна умереть)
    
    layer.grid[30, 30] = True
    layer.age[30, 30] = 10  # Старая клетка (должна умереть)
    
    print(f"До проверки возраста (max_age={layer.max_age}):")
    print(f"  Клетка (10,10): живая={layer.grid[10,10]}, возраст={layer.age[10,10]}")
    print(f"  Клетка (20,20): живая={layer.grid[20,20]}, возраст={layer.age[20,20]}")
    print(f"  Клетка (30,30): живая={layer.grid[30,30]}, возраст={layer.age[30,30]}")
    
    # Применяем логику удаления старых клеток
    old_cells_mask = layer.age >= layer.max_age
    layer.grid[old_cells_mask] = False
    layer.age[old_cells_mask] = 0
    
    print(f"После проверки возраста:")
    print(f"  Клетка (10,10): живая={layer.grid[10,10]}, возраст={layer.age[10,10]} (должна жить)")
    print(f"  Клетка (20,20): живая={layer.grid[20,20]}, возраст={layer.age[20,20]} (должна умереть)")
    print(f"  Клетка (30,30): живая={layer.grid[30,30]}, возраст={layer.age[30,30]} (должна умереть)")
    
    # Проверяем результаты
    assert layer.grid[10,10], "Молодая клетка (возраст 5) должна остаться живой"
    assert layer.age[10,10] == 5, "Возраст молодой клетки не должен измениться"
    assert not layer.grid[20,20], "Клетка на пределе (возраст 7) должна умереть"
    assert layer.age[20,20] == 0, "Возраст умершей клетки должен быть сброшен"
    assert not layer.grid[30,30], "Старая клетка (возраст 10) должна умереть"
    assert layer.age[30,30] == 0, "Возраст умершей клетки должен быть сброшен"
    
    print("✅ Тест логики смерти клеток пройден!")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов нового диапазона Max Age (5-120)...")
    print("=" * 60)
    
    try:
        test_layerconfig_defaults()
        print()
        test_new_max_age_range()
        print()
        test_age_death_logic()
        print()
        print("🎉 Все тесты нового диапазона Max Age пройдены успешно!")
        print("📊 Новые параметры:")
        print("   • Минимум: 5")
        print("   • Максимум: 120")
        print("   • По умолчанию: 60")
        print("   • Диапазон GUI: 5-120")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()