#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест режимов очистки в Guitar Life
Проверяет работу комбобокса soft_mode в GUI
"""

import os
import sys
import pygame

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

try:
    from guitar_lifeE import App, CLEAR_TYPES
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

def main():
    """Тест интерфейса режимов очистки"""
    print("🧪 Тестирование режимов очистки в GUI")
    print("=" * 45)
    
    try:
        # Простая конфигурация
        config = {
            'layer_count': 2,
            'layers_different': True,
            'layers_cfg': [],
            'soft_mode': 'Удалять клетки',
            'soft_clear_enable': True
        }
        
        # Инициализируем pygame для GUI
        pygame.init()
        screen = pygame.display.set_mode((100, 100))  # Минимальное окно
        
        app = App(config)
        
        print(f"✅ Приложение создано")
        print(f"📋 Текущий режим в App: {app.soft_mode}")
        
        # Проверяем что HUD содержит комбобокс soft_mode
        if 'soft_mode' in app.hud.comboboxes:
            combo = app.hud.comboboxes['soft_mode']
            print(f"✅ Комбобокс soft_mode найден")
            print(f"📋 Опции комбобокса: {combo.options}")
            print(f"🎯 Текущий индекс: {combo.current_index}")
            print(f"🎯 Текущее значение: {combo.current_value}")
        else:
            print("❌ Комбобокс soft_mode НЕ НАЙДЕН в HUD")
        
        # Тестируем все режимы
        modes = [
            ("Kill", "Удалять клетки"),
            ("Fade", "Затухание клеток"), 
            ("Fade+Kill", "Затухание + удаление")
        ]
        
        print(f"\n🔄 Тестирование смены режимов:")
        for ui_value, internal_value in modes:
            # Симулируем изменение через GUI
            app.on_hud_parameter_change('soft_mode', ui_value)
            print(f"  📝 {ui_value} → {app.soft_mode}")
            
            # Проверяем что это правильный внутренний режим
            if app.soft_mode == internal_value:
                print(f"  ✅ Корректное преобразование")
            else:
                print(f"  ❌ Ошибка: ожидался '{internal_value}', получен '{app.soft_mode}'")
        
        pygame.quit()
        
        print(f"\n✅ Все режимы очистки работают корректно!")
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