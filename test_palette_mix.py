# This file has been deleted.
#!/usr/bin/env python3
"""
Тест для проверки нового слайдера Palette Mix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_life_patched import build_color_image, color_from_age_rms
import numpy as np

def test_palette_mix():
    """Тест нового слайдера баланса палитр"""
    print("🧪 Тестирование слайдера Palette Mix")
    
    # Создаем тестовую сетку
    grid = np.zeros((10, 10), dtype=bool)
    grid[5, 5] = True  # Одна живая клетка
    
    age = np.zeros((10, 10), dtype=int)
    age[5, 5] = 50  # Возраст 50
    
    # Параметры
    rms = 0.8
    pitch = 440.0
    cfg = {
        'rms_strength': 100,
        'fade_start': 80,
        'fade_sat_drop': 70,
        'fade_val_drop': 60,
        'global_v_mul': 1.0,
        'color_rms_min': 0.1,
        'color_rms_max': 1.0
    }
    
    results = {}
    palette_mix_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print(f"\n🎨 Тестируем разные значения Palette Mix:")
    
    for mix_val in palette_mix_values:
        print(f"\n🔧 Palette Mix = {mix_val:.2f}")
        
        # Тест с режимом HSV-дизайны и режимом palette
        img = build_color_image(
            layer_grid=grid, 
            layer_age=age, 
            mode="HSV-дизайны", 
            rms=rms, 
            pitch=pitch, 
            cfg=cfg,
            age_palette="Fire", 
            rms_palette="Ocean", 
            rms_mode="palette",  # Важно: режим palette для смешивания
            blend_mode="normal",
            rms_enabled=True, 
            max_age=120, 
            rms_only=False,
            palette_mix=mix_val
        )
        
        color = img[5, 5]
        results[mix_val] = color
        print(f"   Цвет с mix={mix_val:.2f}: {color}")
        
        # Дополнительный тест через прямой вызов функции
        direct_color = color_from_age_rms(
            age=50, rms=rms, rms_strength=1.0,
            fade_start=80, max_age=120,
            sat_drop_pct=70, val_drop_pct=60,
            color_rms_min=0.1, color_rms_max=1.0,
            global_v_mul=1.0,
            age_palette="Fire", rms_palette="Ocean",
            rms_mode="palette", blend_mode="normal",
            rms_enabled=True, palette_mix=mix_val
        )
        print(f"   Прямой вызов: {direct_color}")
    
    # Анализ результатов
    print(f"\n📊 Анализ градиента:")
    
    # Проверяем, что цвета образуют плавный градиент
    colors_are_different = True
    for i in range(len(palette_mix_values) - 1):
        curr_mix = palette_mix_values[i]
        next_mix = palette_mix_values[i + 1]
        
        curr_color = results[curr_mix]
        next_color = results[next_mix]
        
        # Вычисляем разность цветов
        color_diff = np.linalg.norm(curr_color.astype(float) - next_color.astype(float))
        print(f"   Mix {curr_mix:.2f} → {next_mix:.2f}: разность = {color_diff:.1f}")
        
        if color_diff < 5:  # Слишком маленькая разность
            colors_are_different = False
    
    # Проверяем крайние значения
    only_age_color = results[0.0]   # Только возраст
    only_rms_color = results[1.0]   # Только RMS
    mixed_color = results[0.5]      # 50/50
    
    age_rms_diff = np.linalg.norm(only_age_color.astype(float) - only_rms_color.astype(float))
    
    print(f"\n✅ Результаты проверки:")
    print(f"   Цвета образуют градиент: {'✅' if colors_are_different else '❌'}")
    print(f"   Только возраст (0.0): {only_age_color}")
    print(f"   Смешанный (0.5): {mixed_color}")
    print(f"   Только RMS (1.0): {only_rms_color}")
    print(f"   Разность крайних значений: {age_rms_diff:.1f}")
    
    # Тест успешен, если есть плавный градиент и значительная разность между крайними значениями
    test_passed = colors_are_different and age_rms_diff > 30
    
    return results, test_passed

def test_palette_mix_in_brightness_mode():
    """Тест palette_mix в режиме brightness (должен не влиять)"""
    print("\n🧪 Тестирование Palette Mix в режиме brightness")
    
    # В режиме brightness, palette_mix не должен влиять
    grid = np.zeros((5, 5), dtype=bool)
    grid[2, 2] = True
    age = np.zeros((5, 5), dtype=int)
    age[2, 2] = 30
    
    rms = 0.6
    cfg = {
        'rms_strength': 100,
        'fade_start': 60,
        'fade_sat_drop': 70,
        'fade_val_drop': 60,
        'global_v_mul': 1.0,
        'color_rms_min': 0.1,
        'color_rms_max': 1.0
    }
    
    # Тестируем разные palette_mix в brightness режиме
    color_1 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV-дизайны", rms=rms, pitch=440.0, cfg=cfg,
        age_palette="Fire", rms_palette="Ocean", rms_mode="brightness",  # brightness режим
        blend_mode="normal", rms_enabled=True, max_age=120, rms_only=False,
        palette_mix=0.0  # Не должно влиять
    )[2, 2]
    
    color_2 = build_color_image(
        layer_grid=grid, layer_age=age, mode="HSV-дизайны", rms=rms, pitch=440.0, cfg=cfg,
        age_palette="Fire", rms_palette="Ocean", rms_mode="brightness",  # brightness режим
        blend_mode="normal", rms_enabled=True, max_age=120, rms_only=False,
        palette_mix=1.0  # Не должно влиять
    )[2, 2]
    
    colors_same = np.array_equal(color_1, color_2)
    print(f"   Brightness режим с mix=0.0: {color_1}")
    print(f"   Brightness режим с mix=1.0: {color_2}")
    print(f"   Цвета одинаковы (ожидаем ✅): {'✅' if colors_same else '❌'}")
    
    return colors_same

if __name__ == "__main__":
    print("🎨 Тестирование нового функционала Palette Mix\n")
    
    # Основной тест palette_mix
    results, test1_passed = test_palette_mix()
    
    # Тест в brightness режиме
    test2_passed = test_palette_mix_in_brightness_mode()
    
    # Общий результат
    all_tests_passed = test1_passed and test2_passed
    
    print(f"\n{'🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!' if all_tests_passed else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    
    if test1_passed:
        print("✅ Palette Mix корректно смешивает палитры в режиме palette")
    else:
        print("❌ Проблемы с градиентом Palette Mix")
        
    if test2_passed:
        print("✅ Palette Mix не влияет в режиме brightness (как ожидается)")
    else:
        print("❌ Palette Mix неожиданно влияет в режиме brightness")
    
    print("\n📝 Palette Mix добавлен успешно! Теперь можно контролировать баланс между возрастной и RMS палитрами.")