#!/usr/bin/env python3
"""
Тест расширенных HSV палитр для Guitar Life
"""

import colorsys
import math
import matplotlib.pyplot as plt
import numpy as np

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp01(t)

# Копируем наши новые HSV функции
def hue_rainbow_smooth_from_t(t: float):
    """Плавная радужная палитра через весь спектр HSV"""
    t = clamp01(t)
    h = 360.0 * (1.0 - t)  # От красного (0°) до фиолетового (360°)
    s = 1.0
    v = 1.0
    return h, s, v

def hue_sunset_from_t(t: float):
    """Закатная палитра: фиолетовый -> розовый -> оранжевый -> желтый"""
    t = clamp01(t)
    if t < 0.25:
        # Темно-фиолетовый к фиолетовому
        k = t / 0.25
        h = lerp(280.0, 300.0, k)
        s = 1.0
        v = lerp(0.3, 0.6, k)
    elif t < 0.5:
        # Фиолетовый к розовому
        k = (t - 0.25) / 0.25
        h = lerp(300.0, 320.0, k)
        s = lerp(1.0, 0.8, k)
        v = lerp(0.6, 0.9, k)
    elif t < 0.75:
        # Розовый к оранжевому
        k = (t - 0.5) / 0.25
        h = lerp(320.0, 30.0, k)
        s = lerp(0.8, 1.0, k)
        v = lerp(0.9, 1.0, k)
    else:
        # Оранжевый к желтому
        k = (t - 0.75) / 0.25
        h = lerp(30.0, 60.0, k)
        s = lerp(1.0, 0.8, k)
        v = 1.0
    return h, s, v

def hue_aurora_from_t(t: float):
    """Палитра северного сияния: зеленый -> синий -> фиолетовый -> розовый"""
    t = clamp01(t)
    if t < 0.33:
        # Зеленый к сине-зеленому
        k = t / 0.33
        h = lerp(120.0, 180.0, k)
        s = lerp(1.0, 0.8, k)
        v = lerp(0.7, 1.0, k)
    elif t < 0.66:
        # Сине-зеленый к синему
        k = (t - 0.33) / 0.33
        h = lerp(180.0, 240.0, k)
        s = lerp(0.8, 1.0, k)
        v = 1.0
    else:
        # Синий к фиолетово-розовому
        k = (t - 0.66) / 0.34
        h = lerp(240.0, 300.0, k)
        s = lerp(1.0, 0.9, k)
        v = lerp(1.0, 0.9, k)
    return h, s, v

def hue_volcano_from_t(t: float):
    """Вулканическая палитра: черный -> красный -> оранжевый -> желтый -> белый"""
    t = clamp01(t)
    if t < 0.2:
        # Черный к темно-красному
        k = t / 0.2
        h = 0.0
        s = 1.0
        v = lerp(0.05, 0.3, k)
    elif t < 0.4:
        # Темно-красный к красному
        k = (t - 0.2) / 0.2
        h = 0.0
        s = 1.0
        v = lerp(0.3, 0.8, k)
    elif t < 0.6:
        # Красный к оранжевому
        k = (t - 0.4) / 0.2
        h = lerp(0.0, 30.0, k)
        s = 1.0
        v = lerp(0.8, 1.0, k)
    elif t < 0.8:
        # Оранжевый к желтому
        k = (t - 0.6) / 0.2
        h = lerp(30.0, 60.0, k)
        s = lerp(1.0, 0.8, k)
        v = 1.0
    else:
        # Желтый к белому
        k = (t - 0.8) / 0.2
        h = 60.0
        s = lerp(0.8, 0.0, k)
        v = 1.0
    return h, s, v

