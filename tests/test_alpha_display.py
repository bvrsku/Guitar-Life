#!/usr/bin/env python3
"""
Тест для проверки отображения alpha_live и alpha_old в HUD
"""

import sys
import os

# Добавляем текущую папку в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guitar_li4fe import *

def test_alpha_display():
    """Тестирует отображение alpha значений в HUD"""
    print("🧪 Тестирование отображения alpha значений в HUD...")
    
    # Создаем тестовую конфигурацию
    test_config = {
        'layer_count': 3,
        'device': None,  # Без звука для теста
        'max_age': 120,
        'aging_speed': 1.5,  # Тестируем и наш новый параметр
        'tick_ms': 100,
        'rms_strength': 100,
        'gain': 2.5,
        'fx': {},
        'layers_different': True
    }
    
    # Создаем приложение
    app = App(test_config)
    
    # Проверяем что слои созданы с разными alpha значениями
    print(f"📊 Создано слоев: {len(app.layers)}")
    
    for i, layer in enumerate(app.layers):
        print(f"  Слой {i}: alpha_live={layer.alpha_live}, alpha_old={layer.alpha_old}")
        
        # Устанавливаем разные значения для демонстрации
        layer.alpha_live = 200 + i * 20  # 200, 220, 240
        layer.alpha_old = 150 + i * 15   # 150, 165, 180
    
    # Симулируем создание info словаря
    total_alive = sum(np.sum(L.grid) for L in app.layers)
    
    # Создаем информацию о альфа-значениях слоев (копируем логику из главного кода)
    alpha_info = []
    for i, layer in enumerate(app.layers):
        alpha_info.append(f"L{i}: {layer.alpha_live}/{layer.alpha_old}")
    
    info = {
        "RMS": "0.0050",
        "Pitch": "440.0 Hz",
        "Tick": "100 ms",
        "Alive": f"{total_alive} cells",
        "Layers": f"{len(app.layers)}",
        "Max Age": f"{app.max_age}",
        "Aging Speed": f"{app.aging_speed:.1f}x",
        "Alpha Values": " | ".join(alpha_info) if alpha_info else "none",
        "FX": "none",
    }
    
    print("\n📋 Информация для HUD:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Тест завершен! Alpha значения должны отображаться в формате:")
    print(f"   Alpha Values: {info['Alpha Values']}")
    print("\n💡 Где L0, L1, L2 - номера слоев, первое число - alpha_live, второе - alpha_old")

if __name__ == "__main__":
    test_alpha_display()