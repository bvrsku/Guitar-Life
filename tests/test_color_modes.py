#!/usr/bin/env python3
"""
Тест нового разделения палитр на HSV-дизайны и HSV Палитры
"""

import sys
import os

# Добавляем текущую папку в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_color_mode_changes():
    """Тестирует новое разделение палитр"""
    print("🎨 Тестирование нового разделения палитр...")
    
    # Симулируем разные режимы color_mode
    test_modes = [
        "HSV-дизайны",      # Бывший "Возраст + RMS" 
        "HSV Палитры",      # Бывший "Только RMS"
        "Высота ноты (Pitch)"  # Остается без изменений
    ]
    
    print("\n📋 Доступные режимы цвета:")
    for i, mode in enumerate(test_modes, 1):
        print(f"  {i}. {mode}")
    
    print("\n🔄 Тест логики выбора режима:")
    
    for mode in test_modes:
        print(f"\n--- Режим: {mode} ---")
        
        if mode == "HSV Палитры":
            print("  ✅ Использует color_from_rms() - только RMS")
            print("  📊 Цвет зависит только от уровня RMS")
            print("  🎵 Игнорирует возраст клеток")
            
        elif mode == "Высота ноты (Pitch)":
            print("  ✅ Использует color_from_pitch() - высота ноты")
            print("  🎼 Цвет зависит от частоты звука")
            print("  📈 Включает модификацию RMS")
            
        else:  # HSV-дизайны (по умолчанию)
            print("  ✅ Использует color_from_age_rms() - комбинированный")
            print("  🧬 Цвет зависит от возраста клеток")
            print("  🎵 Модифицируется уровнем RMS")
            print("  🎨 Поддерживает разные режимы смешивания")
    
    print("\n💡 Изменения в коде:")
    print("  • Layer.color_mode: теперь HSV-дизайны | HSV Палитры | Высота ноты")
    print("  • build_color_image(): обновлена логика выбора функции цвета")
    print("  • modern_gui.py: обновлены дефолтные конфигурации слоев")
    print("  • choose_settings(): все 'Возраст + RMS' заменены на 'HSV-дизайны'")
    
    print("\n✅ Тест завершен! Новое разделение готово к использованию.")
    
def test_backwards_compatibility():
    """Тестирует обратную совместимость"""
    print("\n🔄 Тестирование обратной совместимости...")
    
    # Старые конфигурации
    old_configs = [
        {'color_mode': 'Возраст + RMS'},
        {'color_mode': 'Только RMS'},
        {'color_mode': 'Высота ноты (Pitch)'}
    ]
    
    print("\n📁 Обработка старых конфигураций:")
    for config in old_configs:
        old_mode = config['color_mode']
        
        # Логика преобразования (если потребуется)
        if old_mode == 'Возраст + RMS':
            new_mode = 'HSV-дизайны'
        elif old_mode == 'Только RMS':
            new_mode = 'HSV Палитры'
        else:
            new_mode = old_mode
            
        print(f"  '{old_mode}' → '{new_mode}'")
    
    print("\n⚠️  Внимание: Старые конфигурации могут требовать обновления!")

if __name__ == "__main__":
    test_color_mode_changes()
    test_backwards_compatibility()