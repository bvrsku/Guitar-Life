# This file has been deleted.
#!/usr/bin/env python3
"""
Тест для отладки проблемы с RMS Only режимом
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_life_patched import build_color_image
import numpy as np

def test_rms_only_switching():
    """Тест переключения RMS Only режима"""
    print("🧪 Тестирование переключения RMS Only режима")
    
    # Создаем тестовую сетку
    grid = np.zeros((10, 10), dtype=bool)
    grid[5, 5] = True  # Одна живая клетка
    
    age = np.zeros((10, 10), dtype=int)
    age[5, 5] = 30  # Возраст 30
    
    # Параметры
    rms = 0.7
    pitch = 440.0
    cfg = {
        'rms_strength': 100,
        'fade_start': 60,
        'fade_sat_drop': 70,
        'fade_val_drop': 60,
        'global_v_mul': 1.0,
        'color_rms_min': 0.1,
        'color_rms_max': 1.0
    }
    
    # Тест 1: Обычный режим "HSV-дизайны" (должен использовать возраст + RMS)
    print("\n🔧 Тест 1: Обычный режим 'HSV-дизайны' (rms_only=False)")
    img_normal = build_color_image(
        layer_grid=grid,
        layer_age=age,
        mode="HSV-дизайны",  # Возраст + RMS
        rms=rms,
        pitch=pitch,
        cfg=cfg,
        age_palette="Fire",
        rms_palette="Aurora",
        rms_mode="palette",
        blend_mode="normal",
        rms_enabled=True,
        max_age=120,
        rms_only=False  # ❌ ВЫКЛЮЧЕН
    )
    color_normal = img_normal[5, 5]
    print(f"   Цвет без RMS Only: {color_normal}")
    
    # Тест 2: RMS Only режим с другим базовым режимом
    print("\n🔧 Тест 2: RMS Only режим с 'HSV-дизайны' (rms_only=True)")
    img_rms_only = build_color_image(
        layer_grid=grid,
        layer_age=age,
        mode="HSV-дизайны",  # ❗ Другой режим, но RMS Only должен его переопределить
        rms=rms,
        pitch=pitch,
        cfg=cfg,
        age_palette="Fire",
        rms_palette="Aurora",
        rms_mode="palette",
        blend_mode="normal",
        rms_enabled=True,
        max_age=120,
        rms_only=True  # ✅ ВКЛЮЧЕН
    )
    color_rms_only = img_rms_only[5, 5]
    print(f"   Цвет с RMS Only: {color_rms_only}")
    
    # Тест 3: Другой режим с RMS Only
    print("\n🔧 Тест 3: Режим 'HSV-дизайны' с RMS Only (должен игнорироваться)")
    img_age_rms_only = build_color_image(
        layer_grid=grid,
        layer_age=age,
        mode="HSV-дизайны",  # Обычно возраст + RMS
        rms=rms,
        pitch=pitch,
        cfg=cfg,
        age_palette="Fire",
        rms_palette="Aurora",
        rms_mode="palette",
        blend_mode="normal",
        rms_enabled=True,
        max_age=120,
        rms_only=True  # ✅ ВКЛЮЧЕН - должен принудительно использовать только RMS
    )
    color_age_rms_only = img_age_rms_only[5, 5]
    print(f"   Цвет HSV-дизайны с RMS Only: {color_age_rms_only}")
    
    # Анализ результатов
    print("\n📊 Анализ результатов:")
    
    # Проверяем, что RMS Only дает одинаковый результат независимо от режима
    rms_colors_match = np.array_equal(color_rms_only, color_age_rms_only)
    print(f"   RMS Only цвета одинаковы для разных режимов: {'✅' if rms_colors_match else '❌'}")
    
    # Проверяем, что RMS Only отличается от обычного режима
    colors_different = not np.array_equal(color_normal, color_rms_only)
    print(f"   RMS Only отличается от обычного режима: {'✅' if colors_different else '❌'}")
    
    if colors_different:
        color_diff = np.linalg.norm(color_normal.astype(float) - color_rms_only.astype(float))
        print(f"   Разница в цветах: {color_diff:.1f} единиц")
    
    # Проверяем, что обычный режим не равен нулю
    normal_non_zero = not np.array_equal(color_normal, [0, 0, 0])
    rms_only_non_zero = not np.array_equal(color_rms_only, [0, 0, 0])
    
    print(f"   Обычный режим не черный: {'✅' if normal_non_zero else '❌'}")
    print(f"   RMS Only не черный: {'✅' if rms_only_non_zero else '❌'}")
    
    return {
        'normal': color_normal,
        'rms_only': color_rms_only,
        'age_rms_only': color_age_rms_only,
        'rms_colors_match': rms_colors_match,
        'colors_different': colors_different
    }

if __name__ == "__main__":
    results = test_rms_only_switching()
    
    if results['rms_colors_match'] and results['colors_different']:
        print("\n🎉 Тест ПРОЙДЕН: RMS Only режим работает корректно!")
    else:
        print("\n❌ Тест ПРОВАЛЕН: Есть проблемы с RMS Only режимом")
        
    print(f"\nРезультаты:")
    print(f"  Обычный: {results['normal']}")
    print(f"  RMS Only: {results['rms_only']}")
    print(f"  HSV+RMS Only: {results['age_rms_only']}")