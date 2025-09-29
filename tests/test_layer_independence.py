#!/usr/bin/env python3
"""
Тест независимости слоев - проверяем что каждый слой работает по своим правилам
"""

import sys
import os
import json

def test_layer_independence():
    """Создает конфигурацию для демонстрации независимости слоев"""
    
    # Конфигурация с 3 разными слоями
    test_config = {
        'layers': {
            'layer_count': 3,
            'layers_different': True,
            'auto_rule_sec': 0,  # Отключаем автосмену чтобы видеть разницу
            'auto_palette_sec': 0,
            'mirror_x': False,
            'mirror_y': False,
            'layer_settings': [
                {
                    'rule': 'Conway',
                    'age_palette': 'Fire',
                    'rms_palette': 'Ocean',
                    'solo': False,
                    'mute': False
                },
                {
                    'rule': 'HighLife', 
                    'age_palette': 'Neon',
                    'rms_palette': 'Ukraine',
                    'solo': False,
                    'mute': False
                },
                {
                    'rule': 'Day&Night',
                    'age_palette': 'Blue->Green->Yellow->Red',
                    'rms_palette': 'Fire',
                    'solo': False,
                    'mute': False
                }
            ]
        }
    }
    
    # Сохраняем конфигурацию
    with open('app_config.json', 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print("🔧 Создана тестовая конфигурация для проверки независимости слоев:")
    print("   Слой 1: Conway + Fire/Ocean")
    print("   Слой 2: HighLife + Neon/Ukraine") 
    print("   Слой 3: Day&Night + Blue->Yellow/Fire")
    print("\n✅ Каждый слой будет:")
    print("   - Работать по своим правилам клеточного автомата")
    print("   - Использовать свои цветовые палитры")
    print("   - НЕ влиять на другие слои")
    print("   - Накладываться визуально друг на друга")
    
    print("\n🎸 Запустите guitar_life.py чтобы проверить!")
    print("📋 Используйте HUD ([H]) для управления отдельными слоями")
    print("🔍 Попробуйте Solo/Mute режимы для изоляции слоев")

if __name__ == "__main__":
    test_layer_independence()