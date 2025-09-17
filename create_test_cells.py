#!/usr/bin/env python3
"""
Создание тестовой конфигурации с принудительным созданием клеток
"""

import json

def create_test_config_with_cells():
    """Создает конфигурацию которая гарантированно должна показать клетки"""
    
    test_config = {
        'layers': {
            'layer_count': 1,  # Только один слой для простоты
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
                    'solo': False,  # НЕ solo!
                    'mute': False   # НЕ mute!
                }
            ]
        }
    }
    
    with open('app_config.json', 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print("🔧 Создана простая тестовая конфигурация:")
    print("   - 1 слой Conway с Fire палитрой")
    print("   - НЕТ Solo/Mute конфликтов")
    print("   - Простейшая настройка")
    print()
    print("🎮 После запуска:")
    print("   1. Нажмите [T] для создания тестового паттерна")
    print("   2. Нажмите [R] для случайных паттернов")
    print("   3. Играйте в микрофон для создания клеток")
    print("   4. Смотрите консоль для отладочной информации")

if __name__ == "__main__":
    create_test_config_with_cells()