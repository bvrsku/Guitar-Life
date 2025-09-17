#!/usr/bin/env python3
"""
Тестовый скрипт для проверки modern_gui с редактором слоев
"""

from modern_gui import show_modern_gui

def test_gui():
    # Создаем тестовые устройства
    test_devices = [
        {'name': 'Тестовое устройство 1'},
        {'name': 'Тестовое устройство 2'},
        {'name': 'Микрофон (встроенный)'}
    ]
    
    print("Запускаем тестовый GUI с редактором слоев...")
    result = show_modern_gui(test_devices)
    
    if result:
        print("✅ GUI завершился успешно!")
        print(f"Выбранное устройство: {result['device']}")
        print(f"Количество слоев: {result['layer_count']}")
        print(f"Разные правила по слоям: {result['diff_per_layer']}")
        print(f"Автосмена правил: {result['auto_rule_sec']} сек")
        print(f"Автосмена палитр: {result['auto_palette_sec']} сек")
        print(f"Зеркалирование X: {result['mirror_x']}")
        print(f"Зеркалирование Y: {result['mirror_y']}")
        print(f"Количество слоев в конфигурации: {len(result['layers_cfg'])}")
        
        # Показываем настройки слоев
        for i, layer in enumerate(result['layers_cfg']):
            print(f"Слой {i+1}: {layer['rule']}, возраст={layer['age_palette']}, RMS={layer['rms_palette']}, solo={layer['solo']}, mute={layer['mute']}")
    else:
        print("❌ GUI был отменен")

if __name__ == "__main__":
    test_gui()