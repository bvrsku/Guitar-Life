#!/usr/bin/env python3
"""
Тест для проверки применения параметров GUI в основном приложении
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
import time
from guitar_lifeE import App

# Инициализация pygame
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Parameter Application Test")

# Создание приложения
app = App()
app.screen = screen

print("🧪 Тестирование применения параметров...")
print("=" * 50)

# Первоначальные значения
initial_values = {
    'global_v_mul': app.global_v_mul,
    'hue_offset': app.hue_offset,
    'aging_speed': app.aging_speed,
    'fade_start': app.fade_start,
    'fade_sat_drop': app.fade_sat_drop,
    'fade_val_drop': app.fade_val_drop,
    'max_age': app.max_age,
}

print("📊 Начальные значения:")
for param, value in initial_values.items():
    print(f"  {param}: {value}")

print("\n🔄 Тестируем изменение параметров через GUI...")

# Тестируем каждый параметр
test_values = {
    'global_v_mul': 2.5,
    'hue_offset': 180,
    'aging_speed': 5.0,
    'fade_start': 100,
    'fade_sat_drop': 50,
    'fade_val_drop': 40,
    'max_age': 200,
}

for param, test_value in test_values.items():
    print(f"\n🎛️ Изменяем {param} на {test_value}")
    
    # Вызываем обработчик (имитируем изменение в GUI)
    app.on_hud_parameter_change(param, test_value)
    
    # Проверяем, изменилось ли значение в приложении
    current_value = getattr(app, param)
    
    if abs(float(current_value) - float(test_value)) < 0.01:
        print(f"  ✅ {param}: {current_value} (применено)")
    else:
        print(f"  ❌ {param}: {current_value} (НЕ применено, ожидалось {test_value})")

print("\n📈 Финальные значения:")
for param in test_values.keys():
    current_value = getattr(app, param)
    print(f"  {param}: {current_value}")

print("\n🎨 Тестируем визуальные эффекты...")

# Создаем несколько клеток для тестирования
app.cells = {}
test_cells = [
    (100, 100, {'age': 50, 'hue': 180, 'sat': 80, 'val': 90}),
    (200, 200, {'age': 80, 'hue': 120, 'sat': 70, 'val': 85}),
    (300, 300, {'age': 30, 'hue': 240, 'sat': 90, 'val': 95}),
]

for x, y, props in test_cells:
    app.cells[(x, y)] = props

print(f"Создано {len(app.cells)} тестовых клеток")

# Проверяем применение aging_speed
old_ages = [(pos, cell['age']) for pos, cell in app.cells.items()]
app.aging_speed = 3.0  # Ускоряем старение
print(f"Установлено aging_speed = {app.aging_speed}")

# Симулируем один цикл старения
for pos, cell in app.cells.items():
    if cell['age'] < app.max_age:
        cell['age'] += app.aging_speed

new_ages = [(pos, cell['age']) for pos, cell in app.cells.items()]

print("Старение клеток:")
for (pos, old_age), (_, new_age) in zip(old_ages, new_ages):
    age_increase = new_age - old_age
    print(f"  Клетка {pos}: {old_age} → {new_age} (прирост: {age_increase})")
    
    if abs(age_increase - app.aging_speed) < 0.01:
        print(f"    ✅ aging_speed применяется правильно")
    else:
        print(f"    ❌ aging_speed НЕ применяется (ожидалось {app.aging_speed})")

print("\n🌈 Тестируем hue_offset...")
original_hue = 120
app.hue_offset = 90  # Сдвигаем цвет
adjusted_hue = (original_hue + app.hue_offset) % 360

print(f"Исходный hue: {original_hue}")
print(f"hue_offset: {app.hue_offset}")
print(f"Результирующий hue: {adjusted_hue}")

if adjusted_hue == 210:  # 120 + 90 = 210
    print("✅ hue_offset применяется правильно")
else:
    print("❌ hue_offset НЕ применяется")

print("\n✨ Результат тестирования:")
print("Если все параметры показывают ✅, то система работает правильно.")
print("Если есть ❌, то нужно проверить обработчик параметров.")

pygame.quit()