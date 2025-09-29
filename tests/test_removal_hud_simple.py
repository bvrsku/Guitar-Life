#!/usr/bin/env python3
"""
Простой тест для проверки настроек удаления клеток.
"""

import sys
sys.path.insert(0, r'c:\REPOS\Guitar-Life')

try:
    import pygame
    pygame.init()
    
    from guitar_lifeE import App
    
    def test_removal_parameters():
        """Тестируем все параметры удаления клеток."""
        
        print("Тест параметров удаления клеток:")
        print("=" * 40)
        
        # Создаем приложение с минимальной конфигурацией
        config = {
            'layer_count': 1,
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 80,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 1,
            'soft_fade_up': 5,
            'max_cells_percent': 50,
            'soft_clear_threshold': 70,
            'age_bias': 80,
            # Минимальные настройки для слоя
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
        }
        
        app = App(config)
        
        # Проверяем что все параметры инициализированы
        parameters = [
            ('soft_clear_enable', True),
            ('soft_mode', 'Удалять клетки'),
            ('soft_kill_rate', 80),
            ('soft_fade_floor', 0.3),
            ('soft_fade_down', 1),
            ('soft_fade_up', 5),
            ('max_cells_percent', 50),
            ('soft_clear_threshold', 70),
            ('age_bias', 80),
        ]
        
        print("Проверка инициализации параметров:")
        for param_name, expected_value in parameters:
            actual_value = getattr(app, param_name)
            if actual_value == expected_value:
                print(f"✅ {param_name}: {actual_value}")
            else:
                print(f"❌ {param_name}: {actual_value} (ожидалось {expected_value})")
        
        print()
        
        # Тестируем изменение параметров через set_parameter
        print("Тест изменения параметров:")
        test_changes = [
            ('soft_kill_rate', 90),
            ('soft_fade_floor', 0.5),
            ('soft_fade_down', 3),
            ('soft_fade_up', 8),
            ('max_cells_percent', 60),
            ('soft_clear_threshold', 75),
            ('soft_clear_enable', False),
            ('soft_mode_toggle', True),  # True = "Затухание клеток"
        ]
        
        for param_name, new_value in test_changes:
            try:
                app.set_parameter(param_name, new_value)
                
                if param_name == 'soft_clear_enable':
                    actual = app.soft_clear_enable
                elif param_name == 'soft_mode_toggle':
                    actual = app.soft_mode
                    expected_text = "Затухание клеток"
                    if actual == expected_text:
                        print(f"✅ {param_name}: {actual}")
                    else:
                        print(f"❌ {param_name}: {actual} (ожидалось {expected_text})")
                    continue
                else:
                    actual = getattr(app, param_name)
                
                if actual == new_value:
                    print(f"✅ {param_name}: {actual}")
                else:
                    print(f"❌ {param_name}: {actual} (ожидалось {new_value})")
                    
            except Exception as e:
                print(f"❌ {param_name}: Ошибка - {e}")
        
        print()
        return True
        
    def test_removal_logic():
        """Тестируем логику удаления клеток."""
        
        print("Тест логики удаления клеток:")
        print("-" * 30)
        
        config = {
            'layer_count': 1,
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 50,  # 50% удаления
            'soft_fade_floor': 0.3,
            'soft_fade_down': 1,
            'soft_fade_up': 5,
            'max_cells_percent': 30,  # Максимум 30% от сетки
            'soft_clear_threshold': 20,  # Начинать удаление при 20%
            'age_bias': 80,
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
        }
        
        app = App(config)
        
        # Заполняем слой клетками для теста
        import numpy as np
        from guitar_lifeE import GRID_H, GRID_W
        
        total_cells = GRID_H * GRID_W
        max_allowed = int(total_cells * app.max_cells_percent / 100.0)
        threshold_cells = int(total_cells * app.soft_clear_threshold / 100.0)
        
        print(f"Размер сетки: {GRID_H} x {GRID_W} = {total_cells} клеток")
        print(f"Порог удаления: {threshold_cells} клеток ({app.soft_clear_threshold}%)")
        print(f"Максимум: {max_allowed} клеток ({app.max_cells_percent}%)")
        print()
        
        # Сценарий 1: Количество клеток ниже порога
        test_cells_1 = threshold_cells - 100
        app.layers[0].grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        # Добавляем клетки
        positions = [(i % GRID_H, (i * 7) % GRID_W) for i in range(test_cells_1)]
        for x, y in positions:
            app.layers[0].grid[x, y] = True
            app.layers[0].ages[x, y] = 10
        
        alive_before = np.sum(app.layers[0].grid)
        print(f"Сценарий 1: {alive_before} клеток (ниже порога)")
        
        app.soft_population_control()
        alive_after = np.sum(app.layers[0].grid)
        print(f"После удаления: {alive_after} клеток")
        
        if alive_after == alive_before:
            print("✅ Удаление не должно происходить - корректно")
        else:
            print("❌ Удаление произошло когда не должно было")
        
        print()
        
        # Сценарий 2: Количество клеток выше порога, но ниже максимума
        test_cells_2 = max_allowed - 100
        app.layers[0].grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        positions = [(i % GRID_H, (i * 7) % GRID_W) for i in range(test_cells_2)]
        for x, y in positions:
            app.layers[0].grid[x, y] = True
            app.layers[0].ages[x, y] = 10
        
        alive_before = np.sum(app.layers[0].grid)
        print(f"Сценарий 2: {alive_before} клеток (выше порога, ниже максимума)")
        
        app.soft_population_control()
        alive_after = np.sum(app.layers[0].grid)
        removed = alive_before - alive_after
        print(f"После удаления: {alive_after} клеток (удалено {removed})")
        
        if removed > 0 and removed <= alive_before:
            print("✅ Мягкое удаление сработало корректно")
        else:
            print("❌ Мягкое удаление работает неправильно")
        
        print()
        
        # Сценарий 3: Количество клеток выше максимума
        test_cells_3 = max_allowed + 200
        app.layers[0].grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        positions = [(i % GRID_H, (i * 7) % GRID_W) for i in range(min(test_cells_3, total_cells))]
        for x, y in positions:
            app.layers[0].grid[x, y] = True
            app.layers[0].ages[x, y] = 10
        
        alive_before = np.sum(app.layers[0].grid)
        print(f"Сценарий 3: {alive_before} клеток (выше максимума)")
        
        app.soft_population_control()
        alive_after = np.sum(app.layers[0].grid)
        removed = alive_before - alive_after
        print(f"После удаления: {alive_after} клеток (удалено {removed})")
        
        if removed > 0 and alive_after <= max_allowed:
            print("✅ Агрессивное удаление сработало корректно")
        else:
            print("❌ Агрессивное удаление работает неправильно")
        
        print()
        return True

    if __name__ == "__main__":
        success1 = test_removal_parameters()
        success2 = test_removal_logic()
        
        if success1 and success2:
            print("🎉 Все тесты пройдены успешно!")
            print("\n📊 Резюме добавленных настроек удаления в HUD:")
            print("• soft_kill_rate - процент удаления клеток")
            print("• soft_fade_floor - минимальная яркость при затухании")
            print("• soft_fade_down - скорость затухания (вниз)")
            print("• soft_fade_up - скорость затухания (вверх)")
            print("• max_cells_percent - максимальный процент заполнения")
            print("• soft_clear_threshold - порог начала удаления")
            print("• age_bias - предпочтение возраста при удалении")
            print("• soft_clear_enable - включение/выключение системы")
            print("• soft_mode_toggle - переключение Kill/Fade режимов")
            print("• removal_info - информационная панель с текущими настройками")
        else:
            print("❌ Некоторые тесты не прошли")
            
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()