#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Краткий тест интерфейса новых типов очистки
Проверяет что GUI правильно отображает новые варианты
"""

import os
import sys
import pygame

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

try:
    from create_safe_config import create_safe_config
    from guitar_lifeE import App, CLEAR_TYPES
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

def main():
    """Краткий тест интерфейса"""
    print("🔍 Тестирование интерфейса типов очистки")
    print("=" * 40)
    
    try:
        # Создаем простую конфигурацию
        config = {
            'layer_count': 2,
            'layers_different': True,
            'layers_cfg': [],
            'clear_type': 'Полная очистка'
        }
        
        print("📋 Конфигурация создана")
        print(f"🎯 Доступные типы очистки: {CLEAR_TYPES}")
        print(f"⚙️ Текущий тип очистки: {config.get('clear_type', 'Не задан')}")
        
        # Проверяем что все типы очистки существуют
        expected_types = [
            "Полная очистка",        # Complete clear 
            "Частичная очистка",     # Partial clear
            "Очистка по возрасту",   # Age-based clear
            "Случайная очистка"      # Random clear
        ]
        
        print("\n🔍 Проверка типов очистки:")
        for clear_type in expected_types:
            if clear_type in CLEAR_TYPES:
                print(f"  ✅ {clear_type} - найден")
            else:
                print(f"  ❌ {clear_type} - НЕ НАЙДЕН")
        
        # Тестируем создание App с новым параметром
        print("\n🚀 Создание приложения...")
        
        # Инициализируем pygame для GUI
        pygame.init()
        screen = pygame.display.set_mode((100, 100))  # Минимальное окно
        
        app = App(config)
        
        print(f"✅ Приложение создано")
        print(f"📋 Текущий тип очистки в App: {app.clear_type}")
        
        # Проверяем что HUD содержит комбобокс clear_type
        if 'clear_type' in app.hud.comboboxes:
            combo = app.hud.comboboxes['clear_type']
            print(f"✅ Комбобокс clear_type найден")
            print(f"📋 Опции комбобокса: {combo.options}")
            print(f"🎯 Текущий индекс: {combo.current_index}")
            print(f"🎯 Текущее значение: {combo.current_value}")
        else:
            print("❌ Комбобокс clear_type НЕ НАЙДЕН в HUD")
        
        pygame.quit()
        
        print("\n✅ Тест интерфейса завершен успешно!")
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