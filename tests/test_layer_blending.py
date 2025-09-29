#!/usr/bin/env python3
"""
Тест наложения слоев - проверяем что все слои видны одновременно
"""

import json

def create_multilayer_test_config():
    """Создает конфигурацию с контрастными слоями для визуального тестирования"""
    
    test_config = {
        'layers': {
            'layer_count': 3,
            'layers_different': True,
            'auto_rule_sec': 0,  # Отключаем автосмену
            'auto_palette_sec': 0,
            'mirror_x': False,
            'mirror_y': False,
            'layer_settings': [
                {
                    'rule': 'Conway',
                    'age_palette': 'Fire',  # Красно-оранжевая палитра
                    'rms_palette': 'Fire',
                    'solo': False,
                    'mute': False
                },
                {
                    'rule': 'HighLife',
                    'age_palette': 'Ocean',  # Сине-зеленая палитра 
                    'rms_palette': 'Ocean',
                    'solo': False,
                    'mute': False
                },
                {
                    'rule': 'Day&Night',
                    'age_palette': 'Neon',  # Яркие цвета
                    'rms_palette': 'Neon', 
                    'solo': False,
                    'mute': False
                }
            ]
        }
    }
    
    with open('app_config.json', 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print("🎨 Создана конфигурация для тестирования наложения слоев:")
    print("   Слой 1: Conway + Fire (красно-оранжевый)")
    print("   Слой 2: HighLife + Ocean (сине-зеленый)")
    print("   Слой 3: Day&Night + Neon (яркие цвета)")
    print()
    print("✅ Теперь должны быть видны все 3 слоя одновременно!")
    print("🔍 Контрастные цвета помогут увидеть наложение")
    print()
    print("🎮 Рекомендации для тестирования:")
    print("   1. Запустите Guitar Life")
    print("   2. Откройте HUD ([H])")
    print("   3. Попробуйте Solo режимы для изоляции слоев")
    print("   4. Убедитесь что без Solo видны все слои")
    print("   5. Смотрите в консоль - должна быть отладочная информация")

if __name__ == "__main__":
    create_multilayer_test_config()