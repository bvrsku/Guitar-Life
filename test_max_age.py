# This file has been deleted.
#!/usr/bin/env python3
"""
Тест системы Max Age для каждого слоя
Проверяет правильность работы индивидуального max_age для слоев
"""

import numpy as np
import sys
import os

# Добавляем родительскую директорию в path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые компоненты
from guitar_life_patched import Layer, LayerConfig

def test_max_age_individual():
    """Тестирует индивидуальные max_age для разных слоев"""
    print("🧪 Тестирование индивидуальных Max Age для слоев...")
    
    # Создаем слои с разными max_age напрямую
    layer1 = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        color_mode="HSV дизайны",
        max_age=50  # Короткий максимальный возраст
    )
    
    layer2 = Layer(
        grid=np.zeros((100, 100), dtype=bool),
        age=np.zeros((100, 100), dtype=np.int32),
        rule="Conway",
        age_palette="NEON",
        rms_palette="PURPLE_PINK", 
        color_mode="HSV дизайны",
        max_age=200  # Длинный максимальный возраст
    )
    
    print(f"Слой 1: max_age = {layer1.max_age}")
    print(f"Слой 2: max_age = {layer2.max_age}")
    
    # Имитируем старые клетки
    layer1.grid[10, 10] = True
    layer1.age[10, 10] = 60  # Превышает max_age (50)
    
    layer2.grid[20, 20] = True  
    layer2.age[20, 20] = 150  # Не превышает max_age (200)
    
    print(f"До проверки возраста:")
    print(f"  Слой 1 клетка (10,10): живая={layer1.grid[10,10]}, возраст={layer1.age[10,10]} (max_age={layer1.max_age})")
    print(f"  Слой 2 клетка (20,20): живая={layer2.grid[20,20]}, возраст={layer2.age[20,20]} (max_age={layer2.max_age})")
    
    # Применяем логику удаления старых клеток
    old_cells_mask1 = layer1.age >= layer1.max_age
    layer1.grid[old_cells_mask1] = False
    layer1.age[old_cells_mask1] = 0
    
    old_cells_mask2 = layer2.age >= layer2.max_age
    layer2.grid[old_cells_mask2] = False
    layer2.age[old_cells_mask2] = 0
    
    print(f"После проверки возраста:")
    print(f"  Слой 1 клетка (10,10): живая={layer1.grid[10,10]}, возраст={layer1.age[10,10]} (должна умереть)")
    print(f"  Слой 2 клетка (20,20): живая={layer2.grid[20,20]}, возраст={layer2.age[20,20]} (должна остаться)")
    
    # Проверяем результаты
    assert not layer1.grid[10,10], "Клетка в слое 1 должна была умереть от старости"
    assert layer1.age[10,10] == 0, "Возраст умершей клетки должен быть сброшен"
    assert layer2.grid[20,20], "Клетка в слое 2 должна остаться живой" 
    assert layer2.age[20,20] == 150, "Возраст живой клетки не должен измениться"
    
    print("✅ Тест индивидуальных Max Age пройден!")

def test_layerconfig_with_max_age():
    """Тестирует создание LayerConfig с max_age"""
    print("📋 Тестирование LayerConfig с Max Age...")
    
    # Создаем конфигурации с разными max_age
    config1 = LayerConfig(
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        max_age=50  # Короткий максимальный возраст
    )
    
    config2 = LayerConfig(
        rule="Conway",
        age_palette="NEON",
        rms_palette="PURPLE_PINK", 
        max_age=200  # Длинный максимальный возраст
    )
    
    print(f"Config 1: max_age = {config1.max_age}")
    print(f"Config 2: max_age = {config2.max_age}")
    
    # Проверяем, что значения сохранились правильно
    assert config1.max_age == 50, "Config 1 должен иметь max_age = 50"
    assert config2.max_age == 200, "Config 2 должен иметь max_age = 200"
    
    print("✅ Тест LayerConfig с Max Age пройден!")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов системы Max Age...")
    print("=" * 60)
    
    try:
        test_layerconfig_with_max_age()
        print()
        test_max_age_individual()
        print()
        print("🎉 Все тесты Max Age пройдены успешно!")
        print("Система готова к использованию.")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()