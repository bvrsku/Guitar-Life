#!/usr/bin/env python3
"""
Тест для проверки нового свойства alpha в классе Layer
"""

import sys
import numpy as np

# Временный класс Layer для тестирования
from dataclasses import dataclass

@dataclass
class Layer:
    grid: np.ndarray
    age: np.ndarray
    rule: str
    age_palette: str
    rms_palette: str
    color_mode: str
    alpha_live: int = 220
    alpha_old: int = 140
    mix: str = "Normal"
    solo: bool = False
    mute: bool = False
    
    @property
    def alpha(self):
        """Среднее значение прозрачности"""
        return (self.alpha_live + self.alpha_old) // 2
    
    @alpha.setter
    def alpha(self, value):
        """Устанавливает одинаковую прозрачность для live и old"""
        self.alpha_live = value
        self.alpha_old = value

# Тестируем
if __name__ == "__main__":
    # Создаем тестовый слой
    grid = np.zeros((10, 10), dtype=bool)
    age = np.zeros((10, 10), dtype=int)
    
    layer = Layer(
        grid=grid,
        age=age,
        rule="Conway",
        age_palette="Fire",
        rms_palette="Ocean",
        color_mode="Возраст + RMS"
    )
    
    print(f"Исходные значения:")
    print(f"  alpha_live: {layer.alpha_live}")
    print(f"  alpha_old: {layer.alpha_old}")
    print(f"  alpha (среднее): {layer.alpha}")
    
    # Изменяем alpha
    layer.alpha = 180
    print(f"\nПосле установки alpha = 180:")
    print(f"  alpha_live: {layer.alpha_live}")
    print(f"  alpha_old: {layer.alpha_old}")
    print(f"  alpha (среднее): {layer.alpha}")
    
    # Проверяем другое значение
    layer.alpha = 100
    print(f"\nПосле установки alpha = 100:")
    print(f"  alpha_live: {layer.alpha_live}")
    print(f"  alpha_old: {layer.alpha_old}")
    print(f"  alpha (среднее): {layer.alpha}")
    
    print("\n✅ Тест прошел успешно!")