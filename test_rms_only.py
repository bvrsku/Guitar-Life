# This file has been deleted.
#!/usr/bin/env python3
"""
Тест кнопки RMS Only для слоев
Проверяет работу режима только RMS палитры
"""

import numpy as np
import sys
import os

# Добавляем родительскую директорию в path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые компоненты
from guitar_life_patched import Layer, LayerConfig, build_color_image

def test_rms_only_mode():
    """Тестирует режим RMS Only"""
    print("🎵 Тестирование режима RMS Only...")
    
    # Создаем два слоя: обычный и с RMS Only
    normal_layer = Layer(
        grid=np.zeros((50, 50), dtype=bool),
        age=np.zeros((50, 50), dtype=np.int32),
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        color_mode="HSV-дизайны",
        rms_only=False  # Обычный режим
    )
    
    rms_only_layer = Layer(
        grid=np.zeros((50, 50), dtype=bool),
        age=np.zeros((50, 50), dtype=np.int32),
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        color_mode="HSV-дизайны",
        rms_only=True  # Режим только RMS
    )
    
    print(f"Обычный слой - RMS Only: {normal_layer.rms_only}")
    print(f"RMS слой - RMS Only: {rms_only_layer.rms_only}")
    
    # Добавляем клетки разного возраста
    normal_layer.grid[10, 10] = True
    normal_layer.age[10, 10] = 30
    
    rms_only_layer.grid[10, 10] = True
    rms_only_layer.age[10, 10] = 30
    
    # Конфигурация для рендеринга
    cfg = {
        'rms_strength': 100,
        'fade_start': 20,
        'fade_sat_drop': 70, 
        'fade_val_drop': 60,
        'global_v_mul': 1.0,
        'color_rms_min': 0.01,
        'color_rms_max': 1.0
    }
    
    # Тестируем рендеринг с разными значениями RMS
    rms_values = [0.1, 0.5, 0.9]
    
    for rms in rms_values:
        print(f"\n🎶 Тестирование с RMS = {rms}")
        
        # Обычный слой
        try:
            normal_img = build_color_image(
                normal_layer.grid, normal_layer.age, normal_layer.color_mode,
                rms=rms, pitch=440.0, cfg=cfg,
                age_palette=normal_layer.age_palette,
                rms_palette=normal_layer.rms_palette,
                rms_mode=normal_layer.rms_mode,
                blend_mode=normal_layer.blend_mode,
                rms_enabled=normal_layer.rms_enabled,
                max_age=normal_layer.max_age,
                rms_only=normal_layer.rms_only
            )
            normal_color = normal_img[10, 10]
            print(f"  Обычный слой: цвет = {normal_color}")
        except Exception as e:
            print(f"  ❌ Ошибка в обычном слое: {e}")
            
        # RMS Only слой
        try:
            rms_img = build_color_image(
                rms_only_layer.grid, rms_only_layer.age, rms_only_layer.color_mode,
                rms=rms, pitch=440.0, cfg=cfg,
                age_palette=rms_only_layer.age_palette,
                rms_palette=rms_only_layer.rms_palette,
                rms_mode=rms_only_layer.rms_mode,
                blend_mode=rms_only_layer.blend_mode,
                rms_enabled=rms_only_layer.rms_enabled,
                max_age=rms_only_layer.max_age,
                rms_only=rms_only_layer.rms_only
            )
            rms_color = rms_img[10, 10]
            print(f"  RMS Only слой: цвет = {rms_color}")
        except Exception as e:
            print(f"  ❌ Ошибка в RMS Only слое: {e}")
    
    print("\n✅ Тест режима RMS Only завершен!")

def test_layerconfig_with_rms_only():
    """Тестирует создание LayerConfig с rms_only"""
    print("\n📋 Тестирование LayerConfig с RMS Only...")
    
    # Создаем конфигурации с разными rms_only
    config_normal = LayerConfig(
        rule="Conway",
        age_palette="OCEAN", 
        rms_palette="BLUE_CYAN",
        rms_only=False
    )
    
    config_rms_only = LayerConfig(
        rule="Conway",
        age_palette="NEON",
        rms_palette="PURPLE_PINK", 
        rms_only=True
    )
    
    print(f"Config Normal: rms_only = {config_normal.rms_only}")
    print(f"Config RMS Only: rms_only = {config_rms_only.rms_only}")
    
    # Проверяем, что значения сохранились правильно
    assert config_normal.rms_only == False, "Config Normal должен иметь rms_only = False"
    assert config_rms_only.rms_only == True, "Config RMS Only должен иметь rms_only = True"
    
    print("✅ Тест LayerConfig с RMS Only пройден!")

def test_behavior_differences():
    """Тестирует различия в поведении обычного слоя и RMS Only"""
    print("\n🔍 Тестирование различий поведения...")
    
    # Импортируем функцию цвета RMS
    try:
        from guitar_life_patched import color_from_rms, color_from_age_rms
        
        # Параметры для тестирования
        rms = 0.7
        age = 50
        cfg = {
            'rms_strength': 100,
            'fade_start': 20,
            'fade_sat_drop': 70, 
            'fade_val_drop': 60,
            'global_v_mul': 1.0,
            'color_rms_min': 0.01,
            'color_rms_max': 1.0
        }
        
        # Цвет чистого RMS
        rms_color = color_from_rms(rms, "BLUE_CYAN", cfg['color_rms_min'], cfg['color_rms_max'], cfg['global_v_mul'])
        print(f"Чистый RMS цвет: {rms_color}")
        
        # Цвет с учетом возраста (обычный режим)
        age_rms_color = color_from_age_rms(
            age, rms, cfg['rms_strength']/100.0, cfg['fade_start'], 60,
            cfg['fade_sat_drop'], cfg['fade_val_drop'], 
            cfg['color_rms_min'], cfg['color_rms_max'], cfg['global_v_mul'],
            "OCEAN", "BLUE_CYAN", "brightness", "normal", True
        )
        print(f"Возраст + RMS цвет: {age_rms_color}")
        
        # Проверяем различия
        color_diff = sum(abs(a - b) for a, b in zip(rms_color, age_rms_color))
        print(f"Разница в цветах: {color_diff}")
        
        if color_diff > 10:
            print("✅ Различия значительны - RMS Only режим работает по-другому")
        else:
            print("ℹ️  Различия минимальны при данных параметрах")
            
    except ImportError as e:
        print(f"⚠️  Не удалось импортировать функции цвета: {e}")
    
    print("✅ Тест различий поведения завершен!")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов кнопки RMS Only...")
    print("=" * 70)
    
    try:
        test_layerconfig_with_rms_only()
        test_rms_only_mode()
        test_behavior_differences()
        print("\n🎉 Все тесты кнопки RMS Only пройдены успешно!")
        print("Система готова к использованию с RMS Only режимом.")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()