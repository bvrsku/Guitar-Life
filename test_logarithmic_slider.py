# This file has been deleted.
#!/usr/bin/env python3
"""
Тест логарифмического слайдера Max Age
Проверяет корректность логарифмического масштабирования
"""

import sys
import os

# Добавляем родительскую директорию в path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logarithmic_scaling():
    """Тестирует логарифмическое масштабирование слайдера Max Age"""
    print("🧪 Тестирование логарифмического слайдера Max Age...")
    
    # Импортируем функции
    from guitar_life_patched import max_age_slider_to_value, max_age_value_to_slider
    
    # Тестовые значения
    test_cases = [
        # (позиция слайдера %, ожидаемый max_age)
        (0.0, 10),      # Минимум
        (25.0, 40),     # Четверть первой половины  
        (50.0, 70),     # Граница между половинами
        (75.0, None),   # Три четверти (расчет)
        (100.0, 500),   # Максимум
    ]
    
    print("🔍 Тестирование преобразования позиция слайдера → max_age:")
    for slider_pos, expected_max_age in test_cases:
        actual_max_age = max_age_slider_to_value(slider_pos)
        if expected_max_age is not None:
            status = "✅" if actual_max_age == expected_max_age else "❌"
            print(f"  {status} {slider_pos:5.1f}% → {actual_max_age:3d} (ожидалось: {expected_max_age})")
        else:
            print(f"  ℹ️  {slider_pos:5.1f}% → {actual_max_age:3d}")
    
    print("\n🔄 Тестирование обратного преобразования max_age → позиция слайдера:")
    test_max_ages = [10, 30, 60, 70, 100, 200, 500]
    for max_age in test_max_ages:
        slider_pos = max_age_value_to_slider(max_age)
        back_to_max_age = max_age_slider_to_value(slider_pos)
        error = abs(back_to_max_age - max_age)
        status = "✅" if error <= 1 else "⚠️" if error <= 3 else "❌"
        print(f"  {status} {max_age:3d} → {slider_pos:5.1f}% → {back_to_max_age:3d} (ошибка: {error})")
    
    print("\n📊 Распределение значений по слайдеру:")
    print("Первая половина слайдера (0-50%): диапазон 10-70")
    for i in range(0, 51, 10):
        max_age = max_age_slider_to_value(i)
        print(f"  {i:2d}% → {max_age:3d}")
    
    print("\nВторая половина слайдера (50-100%): диапазон 70-500")
    for i in range(50, 101, 10):
        max_age = max_age_slider_to_value(i)
        print(f"  {i:2d}% → {max_age:3d}")
    
    print("\n✅ Тест логарифмического слайдера завершен!")

def test_key_breakpoints():
    """Тестирует ключевые точки логарифмического масштабирования"""
    print("\n🎯 Проверка ключевых точек:")
    
    from guitar_life_patched import max_age_slider_to_value
    
    # Проверяем, что первая половина слайдера покрывает 10-70
    first_half_start = max_age_slider_to_value(0.0)
    first_half_end = max_age_slider_to_value(50.0)
    
    print(f"Первая половина: {first_half_start}-{first_half_end}")
    assert first_half_start == 10, f"Начало первой половины должно быть 10, а не {first_half_start}"
    assert first_half_end == 70, f"Конец первой половины должен быть 70, а не {first_half_end}"
    
    # Проверяем, что вторая половина слайдера покрывает 70-500
    second_half_start = max_age_slider_to_value(50.0)
    second_half_end = max_age_slider_to_value(100.0)
    
    print(f"Вторая половина: {second_half_start}-{second_half_end}")
    assert second_half_start == 70, f"Начало второй половины должно быть 70, а не {second_half_start}"
    assert second_half_end == 500, f"Конец второй половины должен быть 500, а не {second_half_end}"
    
    print("✅ Все ключевые точки корректны!")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов логарифмического слайдера Max Age...")
    print("=" * 70)
    
    try:
        test_logarithmic_scaling()
        test_key_breakpoints()
        print("\n🎉 Все тесты логарифмического слайдера пройдены успешно!")
        print("Система готова к использованию с логарифмическим масштабированием.")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()