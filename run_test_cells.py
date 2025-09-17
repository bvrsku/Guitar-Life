#!/usr/bin/env python3
"""
Запуск Guitar Life с немедленным созданием тестового паттерна
"""

import os
import sys
import pygame
import numpy as np

# Добавляем текущую директорию в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем приложение
from guitar_life import Application

def test_with_cells():
    """Тест с автоматическим созданием клеток"""
    
    print("🚀 Запуск Guitar Life с тестовыми клетками...")
    
    # Создаем приложение
    app = Application()
    
    # Создаем тестовые клетки
    print("📝 Создание тестового паттерна...")
    app.create_test_pattern()
    
    print("🎯 Количество живых клеток в слоях:")
    for i, layer in enumerate(app.layers):
        live_cells = np.sum(layer.grid)
        print(f"  Слой {i}: {live_cells} клеток, solo={layer.solo}, mute={layer.mute}")
    
    # Один кадр рендеринга для проверки
    print("🎨 Рендеринг тестового кадра...")
    app.render(0.1, 440.0)
    
    print("✅ Тест завершен! Закройте окно для выхода.")
    
    # Запускаем обычный цикл
    app.run()

if __name__ == "__main__":
    try:
        test_with_cells()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")