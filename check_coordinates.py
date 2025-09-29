#!/usr/bin/env python3
"""
Простая проверка кода создания модулей
"""

# Имитируем создание модуля слоя
panel_x = 100  # Примерное значение

# Размеры элементов (копируем из кода)
control_width = 180
control_height = 25
slider_width = 150
button_width = 60
combo_width = 120

x_left = panel_x + 10   # = 110
x_right = panel_x + 200 # = 300

print("🔍 Проверка координат:")
print(f"panel_x = {panel_x}")
print(f"x_left = {x_left}")
print(f"x_right = {x_right}")
print()

# Имитируем создание элементов
current_y = 100

print("📍 Создание элементов:")

# RMS Mode
rms_mode_x = x_right
rms_mode_y = current_y
print(f"RMS Mode: x={rms_mode_x}, y={rms_mode_y} (правая колонка)")

# Palette Mix (должен быть в правой колонке)
palette_mix_x = x_right
palette_mix_y = current_y + 35
print(f"Palette Mix: x={palette_mix_x}, y={palette_mix_y} (правая колонка)")

# Обновляем current_y
current_y += 70

# Spawn Method (в левой колонке)
spawn_method_x = x_left
spawn_method_y = current_y  
print(f"Spawn Method: x={spawn_method_x}, y={spawn_method_y} (левая колонка)")

print()
print("✅ По коду Palette Mix должен быть в правой колонке!")
print(f"   Ожидаемые координаты: x={palette_mix_x} (правая колонка)")
print(f"   vs x={x_left} (левая колонка)")

if palette_mix_x == x_right:
    print("✅ Palette Mix правильно установлен в правую колонку")
else:
    print("❌ Palette Mix НЕ в правой колонке")