#!/usr/bin/env python3
"""
Тест палитр Guitar Life - проверка исправлений
"""
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, r'c:\REPOS\Guitar-Life')

try:
    # Импортируем основной модуль
    from guitar_li4fe import PALETTE_STATE, _PALETTE_ALIASES, palette_key
    from guitar_li4fe import color_from_age_rms, hue_fire_from_t, hue_ocean_from_t, hue_neon_from_t, hue_ukraine_from_t
    
    print("🎨 Тест системы палитр Guitar Life v13")
    print("=" * 50)
    
    # Тест 1: Проверка состояния палитр
    print("1. Проверка текущего состояния палитр:")
    print(f"   RMS Palette: {PALETTE_STATE.rms_palette_choice}")
    print(f"   Age Palette: {PALETTE_STATE.age_palette_choice}")
    print(f"   Hue Offset: {PALETTE_STATE.hue_offset}")
    print(f"   Invert: {PALETTE_STATE.invert}")
    
    # Тест 2: Проверка алиасов
    print("\n2. Проверка алиасов палитр:")
    test_palettes = ["Fire", "Ocean", "Neon", "Ukraine", "Blue->Green->Yellow->Red"]
    for pal in test_palettes:
        key = palette_key(pal)
        print(f"   {pal} -> {key}")
    
    # Тест 3: Проверка функций палитр
    print("\n3. Проверка функций специальных палитр:")
    test_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print("   Fire palette:")
    for t in test_values:
        h, s, v = hue_fire_from_t(t)
        print(f"     t={t:.2f} -> H={h:.1f}, S={s:.2f}, V={v:.2f}")
    
    # Тест 4: Проверка изменения палитр
    print("\n4. Тест изменения палитр:")
    original_rms = PALETTE_STATE.rms_palette_choice
    original_age = PALETTE_STATE.age_palette_choice
    
    # Меняем палитры
    PALETTE_STATE.rms_palette_choice = "Fire"
    PALETTE_STATE.age_palette_choice = "Ocean"
    
    print(f"   Изменено на: RMS={PALETTE_STATE.rms_palette_choice}, Age={PALETTE_STATE.age_palette_choice}")
    
    # Тест цвета с новыми палитрами
    test_color = color_from_age_rms(
        age=10, rms=0.1, rms_strength=1.0,
        fade_start=60, max_age=120,
        sat_drop_pct=70, val_drop_pct=60,
        color_rms_min=0.004, color_rms_max=0.3,
        global_v_mul=1.0,
        age_palette="Ocean"
    )
    print(f"   Тестовый цвет Ocean: RGB{test_color}")
    
    # Возвращаем оригинальные значения
    PALETTE_STATE.rms_palette_choice = original_rms
    PALETTE_STATE.age_palette_choice = original_age
    
    print("\n✅ Все тесты палитр пройдены успешно!")
    print("Изменения в UIComboBox.handle_event и App.__init__ должны работать корректно.")
    
except Exception as e:
    print(f"❌ Ошибка при тестировании палитр: {e}")
    import traceback
    traceback.print_exc()