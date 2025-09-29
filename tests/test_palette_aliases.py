#!/usr/bin/env python3
"""
Тест для проверки работы расширенных псевдонимов палитр AGE.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем функции из guitar_lifeeq.py
from guitar_lifeE import palette_key, color_from_age_only

def test_palette_aliases():
    """Тестируем что все новые псевдонимы палитр работают корректно."""
    
    # Список палитр из HSV_DESIGN_PALETTES и HSV_COLOR_PALETTES
    test_palettes = [
        "Sunset", "Aurora", "Galaxy", "Tropical", "Volcano", "Deep Sea", "Cyberpunk",
        "Fire", "Ocean", "Neon", "Rainbow Smooth", "Ukraine",
        "Grayscale", "Red-DarkRed-Gray-Black"
    ]
    
    print("Тестируем псевдонимы палитр AGE:")
    print("=" * 50)
    
    for palette_name in test_palettes:
        # Проверяем что palette_key возвращает корректный ключ
        key = palette_key(palette_name)
        print(f"Палитра '{palette_name}' -> ключ '{key}'")
        
        # Проверяем что color_from_age_only может сгенерировать цвет с этой палитрой
        try:
            color = color_from_age_only(
                age=10,
                fade_start=20,
                max_age=50,
                sat_drop_pct=0.0,
                val_drop_pct=0.0,
                global_v_mul=1.0,
                age_palette=palette_name
            )
            print(f"  ✅ Цвет: {color}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        
        print()
    
    # Специальный тест для проверки что старые палитры тоже работают
    print("Проверяем классические палитры:")
    print("=" * 30)
    
    classic_palettes = ["BGYR", "FIRE", "OCEAN", "NEON", "UKRAINE", "GRAYSCALE"]
    for palette in classic_palettes:
        key = palette_key(palette)
        color = color_from_age_only(
            age=15,
            fade_start=20,
            max_age=50,
            sat_drop_pct=0.0,
            val_drop_pct=0.0,
            global_v_mul=1.0,
            age_palette=palette
        )
        print(f"Палитра '{palette}' -> ключ '{key}' -> цвет {color}")

if __name__ == "__main__":
    test_palette_aliases()