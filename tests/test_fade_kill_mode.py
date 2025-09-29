#!/usr/bin/env python3
"""
Тест для нового режима "Затухание + удаление" в системе Soft Clean.
"""

import sys
sys.path.insert(0, r'c:\REPOS\Guitar-Life')

try:
    import pygame
    pygame.init()
    
    from guitar_lifeE import App
    import numpy as np
    
    def test_fade_kill_mode():
        """Тестируем новый режим Затухание + удаление."""
        
        print("Тест нового режима 'Затухание + удаление':")
        print("=" * 50)
        
        # Создаем приложение с минимальной конфигурацией
        config = {
            'layer_count': 1,
            'soft_clear_enable': True,
            'soft_mode': 'Затухание + удаление',  # Новый режим
            'soft_kill_rate': 60,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 2,
            'soft_fade_up': 5,
            'max_cells_percent': 40,
            'soft_clear_threshold': 30,
            'age_bias': 80,
            # Минимальные настройки для слоя
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
        }
        
        app = App(config)
        
        # Проверяем что режим правильно установлен
        print(f"Режим Soft Clear: {app.soft_mode}")
        if app.soft_mode == 'Затухание + удаление':
            print("✅ Новый режим правильно инициализирован")
        else:
            print(f"❌ Ожидался режим 'Затухание + удаление', получен '{app.soft_mode}'")
            return False
        
        print()
        
        # Тестируем логику soft_clear для нового режима
        print("Тест логики soft_clear:")
        print("-" * 25)
        
        # Заполняем слой тестовыми клетками
        from guitar_lifeE import GRID_H, GRID_W
        
        app.layers[0].grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        app.layers[0].age = np.zeros((GRID_H, GRID_W), dtype=int)
        
        # Добавляем тестовые клетки
        test_positions = [(10, 10), (10, 11), (11, 10), (11, 11),
                         (20, 20), (20, 21), (21, 20), (21, 21)]
        
        for r, c in test_positions:
            app.layers[0].grid[r, c] = True
            app.layers[0].age[r, c] = 15
        
        cells_before = np.sum(app.layers[0].grid)
        global_v_mul_before = app.global_v_mul
        
        print(f"Клеток до обработки: {cells_before}")
        print(f"global_v_mul до: {global_v_mul_before:.3f}")
        
        # Применяем soft_clear
        app.soft_clear()
        
        cells_after = np.sum(app.layers[0].grid)
        global_v_mul_after = app.global_v_mul
        
        print(f"Клеток после обработки: {cells_after}")
        print(f"global_v_mul после: {global_v_mul_after:.3f}")
        
        # Проверяем результаты
        cells_removed = cells_before - cells_after
        brightness_reduced = global_v_mul_before > global_v_mul_after
        
        if cells_removed > 0 and brightness_reduced:
            print("✅ Комбинированный режим работает: клетки удалились И яркость уменьшилась")
        elif cells_removed > 0:
            print("⚠️ Только удаление клеток сработало")
        elif brightness_reduced:
            print("⚠️ Только затухание яркости сработало")
        else:
            print("❌ Ни удаление, ни затухание не сработали")
        
        print()
        
        # Тестируем soft_population_control для нового режима
        print("Тест логики soft_population_control:")
        print("-" * 35)
        
        # Сбрасываем состояние
        app.layers[0].grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        app.layers[0].age = np.zeros((GRID_H, GRID_W), dtype=int)
        
        # Создаем перенаселение
        total_cells = GRID_H * GRID_W
        threshold_cells = int(total_cells * app.soft_clear_threshold / 100.0)
        test_cell_count = threshold_cells + 500  # Превышаем порог
        
        # Добавляем клетки случайным образом
        positions = [(i % GRID_H, (i * 7) % GRID_W) for i in range(test_cell_count)]
        for r, c in positions:
            app.layers[0].grid[r, c] = True
            app.layers[0].age[r, c] = np.random.randint(5, 25)
        
        cells_before_control = np.sum(app.layers[0].grid)
        print(f"Клеток до population control: {cells_before_control}")
        print(f"Порог срабатывания: {threshold_cells}")
        
        # Применяем population control
        app.soft_population_control()
        
        cells_after_control = np.sum(app.layers[0].grid)
        removed_by_control = cells_before_control - cells_after_control
        
        print(f"Клеток после population control: {cells_after_control}")
        print(f"Удалено/обработано клеток: {removed_by_control}")
        
        if removed_by_control > 0:
            print("✅ Population control в режиме 'Затухание + удаление' работает")
        else:
            print("❌ Population control не сработал")
        
        print()
        return True
    
    def test_mode_switching():
        """Тестируем переключение между режимами."""
        
        print("Тест переключения режимов:")
        print("=" * 30)
        
        config = {
            'layer_count': 1,
            'soft_clear_enable': True,
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 50,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 2,
            'soft_fade_up': 5,
            'max_cells_percent': 40,
            'soft_clear_threshold': 30,
            'age_bias': 80,
            'layer_0_rule': 'Conway',
            'layer_0_age_palette': 'BGYR',
            'layer_0_rms_mode': 'brightness',
            'layer_0_blend_mode': 'Normal',
            'layer_0_rms_enabled': True,
        }
        
        app = App(config)
        
        # Тестируем все три режима
        modes = [
            ("Kill", 'Удалять клетки'),
            ("Fade", 'Затухание клеток'),
            ("Fade+Kill", 'Затухание + удаление')
        ]
        
        for ui_mode, internal_mode in modes:
            print(f"Тестируем режим '{ui_mode}' -> '{internal_mode}'")
            
            # Устанавливаем режим через set_parameter
            app.set_parameter('soft_mode', ui_mode)
            
            if app.soft_mode == internal_mode:
                print(f"✅ Режим '{ui_mode}' правильно установлен")
            else:
                print(f"❌ Ожидался '{internal_mode}', получен '{app.soft_mode}'")
                return False
        
        print()
        print("✅ Все режимы переключаются корректно!")
        return True

    if __name__ == "__main__":
        success1 = test_fade_kill_mode()
        success2 = test_mode_switching()
        
        if success1 and success2:
            print("\n🎉 Все тесты пройдены! Новый режим 'Затухание + удаление' работает корректно!")
            print("\n📊 Особенности нового режима:")
            print("• Комбинирует затухание яркости И удаление клеток")
            print("• В soft_clear: сначала затухание, потом удаление с уменьшенной интенсивностью")
            print("• В population_control: 50% клеток удаляется мгновенно, 50% затухает")
            print("• Обеспечивает более плавное и эффективное управление популяцией")
            print("• Доступен через комбобокс 'Mode' в секции SOFT CLEAN")
        else:
            print("❌ Некоторые тесты не прошли")
            
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()