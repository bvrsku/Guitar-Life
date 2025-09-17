#!/usr/bin/env python3
"""
Упрощенный тест создания App с базовой конфигурацией
"""

import os
import sys
import numpy as np

# Убеждаемся что мы в правильной директории
os.chdir(r'c:\REPOS\Guitar-Life')

# Импортируем необходимые модули
import guitar_life
from guitar_life import App, Layer

def create_minimal_config():
    """Создает минимальную конфигурацию для тестирования"""
    return {
        'device': 'test',
        'device_index': 0,
        'layer_count': 1,
        'layers_cfg': [{
            'rule': 'Conway',
            'age_palette': 'Fire',
            'rms_palette': 'Fire',
            'color_mode': 'Возраст + RMS',
            'alpha_live': 255,
            'alpha_old': 128,
            'mix': 'Normal',
            'solo': False,
            'mute': False,
        }],
        'fx': {},
        'layers_different': True,
        'tick_ms': 100,
        'pitch_tick_enable': False,
        'pitch_tick_min_ms': 50,
        'pitch_tick_max_ms': 500,
        'max_age': 120,
        'fade_start': 60,
        'fade_sat_drop': 70,
        'fade_val_drop': 60,
        'color_rms_min': 0.004,
        'color_rms_max': 0.3,
        'rms_strength': 100,
        'soft_clear_enable': True,
        'soft_mode': 'Удалять клетки',
    }

def test_app_creation():
    """Тестирует создание приложения"""
    
    print("🧪 Тест создания App с минимальной конфигурацией")
    print("=" * 50)
    
    try:
        # Создаем конфигурацию
        config = create_minimal_config()
        print("✅ Конфигурация создана")
        
        # Создаем приложение
        print("Создание App...")
        app = App(config)
        print(f"✅ App создан с {len(app.layers)} слоями")
        
        # Проверяем начальные настройки слоев
        print("\n🔍 Проверка слоев:")
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            print(f"  Слой {i}: {cells} клеток, solo={layer.solo}, mute={layer.mute}")
            print(f"    Правило: {layer.rule}, Age: {layer.age_palette}, RMS: {layer.rms_palette}")
        
        # Создаем тестовый паттерн
        print("\n📝 Создание тестового паттерна...")
        app.create_test_pattern()
        
        # Проверяем результат
        print("🎯 После создания тестового паттерна:")
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            print(f"  Слой {i}: {cells} клеток")
        
        # Тестируем рендеринг
        print("\n🎨 Тест рендеринга...")
        app.render(0.1, 440.0)
        print("✅ Рендеринг выполнен успешно!")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("Если клетки всё равно не видны в GUI, проблема в:")
        print("  1. Функции blit_layer")
        print("  2. Масштабировании изображения")
        print("  3. Pygame отображении")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_creation()
    input("\nНажмите Enter для завершения...")