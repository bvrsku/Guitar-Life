#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивный тест HUD параметров очистки
Запускает GUI и позволяет пользователю протестировать новые элементы управления
"""

import sys
import os
import pygame

# Добавляем путь к модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from guitar_lifeE import App, CLEAR_TYPES
    print("✅ Импорт модуля guitar_lifeeq успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_interactive_hud():
    """Интерактивный тест HUD с новыми параметрами"""
    
    print("🎯 Интерактивный тест HUD параметров очистки")
    print("=" * 60)
    print("Инструкции:")
    print("1. В HUD найдите секцию 'CONTROLS' - там комбобокс 'Mode' для soft_mode")
    print("2. В секции 'ACTIONS' найдите комбобокс 'Clear Type' рядом с кнопкой Clear")
    print("3. Попробуйте изменить эти параметры и нажать кнопку Clear")
    print("4. Нажмите ESC для выхода")
    print("=" * 60)
    
    # Конфигурация для интерактивного теста
    test_config = {
        'layer_count': 3,
        'layers_different': True,
        'tick_ms': 200,  # Медленнее для лучшего наблюдения
        'clear_rms': 0.001,
        'pitch_tick_enable': False,
        'fx': {'trails': True},
        'clear_type': 'Полная очистка',
        'soft_mode': 'Удалять клетки',
        'soft_clear_enable': True,
        'max_cells_percent': 60,
        'soft_clear_threshold': 50,
    }
    
    print(f"📋 Запуск приложения с тестовой конфигурацией...")
    print(f"   - Слоев: {test_config['layer_count']}")
    print(f"   - Начальный тип очистки: {test_config['clear_type']}")
    print(f"   - Начальный режим: {test_config['soft_mode']}")
    
    try:
        app = App(test_config)
        
        # Создаем интересные начальные паттерны
        app.generate_random_patterns()
        initial_cells = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
        print(f"   - Создано начальных клеток: {initial_cells}")
        
        # Проверяем, что элементы управления доступны
        print(f"\n🔍 Проверка доступности элементов управления:")
        
        clear_type_available = 'clear_type' in app.hud.comboboxes
        soft_mode_available = 'soft_mode' in app.hud.comboboxes
        
        print(f"   Clear Type комбобокс: {'✅ Доступен' if clear_type_available else '❌ Недоступен'}")
        print(f"   Soft Mode комбобокс: {'✅ Доступен' if soft_mode_available else '❌ Недоступен'}")
        
        if clear_type_available:
            clear_combo = app.hud.comboboxes['clear_type']
            print(f"   Clear Type опции: {clear_combo.options}")
        
        if soft_mode_available:
            soft_combo = app.hud.comboboxes['soft_mode']
            print(f"   Soft Mode опции: {soft_combo.options}")
        
        print(f"\n🎮 Запуск интерактивного интерфейса...")
        print(f"📌 ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ:")
        print(f"   1. Найдите в правой панели HUD секцию 'CONTROLS'")
        print(f"   2. Найдите комбобокс 'Mode' и попробуйте изменить режим")
        print(f"   3. Найдите в секции 'ACTIONS' комбобокс 'Clear Type'")
        print(f"   4. Попробуйте разные типы очистки с кнопкой 'Clear'")
        print(f"   5. Наблюдайте изменения в популяции клеток")
        print(f"   6. Нажмите ESC для выхода")
        
        # Запускаем приложение
        app.run()
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Тест прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка во время теста: {e}")
    finally:
        pygame.quit()
        print(f"\n✅ Интерактивный тест завершен")

if __name__ == "__main__":
    test_interactive_hud()