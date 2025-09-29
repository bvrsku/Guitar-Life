#!/usr/bin/env python3
"""
Диагностика вылетов Guitar Life - пошаговая проверка компонентов
"""

import sys
import traceback

def test_import():
    """Тестирует импорт модуля"""
    try:
        print("🔍 Тестируем импорт модуля...")
        import guitar_li4fe
        print("✅ Модуль guitar_life импортирован")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        traceback.print_exc()
        return False

def test_basic_components():
    """Тестирует основные компоненты"""
    try:
        print("🔍 Тестируем основные компоненты...")
        import guitar_li4fe
        
        # Тестируем Layer
        layer = guitar_li4fe.Layer
        print("✅ Класс Layer доступен")
        
        # Тестируем функции
        step_life = guitar_li4fe.step_life
        build_color_image = guitar_li4fe.build_color_image
        print("✅ Основные функции доступны")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка компонентов: {e}")
        traceback.print_exc()
        return False

def test_numpy_pygame():
    """Тестирует зависимости"""
    try:
        print("🔍 Тестируем зависимости...")
        import numpy as np
        print("✅ NumPy работает")
        
        import pygame
        pygame.init()
        print("✅ Pygame работает")
        
        # Тест создания массива и surface
        arr = np.zeros((10, 10, 4), dtype=np.uint8)
        arr[:, :, 3] = 255  # альфа
        print("✅ Создание RGBA массивов работает")
        
        surf = pygame.surfarray.make_surface(arr[:,:,0])
        print("✅ Pygame surfarray работает")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка зависимостей: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Тестирует загрузку конфигурации"""
    try:
        print("🔍 Тестируем загрузку конфигурации...")
        import json
        
        with open('app_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        layers_config = config.get('layers', {})
        layer_count = layers_config.get('layer_count', 0)
        layer_settings = layers_config.get('layer_settings', [])
        
        print(f"✅ Конфигурация загружена: {layer_count} слоев, {len(layer_settings)} настроек")
        
        if layer_count != len(layer_settings):
            print(f"⚠️  Предупреждение: layer_count ({layer_count}) != len(layer_settings) ({len(layer_settings)})")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚨 Диагностика вылетов Guitar Life")
    print("=" * 50)
    
    tests = [
        ("Импорт модуля", test_import),
        ("Основные компоненты", test_basic_components),
        ("Зависимости", test_numpy_pygame),
        ("Загрузка конфигурации", test_config_loading)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if not test_func():
            failed_tests.append(test_name)
    
    print("\n" + "=" * 50)
    if failed_tests:
        print(f"❌ Неудачные тесты: {', '.join(failed_tests)}")
        print("🔧 Рекомендации:")
        print("   1. Исправьте ошибки выше")
        print("   2. Попробуйте create_safe_config.py")
        print("   3. Проверьте версии pygame/numpy")
    else:
        print("✅ Все тесты прошли!")
        print("🎸 Попробуйте запустить: python.exe guitar_life.py")

if __name__ == "__main__":
    main()