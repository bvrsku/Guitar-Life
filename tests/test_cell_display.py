#!/usr/bin/env python3
"""
Быстрый тест создания и отображения клеток
"""

import subprocess
import sys

def test_cell_display():
    """Тестирует создание и отображение клеток"""
    
    print("🧪 Тест отображения клеток")
    print("=" * 40)
    
    try:
        # Тест создания Layer и функций отображения
        result = subprocess.run([
            'python.exe', '-c', 
            '''
import numpy as np
import guitar_life

# Создаем тестовую сетку с живыми клетками
grid = np.zeros((50, 50), dtype=bool)
age = np.zeros((50, 50), dtype=np.int32)

# Добавляем блок 2x2 в центр
grid[25:27, 25:27] = True
age[25:27, 25:27] = 5

print(f"✅ Создана сетка с {np.sum(grid)} живыми клетками")

# Тест создания цветного изображения
cfg = {
    "rms_strength": 100, "fade_start": 60, "max_age": 120,
    "fade_sat_drop": 70, "fade_val_drop": 60, "global_v_mul": 1.0,
    "color_rms_min": 0.004, "color_rms_max": 0.3
}

img = guitar_life.build_color_image(
    grid, age, "Возраст + RMS", 0.1, 440.0, cfg, "Fire", "Fire"
)

print(f"✅ Создано изображение {img.shape}")
print(f"✅ Максимальное значение пикселя: {np.max(img)}")
print(f"✅ Количество непустых пикселей: {np.count_nonzero(img)}")

# Проверяем что есть цветные пиксели
if np.max(img) > 0:
    print("✅ Изображение содержит видимые пиксели!")
else:
    print("❌ Изображение полностью черное!")
'''
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Тест успешен!")
            print(result.stdout)
            
            if "Изображение содержит видимые пиксели!" in result.stdout:
                print("\n🎯 Проблема НЕ в создании изображений!")
                print("🔍 Проблема может быть в:")
                print("   • Логике Solo/Mute")
                print("   • Функции blit_layer")
                print("   • Инициализации слоев")
                print("\n💡 Попробуйте:")
                print("   1. Запустить guitar_life.py")
                print("   2. Нажать [T] для тестового паттерна") 
                print("   3. Смотреть консоль на отладочные сообщения")
            else:
                print("\n❌ Проблема в создании изображений")
                
        else:
            print("❌ Ошибка теста:")
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    test_cell_display()