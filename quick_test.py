#!/usr/bin/env python3
"""
Быстрая проверка работоспособности приложения
"""

import pygame
import sys
import traceback

def test_app():
    try:
        # Инициализируем pygame
        pygame.init()
        
        # Пытаемся импортировать наш код
        print("🧪 Проверяем синтаксис...")
        with open('guitar_life.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Компилируем код
        compile(code, 'guitar_life.py', 'exec')
        print("✅ Синтаксис корректен")
        
        # Проверяем что expanded свойство добавлено
        if '@property' in code and 'def expanded(self):' in code:
            print("✅ Свойство expanded добавлено в UIComboBox")
        else:
            print("❌ Свойство expanded не найдено")
            
        # Пытаемся создать UIComboBox и проверить expanded
        exec(code)
        
        # Создаем экземпляр UIComboBox из глобального пространства имен
        combo = eval("UIComboBox(0, 0, 100, 20, 'test', ['opt1', 'opt2'])")
        
        # Проверяем что expanded работает
        assert hasattr(combo, 'expanded'), "Нет атрибута expanded"
        assert combo.expanded == False, "expanded должен быть False по умолчанию"
        print("✅ Свойство expanded работает корректно")
        
        pygame.quit()
        print("\n🎯 Исправление successful! Приложение должно работать.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_app()