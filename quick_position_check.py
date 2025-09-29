#!/usr/bin/env python3
"""
Быстрая проверка позиций элементов в HUD
"""

try:
    # Импортируем из основного файла
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from guitar_life_patched_HUD import HUD
    import pygame
    
    # Создаем минимальный HUD для тестирования
    pygame.init()
    font = pygame.font.SysFont("consolas", 16)
    hud = HUD(font, 800, layer_count=1)
    
    # Проверяем позиции элементов в первом модуле
    if hud.layer_modules:
        module = hud.layer_modules[0]
        controls = module['controls']
        
        print("🔍 Проверка позиций элементов управления:")
        print(f"Panel X: {hud.panel_x}")
        
        if 'rms_mode' in controls and 'palette_mix' in controls:
            rms_mode = controls['rms_mode']
            palette_mix = controls['palette_mix']
            
            print(f"RMS Mode: x={rms_mode.x}, y={rms_mode.y}")
            print(f"Palette Mix: x={palette_mix.x}, y={palette_mix.y}")
            
            x_left = hud.panel_x + 10
            x_right = hud.panel_x + 200
            
            print(f"x_left = {x_left}, x_right = {x_right}")
            
            if palette_mix.x == x_right:
                print("✅ Palette Mix находится в правой колонке!")
            elif palette_mix.x == x_left:
                print("❌ Palette Mix все еще в левой колонке")
            else:
                print(f"⚠️  Palette Mix на неожиданной позиции: {palette_mix.x}")
                
            if palette_mix.y > rms_mode.y:
                print("✅ Palette Mix находится ниже RMS Mode")
            else:
                print("❌ Palette Mix НЕ находится ниже RMS Mode")
        else:
            print("❌ Не найдены элементы rms_mode или palette_mix")
    else:
        print("❌ Нет модулей слоев")
        
    pygame.quit()
    print("\n🎯 Проверка завершена!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()