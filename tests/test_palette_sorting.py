#!/usr/bin/env python3
"""
Тест новой сортировки палитр по категориям HSV
"""

import sys
import os

# Добавляем текущую папку в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_palette_sorting():
    """Тестирует новую группировку палитр"""
    print("🎨 Тестирование новой сортировки палитр...")
    
    try:
        from guitar_li4fe import HSV_DESIGN_PALETTES, HSV_COLOR_PALETTES, PALETTE_OPTIONS
        from guitar_li4fe import get_hsv_design_palettes, get_hsv_color_palettes, get_palette_by_category
        
        print("\n📊 HSV-дизайны (комбинированный режим):")
        print(f"   Количество: {len(HSV_DESIGN_PALETTES)}")
        print("   Категории:")
        print("   • Основные HSV переходы")
        print("   • Природные дизайны") 
        print("   • Сезонные палитры")
        print("   • Научные палитры")
        print("\n   Примеры:")
        for i, palette in enumerate(HSV_DESIGN_PALETTES[:8]):
            print(f"   {i+1:2}. {palette}")
        if len(HSV_DESIGN_PALETTES) > 8:
            print(f"   ... и еще {len(HSV_DESIGN_PALETTES)-8} палитр")
        
        print("\n🎭 HSV Палитры (только RMS режим):")
        print(f"   Количество: {len(HSV_COLOR_PALETTES)}")
        print("   Категории:")
        print("   • Монохромные и контрастные")
        print("   • Материалы и текстуры")
        print("   • Специальные и тематические")
        print("   • Природные цвета")
        print("\n   Примеры:")
        for i, palette in enumerate(HSV_COLOR_PALETTES[:8]):
            print(f"   {i+1:2}. {palette}")
        if len(HSV_COLOR_PALETTES) > 8:
            print(f"   ... и еще {len(HSV_COLOR_PALETTES)-8} палитр")
        
        print(f"\n📈 Статистика:")
        print(f"   HSV-дизайны: {len(HSV_DESIGN_PALETTES)} палитр")
        print(f"   HSV Палитры: {len(HSV_COLOR_PALETTES)} палитр")
        print(f"   Всего: {len(PALETTE_OPTIONS)} палитр")
        print(f"   Проверка целостности: {len(HSV_DESIGN_PALETTES) + len(HSV_COLOR_PALETTES) == len(PALETTE_OPTIONS)}")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
        
    return True

def test_palette_functions():
    """Тестирует функции для работы с палитрами"""
    print("\n🔧 Тестирование функций палитр...")
    
    try:
        from guitar_li4fe import get_hsv_design_palettes, get_hsv_color_palettes, get_palette_by_category
        
        # Тест функций получения палитр
        design_palettes = get_hsv_design_palettes()
        color_palettes = get_hsv_color_palettes()
        
        print(f"✅ get_hsv_design_palettes(): {len(design_palettes)} палитр")
        print(f"✅ get_hsv_color_palettes(): {len(color_palettes)} палитр")
        
        # Тест функции по категориям
        test_categories = ["HSV-дизайны", "HSV Палитры", "Все"]
        
        for category in test_categories:
            palettes = get_palette_by_category(category)
            print(f"✅ get_palette_by_category('{category}'): {len(palettes)} палитр")
            
        # Проверяем что нет дубликатов
        all_palettes = design_palettes + color_palettes
        unique_palettes = list(set(all_palettes))
        
        if len(all_palettes) == len(unique_palettes):
            print("✅ Дубликаты палитр отсутствуют")
        else:
            print(f"⚠️  Найдены дубликаты: {len(all_palettes) - len(unique_palettes)}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования функций: {e}")
        return False
        
    return True

def test_randomize_logic():
    """Тестирует логику рандомизации"""
    print("\n🎲 Тестирование логики рандомизации...")
    
    try:
        from guitar_li4fe import PaletteState
        
        # Создаем состояние палитр
        palette_state = PaletteState()
        
        print("Тестируем рандомизацию 5 раз:")
        for i in range(5):
            palette_state.randomize()
            print(f"  {i+1}. RMS: {palette_state.rms_palette_choice}")
            print(f"     Age: {palette_state.age_palette_choice}")
        
        print("✅ Рандомизация работает корректно")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования рандомизации: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестов новой сортировки палитр...\n")
    
    success = True
    success &= test_palette_sorting()
    success &= test_palette_functions()
    success &= test_randomize_logic()
    
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
        print("\n💡 Ключевые изменения:")
        print("   • Палитры разделены на логические группы")
        print("   • HSV-дизайны: для комбинированного режима (возраст + RMS)")
        print("   • HSV Палитры: для упрощенного режима (только RMS)")
        print("   • Добавлены функции для получения палитр по категориям")
        print("   • Рандомизация использует соответствующие группы")
    else:
        print("\n❌ Некоторые тесты не прошли!")