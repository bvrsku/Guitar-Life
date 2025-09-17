#!/usr/bin/env python3
"""
Тестовый скрипт для проверки HUD элементов
"""

# Проверяем что все модули доступны
try:
    import pygame
    print("✓ pygame доступен")
except ImportError as e:
    print(f"✗ pygame недоступен: {e}")

try:
    import numpy as np
    print("✓ numpy доступен")
except ImportError as e:
    print(f"✗ numpy недоступен: {e}")

# Проверяем синтаксис основного файла
try:
    import py_compile
    py_compile.compile('guitar_life.py', doraise=True)
    print("✓ guitar_life.py синтаксически корректен")
except py_compile.PyCompileError as e:
    print(f"✗ Ошибка синтаксиса в guitar_life.py: {e}")

# Тестируем создание HUD класса
try:
    import sys
    sys.path.append('.')
    
    # Инициализируем pygame для создания шрифта
    pygame.init()
    font = pygame.font.SysFont("consolas", 16)
    
    # Импортируем классы HUD
    from guitar_life import HUD, UISlider, UIButton
    
    # Создаем HUD
    hud = HUD(font)
    print(f"✓ HUD создан успешно")
    print(f"  - Слайдеров создано: {len(hud.sliders)}")
    print(f"  - Кнопок создано: {len(hud.buttons)}")
    print(f"  - Слайдеры: {list(hud.sliders.keys())}")
    print(f"  - Кнопки: {list(hud.buttons.keys())}")
    
    pygame.quit()
    
except Exception as e:
    print(f"✗ Ошибка при создании HUD: {e}")
    import traceback
    traceback.print_exc()

print("\nТест завершен.")