#!/usr/bin/env python3
"""
Простой тест псевдонимов палитр без GUI зависимостей.
"""

# Минимальная реализация palette_key для тестирования
_PALETTE_ALIASES = {
    # HSV_DESIGN_PALETTES mappings
    "Sunset": "SUNSET",
    "Aurora": "AURORA", 
    "Galaxy": "GALAXY",
    "Tropical": "TROPICAL",
    "Volcano": "VOLCANO",
    "Deep Sea": "DEEPSEA",
    "Cyberpunk": "CYBERPUNK",
    
    # HSV_COLOR_PALETTES mappings
    "Fire": "FIRE",
    "Ocean": "OCEAN", 
    "Neon": "NEON",
    "Rainbow Smooth": "RAINBOWSMOOTH",
    "Ukraine": "UKRAINE",
    "Grayscale": "GRAYSCALE",
    "Red-DarkRed-Gray-Black": "RED_DARKRED_GRAY_BLACK"
}

def test_palette_key(age_palette: str) -> str:
    """Тестовая версия palette_key функции."""
    key = _PALETTE_ALIASES.get(age_palette, "BGYR")
    return key

def test_all_aliases():
    """Тестируем все псевдонимы палитр."""
    print("Тест псевдонимов палитр:")
    print("=" * 40)
    
    test_cases = [
        # Новые палитры из HSV_DESIGN_PALETTES  
        "Sunset", "Aurora", "Galaxy", "Tropical", "Volcano", "Deep Sea", "Cyberpunk",
        # Классические палитры из HSV_COLOR_PALETTES
        "Fire", "Ocean", "Neon", "Rainbow Smooth", "Ukraine", "Grayscale", "Red-DarkRed-Gray-Black",
        # Проверка несуществующей палитры
        "NonExistent Palette"
    ]
    
    for palette_name in test_cases:
        result = test_palette_key(palette_name)
        status = "✅" if result != "BGYR" or palette_name in ["BGYR"] else "❌"
        print(f"{status} '{palette_name}' -> '{result}'")
    
    print("\nПроверка завершена!")

if __name__ == "__main__":
    test_all_aliases()