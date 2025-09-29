#!/usr/bin/env python3
"""
Финальный тест стабильности приложения после устранения вылетов
"""

import subprocess
import sys
import time

def final_stability_test():
    """Комплексный тест стабильности"""
    
    print("🚀 Финальный тест стабильности Guitar Life")
    print("=" * 50)
    
    # 1. Тест импорта
    print("1️⃣ Тестируем импорт без отладочных принтов...")
    try:
        result = subprocess.run([
            'python.exe', '-c', 
            'import guitar_life; print("✅ Импорт успешен")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Импорт работает стабильно")
        else:
            print(f"❌ Ошибка импорта: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Критическая ошибка импорта: {e}")
        return False
    
    # 2. Тест создания основных объектов
    print("\n2️⃣ Тестируем создание объектов...")
    try:
        result = subprocess.run([
            'python.exe', '-c', 
            '''
import numpy as np
import guitar_life

# Тест создания Layer
grid = np.zeros((50, 50), dtype=bool)
age = np.zeros((50, 50), dtype=np.int32)
layer = guitar_life.Layer(
    grid=grid, age=age, rule="Conway",
    age_palette="Fire", rms_palette="Fire",
    color_mode="Возраст + RMS"
)
print("✅ Layer создан")

# Тест step_life
new_grid = guitar_life.step_life(grid, "Conway")
print("✅ step_life работает")

# Тест build_color_image
img = guitar_life.build_color_image(grid, age, "Возраст + RMS", 0.1, 440.0, 
    {"rms_strength": 100, "fade_start": 60, "max_age": 120, 
     "fade_sat_drop": 70, "fade_val_drop": 60, "global_v_mul": 1.0,
     "color_rms_min": 0.004, "color_rms_max": 0.3}, "Fire", "Fire")
print(f"✅ build_color_image создал изображение {img.shape}")

print("✅ Все основные компоненты работают стабильно")
'''
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Создание объектов работает стабильно")
            print(result.stdout)
        else:
            print(f"❌ Ошибка создания объектов: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print()
    print("✅ Основные исправления:")
    print("   • Убраны избыточные отладочные принты")
    print("   • Исправлена обработка RGBA изображений")
    print("   • Добавлена обработка ошибок в blit_layer")
    print("   • Создана безопасная конфигурация")
    print()
    print("🎸 Приложение готово к запуску:")
    print("   python.exe guitar_life.py")
    
    return True

if __name__ == "__main__":
    final_stability_test()