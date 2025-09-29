#!/usr/bin/env python3
"""
Создание безопасной конфигурации для устранения вылетов
"""

import json

def create_safe_config():
    """Создает простую и безопасную конфигурацию для тестирования"""
    
    safe_config = {
        'layers': {
            'layer_count': 2,
            'layers_different': True,
            'auto_rule_sec': 0,
            'auto_palette_sec': 0,
            'mirror_x': False,
            'mirror_y': False,
            'layer_settings': [
                {
                    'rule': 'Conway',
                    'age_palette': 'Fire',
                    'rms_palette': 'Fire',
                    'solo': False,
                    'mute': False
                },
                {
                    'rule': 'HighLife',
                    'age_palette': 'Ocean',
                    'rms_palette': 'Ocean',
                    'solo': False,
                    'mute': False
                }
            ]
        }
    }
    
    with open('app_config.json', 'w', encoding='utf-8') as f:
        json.dump(safe_config, f, indent=2, ensure_ascii=False)
    
    print("🔧 Создана безопасная конфигурация:")
    print("   - 2 слоя (соответствует layer_count)")
    print("   - Нет конфликтующих Solo/Mute настроек") 
    print("   - Простые и проверенные палитры")
    print("   - Отключена автосмена")
    print()
    print("✅ Эта конфигурация должна работать без вылетов")

if __name__ == "__main__":
    create_safe_config()