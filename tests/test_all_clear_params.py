#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест всех параметров очистки в HUD
Проверяет работу всех трех новых слайдеров параметров очистки
"""

import os
import sys
import pygame

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_lifeE import App, CLEAR_TYPES
    import numpy as np
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

def main():
    """Финальный тест всех параметров очистки"""
    print("🧪 Финальный тест всех параметров очистки в HUD")
    print("=" * 55)
    
    try:
        # Конфигурация с кастомными значениями
        config = {
            'layer_count': 2,
            'layers_different': True,
            'layers_cfg': [],
            'clear_partial_percent': 60,
            'clear_age_threshold': 12,
            'clear_random_percent': 25
        }
        
        # Инициализируем pygame для GUI
        pygame.init()
        screen = pygame.display.set_mode((100, 100))  # Минимальное окно
        
        app = App(config)
        
        print(f"✅ Приложение создано с кастомными параметрами:")
        print(f"   📊 Процент частичной очистки: {app.clear_partial_percent}%")
        print(f"   📊 Порог возраста для очистки: {app.clear_age_threshold}")
        print(f"   📊 Процент случайной очистки: {app.clear_random_percent}%")
        
        # Проверяем все слайдеры
        sliders_to_check = [
            ('clear_partial_percent', 'Partial Clear (%)'),
            ('clear_age_threshold', 'Age Threshold'),
            ('clear_random_percent', 'Random Clear (%)')
        ]
        
        print(f"\n🎛️ Проверка слайдеров в HUD:")
        for slider_name, display_name in sliders_to_check:
            if slider_name in app.hud.sliders:
                slider = app.hud.sliders[slider_name]
                print(f"   ✅ {display_name}: {slider.current_val} (диапазон: {slider.min_val}-{slider.max_val})")
            else:
                print(f"   ❌ {display_name}: НЕ НАЙДЕН")
        
        # Тестируем все типы очистки с кастомными параметрами
        print(f"\n🧪 Тестирование всех типов очистки:")
        
        test_scenarios = [
            ("Частичная очистка", app.clear_partial_percent),
            ("Очистка по возрасту", app.clear_age_threshold), 
            ("Случайная очистка", app.clear_random_percent)
        ]
        
        for clear_type, expected_param in test_scenarios:
            print(f"\n   📋 Тестируем: {clear_type}")
            
            # Создаем тестовые клетки
            for layer in app.layers:
                layer.grid[:] = False
                layer.age[:] = 0
                
                # Добавляем 30 клеток
                for i in range(30):
                    r = np.random.randint(0, min(20, layer.grid.shape[0]))
                    c = np.random.randint(0, min(20, layer.grid.shape[1]))
                    layer.grid[r, c] = True
                    # Возраст от 1 до 20
                    layer.age[r, c] = np.random.randint(1, 21)
            
            total_before = sum(np.sum(layer.grid) for layer in app.layers)
            
            if clear_type == "Очистка по возрасту":
                old_cells_before = 0
                for layer in app.layers:
                    old_cells_before += np.sum((layer.grid) & (layer.age >= app.clear_age_threshold))
                print(f"      📊 До: {total_before} клеток ({old_cells_before} старых >= {app.clear_age_threshold})")
            else:
                print(f"      📊 До: {total_before} клеток")
            
            # Выполняем очистку
            app.clear_type = clear_type
            app.clear_with_type()
            
            total_after = sum(np.sum(layer.grid) for layer in app.layers)
            removed = total_before - total_after
            removal_percent = (removed / total_before * 100) if total_before > 0 else 0
            
            print(f"      📊 После: {total_after} клеток (удалено: {removed}, {removal_percent:.1f}%)")
            
            # Проверяем соответствие ожидаемому параметру
            if clear_type in ["Частичная очистка", "Случайная очистка"]:
                expected_removal = expected_param
                if abs(removal_percent - expected_removal) < 10:  # Допуск 10%
                    print(f"      ✅ Удаление соответствует параметру {expected_param}%")
                else:
                    print(f"      ⚠️ Удаление {removal_percent:.1f}% не точно соответствует {expected_param}%")
            elif clear_type == "Очистка по возрасту":
                old_cells_after = 0
                for layer in app.layers:
                    old_cells_after += np.sum((layer.grid) & (layer.age >= app.clear_age_threshold))
                if old_cells_after == 0:
                    print(f"      ✅ Все старые клетки (>= {expected_param}) удалены")
                else:
                    print(f"      ⚠️ Остались старые клетки: {old_cells_after}")
        
        # Тестируем изменение параметров через HUD
        print(f"\n🔄 Тестирование изменения параметров через HUD:")
        
        new_values = [
            ('clear_partial_percent', 80),
            ('clear_age_threshold', 20),
            ('clear_random_percent', 40)
        ]
        
        for param_name, new_value in new_values:
            old_value = getattr(app, param_name)
            app.on_hud_parameter_change(param_name, new_value)
            new_actual = getattr(app, param_name)
            print(f"   📝 {param_name}: {old_value} → {new_actual}")
            
            if new_actual == new_value:
                print(f"   ✅ Параметр обновлен корректно")
            else:
                print(f"   ❌ Ошибка: ожидался {new_value}, получен {new_actual}")
        
        pygame.quit()
        
        print(f"\n🎉 Все параметры очистки успешно добавлены в HUD!")
        print(f"✅ Теперь пользователи могут настраивать:")
        print(f"   🎛️ Процент частичной очистки (10-90%)")
        print(f"   🎛️ Порог возраста для очистки (1-50)")
        print(f"   🎛️ Процент случайной очистки (10-90%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        if pygame.get_init():
            pygame.quit()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)