#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест применения палитр в Guitar Life
"""

import sys
import os

# Добавляем путь к главному файлу
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_lifeE import (
        color_from_age_rms, color_from_age_only, build_color_image,
        Layer, DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX
    )
    import numpy as np
    print("✅ Успешно импортированы функции из guitar_lifeeq.py")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_palette_application():
    """Тест применения палитр"""
    print("\n🎨 Тестирование применения палитр...")
    
    # Создаем тестовые данные
    age = 50
    rms = 0.15
    rms_strength = 0.8
    age_palette = "Fire"
    rms_palette = "Ocean"
    
    # Тестируем разные режимы
    print(f"  Параметры: age={age}, rms={rms}, age_palette='{age_palette}', rms_palette='{rms_palette}'")
    
    # 1. Режим "disabled"
    color1 = color_from_age_rms(
        age, rms, rms_strength, 50, 100, 70, 60,
        DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX, 1.0,
        age_palette, rms_palette,
        rms_mode="disabled", rms_enabled=False
    )
    print(f"  RMS отключена: {color1}")
    
    # 2. Режим "brightness"
    color2 = color_from_age_rms(
        age, rms, rms_strength, 50, 100, 70, 60,
        DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX, 1.0,
        age_palette, rms_palette,
        rms_mode="brightness", rms_enabled=True
    )
    print(f"  RMS brightness: {color2}")
    
    # 3. Режим "palette" с разными блендингами
    blend_modes = ["normal", "additive", "screen"]
    for blend_mode in blend_modes:
        color3 = color_from_age_rms(
            age, rms, rms_strength, 50, 100, 70, 60,
            DEFAULT_COLOR_RMS_MIN, DEFAULT_COLOR_RMS_MAX, 1.0,
            age_palette, rms_palette,
            rms_mode="palette", blend_mode=blend_mode, rms_enabled=True
        )
        print(f"  RMS palette ({blend_mode}): {color3}")
    
    # Проверяем, что цвета действительно разные
    colors = [color1, color2]
    unique_colors = set(colors)
    if len(unique_colors) > 1:
        print("  ✅ Палитры применяются по-разному для разных режимов")
    else:
        print("  ❌ Все цвета одинаковые - палитры не применяются!")
    
def test_layer_creation():
    """Тест создания слоя с новыми параметрами"""
    print("\n🔧 Тестирование создания слоя...")
    
    # Создаем тестовую сетку
    grid = np.zeros((10, 10), dtype=bool)
    age = np.zeros((10, 10), dtype=np.int32)
    
    # Добавляем несколько живых клеток
    grid[5, 5] = True
    age[5, 5] = 30
    
    # Создаем слой с новыми параметрами
    layer = Layer(
        grid=grid,
        age=age,
        rule="Conway",
        age_palette="Fire",
        rms_palette="Ocean",
        color_mode="HSV-дизайны",
        rms_mode="palette",
        blend_mode="additive",
        rms_enabled=True,
        alpha_live=220,
        alpha_old=140,
        mix="Normal",
        solo=False,
        mute=False
    )
    
    print(f"  Слой создан:")
    print(f"    RMS режим: {layer.rms_mode}")
    print(f"    Блендинг: {layer.blend_mode}")
    print(f"    RMS включена: {layer.rms_enabled}")
    print(f"    AGE палитра: {layer.age_palette}")
    print(f"    RMS палитра: {layer.rms_palette}")
    
    # Тестируем генерацию изображения
    cfg = {
        'rms_strength': 80,
        'fade_start': 50,
        'max_age': 100,
        'fade_sat_drop': 70,
        'fade_val_drop': 60,
        'global_v_mul': 1.0,
        'color_rms_min': DEFAULT_COLOR_RMS_MIN,
        'color_rms_max': DEFAULT_COLOR_RMS_MAX,
    }
    
    try:
        img = build_color_image(
            layer.grid, layer.age, layer.color_mode,
            0.1, 440.0, cfg,
            layer.age_palette, layer.rms_palette,
            layer.rms_mode, layer.blend_mode, layer.rms_enabled
        )
        print(f"  ✅ Изображение сгенерировано: {img.shape}")
        
        # Проверяем, что в живой клетке есть цвет
        live_color = img[5, 5]
        if any(c > 0 for c in live_color):
            print(f"    Цвет живой клетки: {live_color}")
            print("    ✅ Палитра применилась!")
        else:
            print("    ❌ Живая клетка черная - палитра не применилась!")
            
    except Exception as e:
        print(f"  ❌ Ошибка генерации изображения: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Быстрый тест применения палитр")
    
    try:
        test_palette_application()
        test_layer_creation()
        
        print("\n🎉 Тестирование завершено!")
        print("\nЕсли видите ✅ - палитры работают корректно")
        print("Если видите ❌ - есть проблемы с применением палитр")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)