def hue_cyberpunk_from_t(t: float):
    """Киберпанк палитра: фиолетовый -> розовый -> неоновый синий -> неоновый зеленый"""
    t = clamp01(t)
    if t < 0.25:
        # Темно-фиолетовый к фиолетовому
        k = t / 0.25
        h = 280.0
        s = 1.0
        v = lerp(0.4, 0.8, k)
    elif t < 0.5:
        # Фиолетовый к розовому
        k = (t - 0.25) / 0.25
        h = lerp(280.0, 320.0, k)
        s = 1.0
        v = lerp(0.8, 1.0, k)
    elif t < 0.75:
        # Розовый к неоновому синему
        k = (t - 0.5) / 0.25
        h = lerp(320.0, 200.0, k)
        s = 1.0
        v = 1.0
    else:
        # Неоновый синий к неоновому зеленому
        k = (t - 0.75) / 0.25
        h = lerp(200.0, 120.0, k)
        s = 1.0
        v = 1.0
    return h, s, v

def hsv_to_rgb(h, s, v):
    """Конвертация HSV в RGB"""
    # Конвертируем hue из градусов в диапазон 0-1
    h_norm = (h % 360.0) / 360.0
    return colorsys.hsv_to_rgb(h_norm, s, v)

def test_palettes():
    """Тестируем все новые палитры"""
    palettes = {
        'RainbowSmooth': hue_rainbow_smooth_from_t,
        'Sunset': hue_sunset_from_t,
        'Aurora': hue_aurora_from_t,
        'Volcano': hue_volcano_from_t,
        'Cyberpunk': hue_cyberpunk_from_t,
    }
    
    print("🎨 Тестирование расширенных HSV палитр")
    print("=" * 50)
    
    # Создаем тестовые значения t от 0 до 1
    t_values = np.linspace(0, 1, 10)
    
    for palette_name, palette_func in palettes.items():
        print(f"\n📋 {palette_name}:")
        print("   t    |    H°   |   S   |   V   |  RGB")
        print("-" * 45)
        
        for t in t_values:
            h, s, v = palette_func(t)
            r, g, b = hsv_to_rgb(h, s, v)
            r_int, g_int, b_int = int(r*255), int(g*255), int(b*255)
            print(f" {t:4.1f}  | {h:6.1f}° | {s:4.2f} | {s:4.2f} | #{r_int:02x}{g_int:02x}{b_int:02x}")
    
    print("\n✅ Тест палитр завершен!")
    print("\n💡 Новые палитры добавлены:")
    for name in palettes.keys():
        print(f"   - {name}")

def visual_test():
    """Создает визуальный тест палитр (если matplotlib доступен)"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        palettes = {
            'RainbowSmooth': hue_rainbow_smooth_from_t,
            'Sunset': hue_sunset_from_t,
            'Aurora': hue_aurora_from_t,
            'Volcano': hue_volcano_from_t,
            'Cyberpunk': hue_cyberpunk_from_t,
        }
        
        fig, axes = plt.subplots(len(palettes), 1, figsize=(12, 2*len(palettes)))
        if len(palettes) == 1:
            axes = [axes]
            
        t_values = np.linspace(0, 1, 100)
        
        for i, (name, func) in enumerate(palettes.items()):
            ax = axes[i]
            ax.set_title(f'{name} Palette', fontsize=14, fontweight='bold')
            
            for j, t in enumerate(t_values):
                h, s, v = func(t)
                r, g, b = hsv_to_rgb(h, s, v)
                
                rect = patches.Rectangle((j, 0), 1, 1, 
                                       facecolor=(r, g, b), 
                                       edgecolor='none')
                ax.add_patch(rect)
            
            ax.set_xlim(0, len(t_values))
            ax.set_ylim(0, 1)
            ax.set_xlabel('Age/RMS Progress →')
            ax.set_ylabel('')
            ax.set_yticks([])
        
        plt.tight_layout()
        plt.savefig('hsv_palettes_test.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("🖼️ Визуальный тест сохранен в hsv_palettes_test.png")
        
    except ImportError:
        print("⚠️ matplotlib не доступен, пропускаем визуальный тест")

if __name__ == "__main__":
    test_palettes()
    try:
        visual_test()
    except Exception as e:
        print(f"⚠️ Визуальный тест не удался: {e}")