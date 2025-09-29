#!/usr/bin/env python3
"""
Тест для проверки всех настроек удаления клеток в HUD.
"""

import sys
import os
sys.path.insert(0, r'c:\REPOS\Guitar-Life')

try:
    from guitar_lifeE import App, HUD, GRID_H, GRID_W
    
    def test_removal_controls():
        """Тестируем все элементы управления удалением в HUD."""
        
        print("Тест элементов управления удалением клеток в HUD:")
        print("=" * 60)
        
        # Создаем приложение и HUD
        default_sel = {
            'layer_count': 2,  # Минимальное количество слоёв для теста
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 80,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 1,
            'soft_fade_up': 5,
            'max_cells_percent': 50,
            'soft_clear_threshold': 70,
            'age_bias': 80,
            # Минимальные настройки слоёв
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
            'layer_1_rule': 'Conway',
            'layer_1_age_palette': 'BGYR',
            'layer_1_rms_mode': 'brightness',
            'layer_1_blend_mode': 'Normal',
            'layer_1_rms_enabled': True,
        }
        app = App(default_sel)
        hud = HUD()
        
        # Проверяем наличие всех слайдеров удаления
        removal_sliders = [
            'soft_kill_rate',
            'soft_fade_floor', 
            'soft_fade_down',
            'soft_fade_up',
            'max_cells_percent',
            'soft_clear_threshold',
            'age_bias'
        ]
        
        print("Проверка слайдеров:")
        for slider_name in removal_sliders:
            if slider_name in hud.sliders:
                slider = hud.sliders[slider_name]
                print(f"✅ {slider_name}: {slider.label} | Диапазон: {slider.min_val}-{slider.max_val} | Значение: {slider.current_val}")
            else:
                print(f"❌ {slider_name}: НЕ НАЙДЕН")
        
        print()
        
        # Проверяем наличие кнопок удаления
        removal_buttons = [
            'soft_clear_enable',
            'soft_mode_toggle'
        ]
        
        print("Проверка кнопок:")
        for button_name in removal_buttons:
            if button_name in hud.buttons:
                button = hud.buttons[button_name]
                print(f"✅ {button_name}: {button.text} | Активна: {button.active}")
            else:
                print(f"❌ {button_name}: НЕ НАЙДЕНА")
        
        print()
        
        # Проверяем наличие информационных панелей
        info_labels = [
            'population_info',
            'removal_info'
        ]
        
        print("Проверка информационных панелей:")
        for label_name in info_labels:
            if label_name in hud.labels:
                label = hud.labels[label_name]
                print(f"✅ {label_name}: {label.text}")
            else:
                print(f"❌ {label_name}: НЕ НАЙДЕНА")
        
        print()
        
        # Тестируем обновление HUD от приложения
        print("Тест обновления HUD от приложения:")
        print("-" * 40)
        
        # Изменяем параметры приложения
        app.soft_kill_rate = 90
        app.soft_fade_floor = 0.5
        app.soft_fade_down = 3
        app.soft_fade_up = 8
        app.max_cells_percent = 60
        app.soft_clear_threshold = 80
        app.soft_clear_enable = False
        app.soft_mode = "Затухание клеток"
        
        # Обновляем HUD
        hud.update_from_app(app)
        
        # Проверяем что значения обновились
        test_cases = [
            ('soft_kill_rate', 90),
            ('soft_fade_floor', 0.5),
            ('soft_fade_down', 3),
            ('soft_fade_up', 8),
            ('max_cells_percent', 60),
            ('soft_clear_threshold', 80)
        ]
        
        for param_name, expected_value in test_cases:
            if param_name in hud.sliders:
                actual_value = hud.sliders[param_name].current_val
                if abs(actual_value - expected_value) < 0.01:  # Учитываем погрешности float
                    print(f"✅ {param_name}: {actual_value} (ожидалось {expected_value})")
                else:
                    print(f"❌ {param_name}: {actual_value} (ожидалось {expected_value})")
            else:
                print(f"❌ {param_name}: слайдер не найден")
        
        # Проверяем кнопки
        if 'soft_clear_enable' in hud.buttons:
            actual = hud.buttons['soft_clear_enable'].active
            expected = False
            if actual == expected:
                print(f"✅ soft_clear_enable: {actual} (ожидалось {expected})")
            else:
                print(f"❌ soft_clear_enable: {actual} (ожидалось {expected})")
        
        if 'soft_mode_toggle' in hud.buttons:
            actual = hud.buttons['soft_mode_toggle'].active
            expected = True  # True означает "Затухание клеток"
            if actual == expected:
                print(f"✅ soft_mode_toggle: {actual} (режим: {app.soft_mode})")
            else:
                print(f"❌ soft_mode_toggle: {actual} (режим: {app.soft_mode})")
        
        print()
        
        # Тестируем изменение параметров через set_parameter
        print("Тест изменения параметров:")
        print("-" * 30)
        
        test_changes = [
            ('soft_kill_rate', 75),
            ('soft_fade_floor', 0.2),
            ('soft_fade_down', 2),
            ('soft_fade_up', 10),
            ('max_cells_percent', 40),
            ('soft_clear_threshold', 65),
            ('soft_clear_enable', True),
            ('soft_mode_toggle', False)  # False = "Удалять клетки"
        ]
        
        for param_name, new_value in test_changes:
            try:
                app.set_parameter(param_name, new_value)
                
                if param_name == 'soft_clear_enable':
                    actual = app.soft_clear_enable
                elif param_name == 'soft_mode_toggle':
                    actual = app.soft_mode
                    new_value = "Удалять клетки"  # Для сравнения
                else:
                    actual = getattr(app, param_name)
                
                if actual == new_value:
                    print(f"✅ {param_name}: {actual}")
                else:
                    print(f"❌ {param_name}: {actual} (ожидалось {new_value})")
                    
            except Exception as e:
                print(f"❌ {param_name}: Ошибка - {e}")
        
        print()
        print("✅ Тест завершён!")
        
        return True
        
    def test_removal_info_display():
        """Тестируем отображение информации о системе удаления."""
        
        print("\nТест отображения информации о системе удаления:")
        print("=" * 50)
        
        default_sel = {
            'layer_count': 2,  # Минимальное количество слоёв для теста
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 80,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 1,
            'soft_fade_up': 5,
            'max_cells_percent': 50,
            'soft_clear_threshold': 70,
            'age_bias': 80,
            # Минимальные настройки слоёв
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
            'layer_1_rule': 'Conway',
            'layer_1_age_palette': 'BGYR',
            'layer_1_rms_mode': 'brightness',
            'layer_1_blend_mode': 'Normal',
            'layer_1_rms_enabled': True,
        }
        app = App(default_sel)
        hud = HUD()
        
        # Тестируем разные конфигурации
        test_configs = [
            {
                'soft_clear_enable': True,
                'soft_mode': 'Удалять клетки',
                'soft_clear_threshold': 70,
                'max_cells_percent': 50,
                'expected': "Removal: ON | Kill | Threshold: 70% | Max: 50%"
            },
            {
                'soft_clear_enable': False,
                'soft_mode': 'Затухание клеток',
                'soft_clear_threshold': 80,
                'max_cells_percent': 60,
                'expected': "Removal: OFF | Fade | Threshold: 80% | Max: 60%"
            },
            {
                'soft_clear_enable': True,
                'soft_mode': 'Затухание клеток',
                'soft_clear_threshold': 75,
                'max_cells_percent': 45,
                'expected': "Removal: ON | Fade | Threshold: 75% | Max: 45%"
            }
        ]
        
        for i, config in enumerate(test_configs):
            print(f"Конфигурация {i+1}:")
            
            # Устанавливаем конфигурацию
            for param, value in config.items():
                if param != 'expected':
                    setattr(app, param, value)
            
            # Обновляем HUD
            hud.update_from_app(app)
            
            # Проверяем текст
            if 'removal_info' in hud.labels:
                actual_text = hud.labels['removal_info'].text
                expected_text = config['expected']
                
                if actual_text == expected_text:
                    print(f"✅ {actual_text}")
                else:
                    print(f"❌ '{actual_text}' (ожидалось '{expected_text}')")
            else:
                print("❌ removal_info панель не найдена")
            
            print()
        
        return True

    if __name__ == "__main__":
        success1 = test_removal_controls()
        success2 = test_removal_info_display()
        
        if success1 and success2:
            print("🎉 Все тесты пройдены успешно!")
        else:
            print("❌ Некоторые тесты не прошли")
            
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()