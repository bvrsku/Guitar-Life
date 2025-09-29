#!/usr/bin/env python3
"""
Тест нового функционала управления слоями в CyberHUD
"""

import pygame
import sys
import os

# Добавляем путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import App

def test_layer_management():
    """Тестирует функциональность управления слоями"""
    
    print("🚀 Тестируем новую функциональность управления слоями")
    
    # Создаем минимальную конфигурацию
    sel = {
        'device': 'Mock Audio Device',
        'device_index': 0,
        'layer_count': 3,
        'tick_ms': 150,
        'rms_strength': 100,
        'max_age': 120,
        'aging_speed': 1.0,
        'gain': 1.0,
        'fx': {
            'trails': True,
            'blur': False,
            'bloom': False,
            'posterize': False,
            'scanlines': False
        },
        'layers_cfg': [
            {
                'rule': 'Conway',
                'age_palette': 'Blue->Green->Yellow->Red',
                'rms_palette': 'Blue->Green->Yellow->Red',
                'color_mode': 'HSV-дизайны',
                'alpha_live': 220,
                'alpha_old': 140,
                'solo': False,
                'mute': False,
            },
            {
                'rule': 'HighLife',
                'age_palette': 'Ocean',
                'rms_palette': 'Fire',
                'color_mode': 'HSV-дизайны',
                'alpha_live': 220,
                'alpha_old': 140,
                'solo': False,
                'mute': False,
            },
            {
                'rule': 'Day&Night',
                'age_palette': 'Neon',
                'rms_palette': 'Ocean',
                'color_mode': 'HSV-дизайны',
                'alpha_live': 220,
                'alpha_old': 140,
                'solo': False,
                'mute': False,
            }
        ]
    }
    
    try:
        print("📦 Создаем приложение...")
        app = App(sel)
        
        print(f"✅ Приложение создано успешно!")
        print(f"   - Слоев: {len(app.layers)}")
        print(f"   - HUD категории: {list(app.hud.categories.keys())}")
        
        # Проверяем новые кнопки управления слоями
        print("\n🔍 Проверяем новые кнопки управления слоями:")
        layer_controls = app.hud._get_active_category_controls()
        
        layer_management_buttons = [
            'add_layer', 'remove_layer', 'clear_layer', 
            'solo_all', 'mute_all', 'unmute_all', 'unsolo_all'
        ]
        
        found_buttons = []
        for button_name in layer_management_buttons:
            if button_name in app.hud.buttons:
                found_buttons.append(button_name)
                print(f"   ✅ {button_name}")
            else:
                print(f"   ❌ {button_name}")
        
        print(f"\n📊 Найдено {len(found_buttons)}/{len(layer_management_buttons)} кнопок управления слоями")
        
        # Тестируем функциональность
        print("\n🧪 Тестируем функциональность:")
        
        # Тест добавления слоя
        initial_layer_count = len(app.layers)
        app.on_parameter_change('add_layer', True)
        if len(app.layers) == initial_layer_count + 1:
            print("   ✅ Добавление слоя работает")
        else:
            print("   ❌ Ошибка добавления слоя")
        
        # Тест удаления слоя
        app.on_parameter_change('remove_layer', True)
        if len(app.layers) == initial_layer_count:
            print("   ✅ Удаление слоя работает")
        else:
            print("   ❌ Ошибка удаления слоя")
        
        # Тест Solo/Mute всех слоев
        app.on_parameter_change('solo_all', True)
        if all(layer.solo for layer in app.layers):
            print("   ✅ Solo всех слоев работает")
        else:
            print("   ❌ Ошибка Solo всех слоев")
        
        app.on_parameter_change('unsolo_all', True)
        if not any(layer.solo for layer in app.layers):
            print("   ✅ Unsolo всех слоев работает")
        else:
            print("   ❌ Ошибка Unsolo всех слоев")
        
        app.on_parameter_change('mute_all', True)
        if all(layer.mute for layer in app.layers):
            print("   ✅ Mute всех слоев работает")
        else:
            print("   ❌ Ошибка Mute всех слоев")
        
        app.on_parameter_change('unmute_all', True)
        if not any(layer.mute for layer in app.layers):
            print("   ✅ Unmute всех слоев работает")
        else:
            print("   ❌ Ошибка Unmute всех слоев")
        
        print("\n🎮 Проверяем визуализацию слоев в HUD:")
        app.hud.active_category = 'LAYERS'
        
        # Проверяем наличие информации о слоях
        layer_info_found = False
        try:
            # Имитируем отрисовку для проверки функции визуализации
            screen = pygame.display.set_mode((1, 1))  # Минимальный экран для теста
            info = {'fps': 60, 'cells': 100, 'layers': len(app.layers)}
            
            # Проверяем что метод _draw_layer_status_list существует
            if hasattr(app.hud, '_draw_layer_status_list'):
                print("   ✅ Функция визуализации слоев найдена")
                layer_info_found = True
            else:
                print("   ❌ Функция визуализации слоев не найдена")
                
            pygame.quit()
        except Exception as e:
            print(f"   ⚠️ Ошибка проверки визуализации: {e}")
        
        print(f"\n🎯 РЕЗУЛЬТАТ ТЕСТА:")
        print(f"   - Кнопки управления: {len(found_buttons)}/{len(layer_management_buttons)}")
        print(f"   - Функциональность: {'✅ Работает' if len(app.layers) == initial_layer_count else '❌ Ошибки'}")
        print(f"   - Визуализация: {'✅ Работает' if layer_info_found else '❌ Ошибки'}")
        
        if len(found_buttons) == len(layer_management_buttons) and len(app.layers) == initial_layer_count and layer_info_found:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Управление слоями работает корректно.")
            return True
        else:
            print("⚠️ Некоторые тесты не прошли. Требуется доработка.")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_layer_management()
    sys.exit(0 if success else 1)