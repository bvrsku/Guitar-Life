# This file has been deleted.
#!/usr/bin/env python3
"""
Быстрый тест исправленного расположения Palette Mix
"""

import pygame
import sys

try:
    from guitar_life_patched_HUD import HUD, SimpleColors
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест исправленного HUD")
    font = pygame.font.SysFont("consolas", 16)
    
    # Создаем HUD с одним слоем
    hud = HUD(font, 600, layer_count=1)
    hud.visible = True
    
    print("✅ HUD создан успешно")
    print(f"📍 Панель находится на x={hud.panel_x}")
    
    if hud.layer_modules:
        module = hud.layer_modules[0]
        controls = module['controls']
        
        print("\n🔍 Проверка позиций элементов:")
        
        # Проверяем ключевые элементы
        elements_to_check = ['age_palette', 'rms_palette', 'rms_mode', 'palette_mix', 'spawn_method']
        
        for elem_name in elements_to_check:
            if elem_name in controls:
                control = controls[elem_name]
                x_pos = "LEFT" if control.x < hud.panel_x + 150 else "RIGHT"
                print(f"  {elem_name}: x={control.x}, y={control.y} ({x_pos} колонка)")
            else:
                print(f"  {elem_name}: НЕ НАЙДЕН")
        
        # Специальная проверка Palette Mix
        if 'palette_mix' in controls and 'rms_mode' in controls:
            palette_mix = controls['palette_mix']
            rms_mode = controls['rms_mode']
            
            x_right = hud.panel_x + 200
            
            if palette_mix.x == x_right:
                print(f"\n✅ Palette Mix в правой колонке (x={palette_mix.x})")
            else:
                print(f"\n❌ Palette Mix НЕ в правой колонке (x={palette_mix.x}, должно быть {x_right})")
            
            if palette_mix.y > rms_mode.y:
                print(f"✅ Palette Mix ниже RMS Mode ({palette_mix.y} > {rms_mode.y})")
            else:
                print(f"❌ Palette Mix НЕ ниже RMS Mode ({palette_mix.y} vs {rms_mode.y})")
    
    pygame.quit()
    print("\n🎯 Проверка завершена!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()