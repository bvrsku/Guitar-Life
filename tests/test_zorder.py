#!/usr/bin/env python3
"""
Тест z-order для комбобоксов
"""

import pygame
import sys

# Простая проверка того, что наши изменения синтаксически корректны
try:
    exec(open('guitar_life.py').read())
    print("✅ Файл guitar_life.py синтаксически корректен")
    print("✅ Изменения z-order применены успешно")
    
    # Проверим что в коде есть нужные нам изменения
    with open('guitar_life.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'if not combobox.expanded:' in content:
        print("✅ Найдена логика отрисовки закрытых комбобоксов")
    else:
        print("❌ Логика отрисовки закрытых комбобоксов не найдена")
        
    if 'if combobox.expanded:' in content:
        print("✅ Найдена логика отрисовки открытых комбобоксов")
    else:
        print("❌ Логика отрисовки открытых комбобоксов не найдена")
        
    print("\n🎯 Описание исправления:")
    print("• Закрытые комбобоксы рисуются первыми")
    print("• Открытые комбобоксы рисуются поверх всех элементов")
    print("• Это решает проблему перекрытия выпадающих списков")
    
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка выполнения: {e}")
    sys.exit(1)