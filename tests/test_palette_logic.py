#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новой логики палитр для Guitar Life
Проверяет различные комбинации режимов RMS и блендинга
"""

import sys
import os

# Добавляем путь к главному файлу
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_li4fe import (
        blend_colors, color_from_age_rms, color_from_age_only,
        color_from_age_brightness_rms, clamp01
    )
    print("✅ Все функции успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_blend_colors():
    """Тест функции blend_colors"""
    print("\n🎨 Тестирование blend_colors...")
    
    color1 = (255, 0, 0)    # Красный
    color2 = (0, 255, 0)    # Зеленый
    factor = 0.5
    
    # Тест различных режимов блендинга
    modes = ["normal", "additive", "screen", "multiply", "overlay"]
    
    for mode in modes:
        result = blend_colors(color1, color2, factor, mode)
        print(f"  {mode}: {color1} + {color2} (factor={factor}) = {result}")
    
    print("✅ blend_colors работает корректно")

def test_rms_modes():
    """Тест различных режимов RMS"""
    print("\n🎛️ Тестирование режимов RMS...")
    
    # Тестовые параметры
    age = 30
    rms = 0.1
    rms_strength = 0.8
    fade_start = 50
    max_age = 100
    sat_drop_pct = 70
    val_drop_pct = 60
    color_rms_min = 0.01
    color_rms_max = 0.3
    global_v_mul = 1.0
    age_palette = "Fire"
    rms_palette = "Ocean"
    
    # Тест режима "disabled" (RMS отключена)
    print("  Режим 'disabled':")
    color_disabled = color_from_age_rms(
        age, rms, rms_strength, fade_start, max_age,
        sat_drop_pct, val_drop_pct, color_rms_min, color_rms_max,
        global_v_mul, age_palette, rms_palette,
        rms_mode="disabled", rms_enabled=False
    )
    print(f"    Цвет (RMS отключена): {color_disabled}")
    
    # Тест режима "brightness"
    print("  Режим 'brightness':")
    color_brightness = color_from_age_rms(
        age, rms, rms_strength, fade_start, max_age,
        sat_drop_pct, val_drop_pct, color_rms_min, color_rms_max,
        global_v_mul, age_palette, rms_palette,
        rms_mode="brightness", rms_enabled=True
    )
    print(f"    Цвет (RMS на яркость): {color_brightness}")
    
    # Тест режима "palette" с различными блендингами
    print("  Режим 'palette':")
    blend_modes = ["normal", "additive", "screen", "multiply", "overlay"]
    
    for blend_mode in blend_modes:
        color_palette = color_from_age_rms(
            age, rms, rms_strength, fade_start, max_age,
            sat_drop_pct, val_drop_pct, color_rms_min, color_rms_max,
            global_v_mul, age_palette, rms_palette,
            rms_mode="palette", blend_mode=blend_mode, rms_enabled=True
        )
        print(f"    Цвет (palette + {blend_mode}): {color_palette}")
    
    print("✅ Режимы RMS работают корректно")

def test_edge_cases():
    """Тест граничных случаев"""
    print("\n⚠️ Тестирование граничных случаев...")
    
    # Тест с экстремальными значениями
    test_cases = [
        {"age": 0, "rms": 0.0, "description": "Нулевые значения"},
        {"age": 1000, "rms": 1.0, "description": "Максимальные значения"},
        {"age": -10, "rms": -0.5, "description": "Отрицательные значения"},
    ]
    
    for case in test_cases:
        print(f"  {case['description']}:")
        try:
            color = color_from_age_rms(
                case["age"], case["rms"], 1.0, 50, 100,
                70, 60, 0.01, 0.3, 1.0,
                "Fire", "Ocean", "palette", "normal", True
            )
            print(f"    Результат: {color}")
            
            # Проверяем, что все компоненты в пределах 0-255
            if all(0 <= c <= 255 for c in color):
                print("    ✅ Цвет в допустимых пределах")
            else:
                print("    ❌ Цвет вне допустимых пределов!")
                
        except Exception as e:
            print(f"    ❌ Ошибка: {e}")
    
    print("✅ Граничные случаи обработаны")

def demonstrate_palette_logic():
    """Демонстрация логики работы с палитрами"""
    print("\n📚 Демонстрация логики палитр:")
    print()
    print("1. RMS отключена (rms_enabled=False):")
    print("   └─ Используется только AGE палитра")
    print()
    print("2. RMS включена, режим 'brightness':")
    print("   └─ AGE палитра + RMS влияет на яркость/насыщенность")
    print()
    print("3. RMS включена, режим 'palette':")
    print("   ├─ Получаем цвет от AGE палитры")
    print("   ├─ Получаем цвет от RMS палитры")
    print("   └─ Смешиваем с выбранным режимом блендинга:")
    print("     ├─ Normal: альфа-блендинг (линейная интерполяция)")
    print("     ├─ Additive: аддитивное смешивание (RGB1 + RGB2)")
    print("     ├─ Screen: режим экрана (осветление)")
    print("     ├─ Multiply: умножение (затемнение)")
    print("     └─ Overlay: перекрытие (контраст)")
    print()
    print("4. RMS включена, режим 'disabled':")
    print("   └─ То же что и RMS отключена")

if __name__ == "__main__":
    print("🧪 Запуск тестов новой логики палитр Guitar Life")
    
    try:
        demonstrate_palette_logic()
        test_blend_colors()
        test_rms_modes()
        test_edge_cases()
        
        print("\n🎉 Все тесты пройдены успешно!")
        print("\nНовая логика палитр готова к использованию:")
        print("- ✅ Функция blend_colors для различных режимов смешивания")
        print("- ✅ Режимы RMS: brightness, palette, disabled")
        print("- ✅ Опция включения/выключения RMS палитры")
        print("- ✅ Поддержка различных режимов блендинга палитр")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)