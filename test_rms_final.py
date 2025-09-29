# This file has been deleted.
#!/usr/bin/env python3
"""
Финальный тест для проверки исправленного RMS Only режима
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_life_patched import build_color_image
import numpy as np

def test_rms_only_fixed():
    """Финальный тест RMS Only с различными режимами"""
    print("🧪 Финальный тест исправленного RMS Only режима")
    
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
    
    results = {}
    
    # Тест 1: HSV-дизайны без RMS Only (возраст + RMS)
    print("\n🔧 Тест 1: HSV-дизайны без RMS Only")
    img1 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV-дизайны", rms=rms, pitch=pitch, cfg=cfg,
        age_palette="Fire", rms_palette="Aurora", rms_mode="palette", blend_mode="normal",
        rms_enabled=True, max_age=120, rms_only=False
    )
    results['hsv_normal'] = img1[5, 5]
    print(f"   HSV-дизайны (обычный): {results['hsv_normal']}")
    
    # Тест 2: HSV-дизайны с RMS Only (должен игнорировать возраст)
    print("\n🔧 Тест 2: HSV-дизайны с RMS Only")
    img2 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV-дизайны", rms=rms, pitch=pitch, cfg=cfg,
        age_palette="Fire", rms_palette="Aurora", rms_mode="palette", blend_mode="normal",
        rms_enabled=True, max_age=120, rms_only=True  # ✅ RMS Only
    )
    results['hsv_rms_only'] = img2[5, 5]
    print(f"   HSV-дизайны (RMS Only): {results['hsv_rms_only']}")
    
    # Тест 3: HSV Палитры без RMS Only (чистый RMS)
    print("\n🔧 Тест 3: HSV Палитры без RMS Only")
    img3 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV Палитры", rms=rms, pitch=pitch, cfg=cfg,
        age_palette="Fire", rms_palette="Aurora", rms_mode="palette", blend_mode="normal",
        rms_enabled=True, max_age=120, rms_only=False
    )
    results['hsv_palette_normal'] = img3[5, 5]
    print(f"   HSV Палитры (обычный): {results['hsv_palette_normal']}")
    
    # Тест 4: HSV Палитры с RMS Only (должен быть идентичен тесту 3)
    print("\n🔧 Тест 4: HSV Палитры с RMS Only")
    img4 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV Палитры", rms=rms, pitch=pitch, cfg=cfg,
        age_palette="Fire", rms_palette="Aurora", rms_mode="palette", blend_mode="normal",
        rms_enabled=True, max_age=120, rms_only=True  # ✅ RMS Only
    )
    results['hsv_palette_rms_only'] = img4[5, 5]
    print(f"   HSV Палитры (RMS Only): {results['hsv_palette_rms_only']}")
    
    # Тест 5: Pitch режим с RMS Only (должен игнорировать pitch)
    print("\n🔧 Тест 5: Pitch режим с RMS Only")
    img5 = build_color_image(
        layer_grid=grid, layer_age=age, mode="Высота ноты (Pitch)", rms=rms, pitch=pitch, cfg=cfg,
        age_palette="Fire", rms_palette="Aurora", rms_mode="palette", blend_mode="normal",
        rms_enabled=True, max_age=120, rms_only=True  # ✅ RMS Only
    )
    results['pitch_rms_only'] = img5[5, 5]
    print(f"   Pitch (RMS Only): {results['pitch_rms_only']}")
    
    # Анализ результатов
    print("\n📊 Анализ результатов:")
    
    # Проверка 1: RMS Only должен давать одинаковый цвет для всех режимов
    rms_only_colors = [results['hsv_rms_only'], results['hsv_palette_rms_only'], results['pitch_rms_only']]
    all_rms_same = all(np.array_equal(color, rms_only_colors[0]) for color in rms_only_colors)
    print(f"   ✅ RMS Only дает одинаковый цвет для всех режимов: {'✅' if all_rms_same else '❌'}")
    
    # Проверка 2: HSV-дизайны обычный vs RMS Only должны отличаться
    hsv_different = not np.array_equal(results['hsv_normal'], results['hsv_rms_only'])
    print(f"   ✅ HSV-дизайны: обычный ≠ RMS Only: {'✅' if hsv_different else '❌'}")
    
    if hsv_different:
        diff = np.linalg.norm(results['hsv_normal'].astype(float) - results['hsv_rms_only'].astype(float))
        print(f"      Разница: {diff:.1f} единиц")
    
    # Проверка 3: HSV Палитры обычный и RMS Only должны быть одинаковы (оба используют RMS)
    hsv_palette_same = np.array_equal(results['hsv_palette_normal'], results['hsv_palette_rms_only'])
    print(f"   ✅ HSV Палитры: обычный = RMS Only: {'✅' if hsv_palette_same else '❌'}")
    
    # Проверка 4: Все RMS Only режимы равны чистому RMS режиму
    pure_rms_match = np.array_equal(results['hsv_palette_normal'], results['hsv_rms_only'])
    print(f"   ✅ RMS Only = чистый RMS режим: {'✅' if pure_rms_match else '❌'}")
    
    print(f"\n🎯 Детальные результаты:")
    for key, color in results.items():
        print(f"   {key}: {color}")
    
    # Общий результат
    all_tests_passed = all_rms_same and hsv_different and hsv_palette_same and pure_rms_match
    print(f"\n{'🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!' if all_tests_passed else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    
    return results, all_tests_passed

if __name__ == "__main__":
    results, passed = test_rms_only_fixed()
    if passed:
        print("\n✅ RMS Only режим работает корректно после исправления!")
    else:
        print("\n❌ RMS Only режим требует дополнительных исправлений")