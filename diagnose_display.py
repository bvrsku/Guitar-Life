#!/usr/bin/env python3
"""
Прямая диагностика проблемы отображения
"""

import numpy as np
import subprocess
import sys
import os

def diagnose_display_issue():
    """Диагностика проблемы с отображением"""
    
    print("🔍 Диагностика проблемы с отображением клеток")
    print("=" * 50)
    
    # Меняем директорию на Guitar-Life если нужно
    if not os.path.exists('guitar_life.py'):
        guitar_life_dir = r'c:\REPOS\Guitar-Life'
        if os.path.exists(guitar_life_dir):
            os.chdir(guitar_life_dir)
            print(f"📁 Сменили директорию на: {guitar_life_dir}")
    
    # Тестируем импорт и создание слоев
    try:
        print("1. Импорт модулей...")
        import guitar_life
        from guitar_life import App, Layer
        print("   ✅ Импорт успешен")
        
        print("2. Создание конфигурации...")
        # Создаем такую же конфигурацию как в main()
        config = {
            'layer_count': 1,
            'layers_cfg': [{
                'rule': 'Conway',
                'age_palette': 'Fire',
                'rms_palette': 'Fire',
                'color_mode': 'Возраст + RMS',
                'alpha_live': 255,
                'alpha_old': 128,
                'mix': 'Normal',
                'solo': False,
                'mute': False,
            }]
        }
        print("   ✅ Конфигурация создана")
        
        print("3. Создание приложения...")
        app = App(config)
        print(f"   ✅ Приложение создано с {len(app.layers)} слоями")
        
        print("3. Проверка слоев:")
        for i, layer in enumerate(app.layers):
            print(f"   Слой {i}: solo={layer.solo}, mute={layer.mute}, клеток={np.sum(layer.grid)}")
        
        print("4. Дополнительная проверка начальных клеток...")
        total_initial = sum(np.sum(layer.grid) for layer in app.layers)
        print(f"   Всего начальных клеток: {total_initial}")
        
        print("5. Создание тестового паттерна...")
        app.create_test_pattern()
        print(f"   ✅ Паттерн создан")
        
        print("6. Проверка клеток после создания:")
        total_cells = 0
        for i, layer in enumerate(app.layers):
            cells = np.sum(layer.grid)
            total_cells += cells
            print(f"   Слой {i}: клеток={cells}, solo={layer.solo}, mute={layer.mute}")
        
        if total_cells == 0:
            print("   ❌ ПРОБЛЕМА: Нет живых клеток!")
            return
        else:
            print(f"   ✅ Всего живых клеток: {total_cells}")
        
        print("7. Тест логики Solo/Mute...")
        solos = [L for L in app.layers if L.solo and not L.mute]
        layers = solos if solos else [L for L in app.layers if not L.mute]
        print(f"   Слоев с solo: {len(solos)}")
        print(f"   Слоев для рендеринга: {len(layers)}")
        
        if len(layers) == 0:
            print("   ❌ ПРОБЛЕМА: Нет слоев для рендеринга!")
            
            # Проверяем почему
            for i, layer in enumerate(app.layers):
                if layer.mute:
                    print(f"     Слой {i} заглушен (mute=True)")
                if layer.solo:
                    print(f"     Слой {i} в режиме solo")
                    
            # ИСПРАВЛЯЕМ проблему
            print("   🔧 Исправляем проблему...")
            for layer in app.layers:
                layer.mute = False
                layer.solo = False
            print("   ✅ Все слои разглушены")
            
        else:
            print(f"   ✅ {len(layers)} слоев будут отрендерены")
            
        print("8. Тест создания изображения...")
        layer = app.layers[0]
        cfg = {
            "rms_strength": 100, "fade_start": 60, "max_age": 120,
            "fade_sat_drop": 70, "fade_val_drop": 60, "global_v_mul": 1.0,
            "color_rms_min": 0.004, "color_rms_max": 0.3
        }
        
        img = guitar_life.build_color_image(
            layer.grid, layer.age, layer.color_mode, 0.1, 440.0, cfg,
            layer.age_palette, layer.rms_palette
        )
        
        print(f"   Изображение: {img.shape}")
        print(f"   Максимальное значение: {np.max(img)}")
        print(f"   Ненулевых пикселей: {np.count_nonzero(img)}")
        
        if np.max(img) == 0:
            print("   ❌ ПРОБЛЕМА: Изображение полностью черное!")
        else:
            print("   ✅ Изображение содержит цветные пиксели")
            
        print("\n9. Попытка запуска приложения...")
        print("   Одну секунду рендеринга...")
        app.render(0.1, 440.0)
        print("   ✅ Рендеринг завершен без ошибок")
            
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_display_issue()
    print("\n" + "="*50)
    print("🎯 РЕЗЮМЕ:")
    print("   Если все тесты прошли успешно, проблема может быть:")
    print("   1. В конфигурации слоев (Solo/Mute)")
    print("   2. В инициализации при старте приложения")
    print("   3. В чтении настроек из app_config.json")
    input("\nНажмите Enter для завершения...")