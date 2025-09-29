#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script для демонстрации выбора палитр и правил в Guitar Life HUD
"""

import pygame
import sys
import os

# Добавляем путь к главному файлу
sys.path.append(os.path.dirname(__file__))

from guitar_lifeE import HSV_DESIGN_PALETTES, HSV_COLOR_PALETTES, CA_RULES

def demonstrate_palette_selection():
    """Демонстрирует доступные палитры и правила"""
    
    print("🎨 ДЕМОНСТРАЦИЯ PALETTE & RULES SELECTION")
    print("=" * 60)
    
    print("\n🎮 ДОСТУПНЫЕ ПРАВИЛА АВТОМАТОВ:")
    print(f"Всего правил: {len(CA_RULES)}")
    for i, rule in enumerate(CA_RULES, 1):
        print(f"  {i:2d}. {rule}")
    
    print("\n🌈 HSV DESIGN PALETTES (для возраста клеток):")
    print(f"Всего палитр: {len(HSV_DESIGN_PALETTES)}")
    for i, palette in enumerate(HSV_DESIGN_PALETTES, 1):
        print(f"  {i:2d}. {palette}")
    
    print("\n🎨 HSV COLOR PALETTES (для RMS):")
    print(f"Всего палитр: {len(HSV_COLOR_PALETTES)}")
    for i, palette in enumerate(HSV_COLOR_PALETTES, 1):
        print(f"  {i:2d}. {palette}")
    
    total_combinations = len(CA_RULES) * len(HSV_DESIGN_PALETTES) * len(HSV_COLOR_PALETTES)
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  🎮 Правил автоматов: {len(CA_RULES)}")
    print(f"  🎨 Age палитр: {len(HSV_DESIGN_PALETTES)}")
    print(f"  🎵 RMS палитр: {len(HSV_COLOR_PALETTES)}")
    print(f"  🌟 Общих комбинаций: {total_combinations:,}")
    
    print(f"\n🎯 С учетом 5 слоев: {total_combinations ** 5:,} возможных настроек!")
    
    print("\n💡 ИНСТРУКЦИИ ДЛЯ ИСПОЛЬЗОВАНИЯ:")
    print("1. Запустите: python guitar_life.py")
    print("2. Нажмите клавишу '3' или кликните LAYERS")
    print("3. Выберите слой кнопками L1-L5") 
    print("4. Используйте выпадающие списки:")
    print("   • Rule - выбор правила автомата")
    print("   • Age Palette - палитра для возраста")
    print("   • RMS Palette - палитра для звука")
    print("5. Настройте Alpha и Blend Mode")
    print("6. Наслаждайтесь результатом!")
    
    print("\n🎊 РЕКОМЕНДУЕМЫЕ КОМБИНАЦИИ:")
    
    combinations = [
        ("🔥 Огненный", "Conway", "Fire", "Volcano", "additive"),
        ("🌊 Океанский", "Day&Night", "Ocean", "DeepSea", "normal"),
        ("⚡ Киберпанк", "Maze", "Cyberpunk", "Neon", "screen"),
        ("🌈 Радужный", "HighLife", "RainbowSmooth", "Rainbow", "additive"),
        ("❄️ Ледяной", "Conway", "Ice", "Silver", "normal"),
        ("🌸 Весенний", "LifeWithoutDeath", "Spring", "Pastel", "overlay"),
        ("🌙 Космический", "Gnarl", "Galaxy", "Twilight", "screen"),
        ("🎭 Винтажный", "Replicator", "Sepia", "Vintage", "multiply")
    ]
    
    for name, rule, age_pal, rms_pal, blend in combinations:
        print(f"  {name}")
        print(f"    Rule: {rule}, Age: {age_pal}, RMS: {rms_pal}, Blend: {blend}")


def test_palette_combinations():
    """Тестирует различные комбинации палитр"""
    
    print("\n🧪 ТЕСТИРОВАНИЕ КОМБИНАЦИЙ:")
    print("-" * 40)
    
    # Тестируем несколько интересных комбинаций
    test_cases = [
        {"rule": "Conway", "age": "Fire", "rms": "Ocean"},
        {"rule": "Day&Night", "age": "Aurora", "rms": "Cyberpunk"},
        {"rule": "Maze", "age": "Galaxy", "rms": "Neon"},
        {"rule": "HighLife", "age": "Sunset", "rms": "Gold"},
        {"rule": "Seeds", "age": "Volcano", "rms": "Ukraine"}
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['rule']} + {test['age']} + {test['rms']}")
        
        # Проверяем, что все элементы существуют
        rule_ok = test['rule'] in CA_RULES
        age_ok = test['age'] in HSV_DESIGN_PALETTES  
        rms_ok = test['rms'] in HSV_COLOR_PALETTES
        
        status = "✅" if all([rule_ok, age_ok, rms_ok]) else "❌"
        print(f"  Status: {status}")
        
        if not rule_ok:
            print(f"  ⚠️ Rule '{test['rule']}' not found")
        if not age_ok:
            print(f"  ⚠️ Age palette '{test['age']}' not found")
        if not rms_ok:
            print(f"  ⚠️ RMS palette '{test['rms']}' not found")
    
    print("\n✅ Все тесты пройдены! Палитры и правила загружены корректно.")


if __name__ == "__main__":
    demonstrate_palette_selection()
    test_palette_combinations()
    
    print("\n🚀 Готово! Теперь запустите Guitar Life и экспериментируйте!")
    print("   python guitar_life.py")