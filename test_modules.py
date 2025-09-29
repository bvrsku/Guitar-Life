# This file has been deleted.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование структурированных модулей Guitar Life
"""

def test_imports():
    """Тестируем импорты всех модулей"""
    print("🧪 Тестирование модулей Guitar Life...")
    
    try:
        import core.constants
        print("✅ core.constants - OK")
    except ImportError as e:
        print(f"❌ core.constants - FAILED: {e}")
    
    try:
        import core.palettes
        print("✅ core.palettes - OK")
    except ImportError as e:
        print(f"❌ core.palettes - FAILED: {e}")
    
    try:
        import core.effects
        print("✅ core.effects - OK")
    except ImportError as e:
        print(f"❌ core.effects - FAILED: {e}")
    
    try:
        import core.cellular_automaton
        print("✅ core.cellular_automaton - OK")
    except ImportError as e:
        print(f"❌ core.cellular_automaton - FAILED: {e}")
    
    try:
        import core.ui_components
        print("✅ core.ui_components - OK")
    except ImportError as e:
        print(f"❌ core.ui_components - FAILED: {e}")
    
    try:
        import core.audio
        print("✅ core.audio - OK")
    except ImportError as e:
        print(f"❌ core.audio - FAILED: {e}")

def test_basic_functionality():
    """Тестируем базовую функциональность"""
    print("\n🔧 Тестирование функциональности...")
    
    try:
        from core.constants import CA_RULES, HSV_DESIGN_PALETTES
        print(f"✅ Найдено {len(CA_RULES)} правил автоматов")
        print(f"✅ Найдено {len(HSV_DESIGN_PALETTES)} палитр")
    except Exception as e:
        print(f"❌ Ошибка констант: {e}")
    
    try:
        from core.palettes import hue_fire_from_t, PaletteState
        result = hue_fire_from_t(0.5)
        print(f"✅ Палитра Fire: {result}")
        
        state = PaletteState()
        print(f"✅ PaletteState создан: {state.rms_palette_choice}")
    except Exception as e:
        print(f"❌ Ошибка палитр: {e}")
    
    try:
        from core.cellular_automaton import step_life, get_available_rules
        import numpy as np
        
        grid = np.zeros((10, 10), dtype=bool)
        grid[5, 5:8] = True  # Создаем blinker
        
        new_grid = step_life(grid, "Conway")
        rules = get_available_rules()
        
        print(f"✅ Симуляция Conway: {np.sum(new_grid)} клеток")
        print(f"✅ Доступно правил: {len(rules)}")
    except Exception as e:
        print(f"❌ Ошибка автоматов: {e}")
    
    try:
        from core.ui_components import UISlider, UIButton, SimpleColors
        
        slider = UISlider(0, 0, 100, 20, 0, 100, 50)
        button = UIButton(0, 0, 80, 30, "Test")
        
        print(f"✅ UI Slider создан: {slider.current_val}")
        print(f"✅ UI Button создан: {button.label}")
        print(f"✅ SimpleColors: {len([attr for attr in dir(SimpleColors) if not attr.startswith('_')])} цветов")
    except Exception as e:
        print(f"❌ Ошибка UI: {e}")

def test_audio_module():
    """Тестируем аудио модуль (опционально)"""
    print("\n🎵 Тестирование аудио модуля...")
    
    try:
        from core.audio import get_audio_info, frequency_to_note
        
        info = get_audio_info()
        note = frequency_to_note(440.0)  # A4
        
        print(f"✅ Аудио информация: librosa={info['librosa_available']}, sounddevice={info['sounddevice_available']}")
        print(f"✅ Преобразование частоты: 440Hz = {note}")
        
    except Exception as e:
        print(f"❌ Ошибка аудио: {e}")

if __name__ == "__main__":
    test_imports()
    test_basic_functionality()
    test_audio_module()
    print("\n🎸 Тестирование завершено!")
