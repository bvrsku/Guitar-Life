#!/usr/bin/env python3
"""
Простой тест интеграции HUD и GUI редакторов слоев
"""

import json

def test_layer_config_integration():
    """Тестируем создание и загрузку конфигурации слоев"""
    
    # Создаем тестовую конфигурацию слоев
    test_config = {
        'layers': {
            'layer_count': 3,
            'layers_different': True,
            'auto_rule_sec': 5,
            'auto_palette_sec': 10,
            'mirror_x': False,
            'mirror_y': True,
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
                    'solo': True,
                    'mute': False
                },
                {
                    'rule': 'Day&Night',
                    'age_palette': 'Blue->Green->Yellow->Red',
                    'rms_palette': 'Fire',
                    'solo': False,
                    'mute': True
                }
            ]
        }
    }
    
    # Сохраняем тестовую конфигурацию
    with open('app_config.json', 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print("✅ Тестовая конфигурация слоев создана:")
    print(f"   - Количество слоев: {test_config['layers']['layer_count']}")
    print(f"   - Разные правила: {test_config['layers']['layers_different']}")
    print(f"   - Автосмена правил: {test_config['layers']['auto_rule_sec']} сек")
    print(f"   - Автосмена палитр: {test_config['layers']['auto_palette_sec']} сек")
    print(f"   - Зеркалирование: X={test_config['layers']['mirror_x']}, Y={test_config['layers']['mirror_y']}")
    
    for i, layer in enumerate(test_config['layers']['layer_settings']):
        status = []
        if layer['solo']: status.append("SOLO")
        if layer['mute']: status.append("MUTE")
        status_str = f" ({', '.join(status)})" if status else ""
        print(f"   - Слой {i+1}: {layer['rule']}, {layer['age_palette']} + {layer['rms_palette']}{status_str}")
    
    print("\n🔧 Конфигурация сохранена в app_config.json")
    print("📝 Теперь можно запустить GUI и HUD для проверки синхронизации настроек")

if __name__ == "__main__":
    test_layer_config_integration()