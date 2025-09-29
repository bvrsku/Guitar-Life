#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Демонстрация структурированной версии
==================================================

Показывает возможности каждого модуля без запуска полного приложения.
"""

def demo_constants():
    """Демонстрация модуля констант"""
    print("🔧 МОДУЛЬ КОНСТАНТ")
    print("=" * 40)
    
    from core.constants import CA_RULES, HSV_DESIGN_PALETTES, SAMPLE_RATE, GRID_W, GRID_H
    
    print(f"📏 Размер сетки: {GRID_W}x{GRID_H}")
    print(f"🎵 Частота дискретизации: {SAMPLE_RATE} Hz")
    print(f"🤖 Правила автоматов ({len(CA_RULES)}): {', '.join(CA_RULES[:3])}...")
    print(f"🎨 Дизайн палитры ({len(HSV_DESIGN_PALETTES)}): {', '.join(HSV_DESIGN_PALETTES[:3])}...")
    print()

def demo_palettes():
    """Демонстрация системы палитр"""
    print("🎨 СИСТЕМА ПАЛИТР")
    print("=" * 40)
    
    from core.palettes import (
        hue_fire_from_t, hue_ocean_from_t, hue_galaxy_from_t,
        PaletteState, get_hsv_design_palettes, _cached_hsv_to_rgb
    )
    
    # Демонстрация палитр
    palettes_demo = [
        ("Fire", hue_fire_from_t),
        ("Ocean", hue_ocean_from_t), 
        ("Galaxy", hue_galaxy_from_t)
    ]
    
    print("🔥 Примеры палитр:")
    for name, func in palettes_demo:
        h, s, v = func(0.5)  # Средняя точка
        r, g, b = _cached_hsv_to_rgb(h, s, v)
        print(f"   {name}: HSV({h:.1f}, {s:.2f}, {v:.2f}) → RGB({r}, {g}, {b})")
    
    # Состояние палитры
    state = PaletteState()
    print(f"📊 Состояние: offset={state.hue_offset:.1f}°, invert={state.invert}")
    
    # Количество палитр
    palettes = get_hsv_design_palettes()
    print(f"📈 Всего палитр: {len(palettes)}")
    print()

def demo_cellular_automaton():
    """Демонстрация клеточных автоматов"""
    print("🤖 КЛЕТОЧНЫЕ АВТОМАТЫ")
    print("=" * 40)
    
    import numpy as np
    from core.cellular_automaton import (
        step_life, spawn_cells, get_available_rules, 
        get_available_spawn_methods, get_rule_description
    )
    
    # Создаем простую сетку
    grid = np.zeros((10, 10), dtype=bool)
    
    # Создаем blinker pattern
    grid[4:7, 5] = True
    print("📍 Начальное состояние (blinker):")
    print(f"   Живых клеток: {np.sum(grid)}")
    
    # Симулируем Conway
    new_grid = step_life(grid, "Conway")
    print(f"   После 1 шага: {np.sum(new_grid)} клеток")
    
    # Информация о правилах
    rules = get_available_rules()
    print(f"📋 Доступно правил: {len(rules)}")
    print(f"   Conway: {get_rule_description('Conway')}")
    
    # Методы спавна
    spawn_methods = get_available_spawn_methods()
    print(f"🎲 Методов спавна: {len(spawn_methods)}")
    
    # Тест спавна
    test_grid = np.zeros((20, 20), dtype=bool)
    spawn_cells(test_grid, 10, "Глайдеры")
    print(f"   Спавн глайдеров: {np.sum(test_grid)} клеток")
    print()

def demo_effects():
    """Демонстрация визуальных эффектов"""
    print("✨ ВИЗУАЛЬНЫЕ ЭФФЕКТЫ")
    print("=" * 40)
    
    from core.effects import AVAILABLE_EFFECTS, blend_colors
    
    print(f"🎭 Доступно эффектов: {len(AVAILABLE_EFFECTS)}")
    print(f"   {', '.join(AVAILABLE_EFFECTS[:5])}...")
    
    # Демонстрация смешивания цветов
    color1 = (255, 0, 0)    # Красный
    color2 = (0, 0, 255)    # Синий
    
    blend_modes = ["normal", "multiply", "screen", "overlay", "add"]
    print("🎨 Смешивание цветов (красный + синий):")
    for mode in blend_modes:
        result = blend_colors(color1, color2, mode, 0.5)
        print(f"   {mode:8}: {result}")
    print()

def demo_ui_components():
    """Демонстрация UI компонентов"""
    print("🖱️  UI КОМПОНЕНТЫ")
    print("=" * 40)
    
    from core.ui_components import UISlider, UIButton, UIComboBox, SimpleColors
    
    # Создаем компоненты
    slider = UISlider(10, 10, 200, 20, 0, 100, 75, "Громкость", "{:.0f}%")
    button = UIButton(10, 40, 100, 30, "Пауза", is_toggle=True)
    combo = UIComboBox(10, 80, 150, 25, "Правило", ["Conway", "HighLife", "Seeds"], 0)
    
    print(f"🎚️  Слайдер: {slider.label} = {slider.current_val:.0f}")
    print(f"🔘 Кнопка: {button.label} (toggle: {button.is_toggle})")
    print(f"📋 Комбобокс: {combo.label} = '{combo.current_value}'")
    
    # Цветовая схема
    colors = [attr for attr in dir(SimpleColors) if not attr.startswith('_')]
    print(f"🎨 Цветовая схема: {len(colors)} цветов")
    print()

def demo_audio():
    """Демонстрация аудио модуля"""
    print("🎵 АУДИО СИСТЕМА")
    print("=" * 40)
    
    from core.audio import get_audio_info, frequency_to_note, get_available_audio_devices
    
    # Информация о системе
    info = get_audio_info()
    print(f"📊 Статус аудио:")
    print(f"   librosa: {'✅' if info['librosa_available'] else '❌'}")
    print(f"   sounddevice: {'✅' if info['sounddevice_available'] else '❌'}")
    print(f"   Sample Rate: {info['sample_rate']} Hz")
    print(f"   Block Size: {info['block_size']}")
    
    # Преобразование частот в ноты
    frequencies = [220.0, 440.0, 880.0, 1760.0]  # A3, A4, A5, A6
    print("🎼 Преобразование частот:")
    for freq in frequencies:
        note = frequency_to_note(freq)
        print(f"   {freq:6.1f} Hz → {note}")
    
    # Аудио устройства
    try:
        devices = get_available_audio_devices()
        print(f"🎤 Найдено устройств: {len(devices)}")
    except:
        print("🎤 Устройства недоступны")
    print()

def main():
    """Главная демонстрация"""
    print("🎸 GUITAR LIFE - СТРУКТУРИРОВАННАЯ ВЕРСИЯ")
    print("🎸 ДЕМОНСТРАЦИЯ МОДУЛЕЙ")
    print("=" * 50)
    print()
    
    try:
        demo_constants()
        demo_palettes()
        demo_cellular_automaton()
        demo_effects()
        demo_ui_components()
        demo_audio()
        
        print("✅ ВСЕ МОДУЛИ РАБОТАЮТ КОРРЕКТНО!")
        print()
        print("🚀 Для запуска приложения используйте:")
        print("   python main.py")
        print()
        print("📚 Для подробной информации смотрите:")
        print("   README_STRUCTURED.md")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Установите зависимости: pip install pygame numpy")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
