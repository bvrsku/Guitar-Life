#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Документация по отображению параметров в HUD
"""

# Импортируем для получения списков контролов
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def print_hud_documentation():
    """Выводит документацию по всем параметрам HUD"""
    
    print("🎛️ ДОКУМЕНТАЦИЯ HUD - ОТОБРАЖЕНИЕ ВСЕХ ПАРАМЕТРОВ")
    print("=" * 60)
    print()
    
    # AUDIO категория
    print("🔊 КАТЕГОРИЯ: AUDIO")
    print("-" * 30)
    audio_params = [
        ("gain", "Усиление звука", "Слайдер", "0.1 - 10.0x"),
        ("rms_strength", "Сила RMS", "Слайдер", "0 - 500"),
        ("color_rms_min", "RMS минимум", "Слайдер", "0.001 - 1.0"),
        ("color_rms_max", "RMS максимум", "Слайдер", "0.001 - 1.0"),
        ("pitch_tick_enable", "Частотная синхронизация", "Кнопка", "Вкл/Выкл"),
        ("pitch_tick_min", "Мин. частота", "Слайдер", "1 - 1000ms"),
        ("pitch_tick_max", "Макс. частота", "Слайдер", "1 - 1000ms"),
    ]
    
    for param, desc, control_type, range_info in audio_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    # VISUAL категория
    print("🎨 КАТЕГОРИЯ: VISUAL")
    print("-" * 30)
    visual_params = [
        ("global_v_mul", "Общая яркость", "Слайдер", "0.1 - 3.0x"),
        ("hue_offset", "Сдвиг оттенка", "Слайдер", "0 - 360°"),
        ("aging_speed", "Скорость старения", "Слайдер", "0.1 - 10.0x"),
        ("fade_start", "Начало затухания", "Слайдер", "1 - 500"),
        ("fade_sat_drop", "Потеря насыщенности", "Слайдер", "0 - 100%"),
        ("fade_val_drop", "Потеря яркости", "Слайдер", "0 - 100%"),
        ("max_age", "Максимальный возраст", "Слайдер", "60 - 300"),
        ("palette_invert", "Инверсия палитры", "Кнопка", "Вкл/Выкл"),
    ]
    
    for param, desc, control_type, range_info in visual_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    # LAYERS категория
    print("🏗️ КАТЕГОРИЯ: LAYERS")
    print("-" * 30)
    layer_params = [
        ("layer_count", "Количество слоев", "Слайдер", "1 - 5"),
        ("layer_select", "Выбор слоя", "Кнопки", "L1, L2, L3, L4, L5"),
        ("layer_rule", "Правило автомата", "Комбобокс", "Conway, HighLife, etc."),
        ("layer_age_palette", "Палитра возраста", "Комбобокс", "Fire, Ocean, Neon, etc."),
        ("layer_rms_palette", "Палитра RMS", "Комбобокс", "Fire, Ocean, Rainbow, etc."),
        ("layer_alpha", "Прозрачность", "Слайдер", "0.0 - 1.0"),
        ("layer_blend_mode", "Режим смешивания", "Комбобокс", "normal, additive, screen, etc."),
        ("layer_mute", "Отключить слой", "Кнопка", "Вкл/Выкл"),
        ("layer_solo", "Изолировать слой", "Кнопка", "Вкл/Выкл"),
        ("layer_mirror_x", "Зеркало по X", "Кнопка", "Вкл/Выкл"),
        ("layer_mirror_y", "Зеркало по Y", "Кнопка", "Вкл/Выкл"),
    ]
    
    for param, desc, control_type, range_info in layer_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    # EFFECTS категория
    print("✨ КАТЕГОРИЯ: EFFECTS")
    print("-" * 30)
    effect_params = [
        ("fx_scanlines", "Эффект сканлайнов", "Кнопка", "Вкл/Выкл"),
        ("fx_scan_strength", "Сила сканлайнов", "Слайдер", "0.0 - 1.0"),
        ("fx_posterize", "Постеризация", "Кнопка", "Вкл/Выкл"),
        ("fx_poster_levels", "Уровни постеризации", "Слайдер", "2 - 16"),
        ("fx_dither", "Дизеринг", "Кнопка", "Вкл/Выкл"),
        ("fx_pixelate", "Пикселизация", "Кнопка", "Вкл/Выкл"),
        ("fx_pixel_size", "Размер пикселей", "Слайдер", "1 - 8"),
        ("fx_blur", "Размытие движения", "Кнопка", "Вкл/Выкл"),
    ]
    
    for param, desc, control_type, range_info in effect_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    # PERFORMANCE категория
    print("⚡ КАТЕГОРИЯ: PERFORMANCE")
    print("-" * 30)
    perf_params = [
        ("tick_ms", "Скорость обновления", "Слайдер", "1 - 5000ms"),
        ("perf_max_age", "Производительный возраст", "Слайдер", "1 - 1000"),
        ("max_cells_percent", "Макс. заполнение", "Слайдер", "10 - 100%"),
        ("soft_clear_threshold", "Порог очистки", "Слайдер", "50 - 95%"),
        ("age_bias", "Приоритет возраста", "Слайдер", "0 - 100%"),
        ("soft_clear_enable", "Автоочистка", "Кнопка", "Вкл/Выкл"),
    ]
    
    for param, desc, control_type, range_info in perf_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    # ACTIONS категория  
    print("🎬 КАТЕГОРИЯ: ACTIONS")
    print("-" * 30)
    action_params = [
        ("clear_type", "Тип очистки", "Комбобокс", "Полная, Частичная, По возрасту, Случайная"),
        ("soft_mode", "Режим очистки", "Комбобокс", "Удалять, Затухание, Затухание+удаление"),
        ("clear_partial_percent", "Процент частичной", "Слайдер", "10 - 90%"),
        ("clear_age_threshold", "Порог возраста", "Слайдер", "5 - 100"),
        ("clear_random_percent", "Процент случайной", "Слайдер", "10 - 70%"),
        ("clear", "Очистить", "Кнопка", "Действие"),
        ("random_pattern", "Случайный паттерн", "Кнопка", "Действие"),
        ("save_preset", "Сохранить пресет", "Кнопка", "Действие"),
        ("load_preset", "Загрузить пресет", "Кнопка", "Действие"),
        ("reset_defaults", "Сброс настроек", "Кнопка", "Действие"),
        ("joy_division", "Joy Division эффект", "Кнопка", "Действие"),
        ("conway_gliders", "Планеры Конвея", "Кнопка", "Действие"),
        ("mirror_x", "Глобальное зеркало X", "Кнопка", "Вкл/Выкл"),
        ("mirror_y", "Глобальное зеркало Y", "Кнопка", "Вкл/Выкл"),
    ]
    
    for param, desc, control_type, range_info in action_params:
        print(f"   • {param:<20} {desc:<25} [{control_type:<8}] {range_info}")
    print()
    
    print("📊 СТАТИСТИКА")
    print("-" * 30)
    
    total_audio = len(audio_params)
    total_visual = len(visual_params)
    total_layers = len(layer_params)
    total_effects = len(effect_params)
    total_perf = len(perf_params)
    total_actions = len(action_params)
    total_all = total_audio + total_visual + total_layers + total_effects + total_perf + total_actions
    
    print(f"   AUDIO:        {total_audio:2d} параметров")
    print(f"   VISUAL:       {total_visual:2d} параметров")
    print(f"   LAYERS:       {total_layers:2d} параметров")
    print(f"   EFFECTS:      {total_effects:2d} параметров")
    print(f"   PERFORMANCE:  {total_perf:2d} параметров")
    print(f"   ACTIONS:      {total_actions:2d} параметров")
    print(f"   " + "-" * 25)
    print(f"   ВСЕГО:        {total_all:2d} параметров")
    print()
    
    print("🎛️ ТИПЫ КОНТРОЛОВ")
    print("-" * 30)
    
    # Подсчитываем типы контролов
    all_params = audio_params + visual_params + layer_params + effect_params + perf_params + action_params
    
    sliders = sum(1 for _, _, control_type, _ in all_params if control_type == "Слайдер")
    buttons = sum(1 for _, _, control_type, _ in all_params if control_type == "Кнопка")
    combos = sum(1 for _, _, control_type, _ in all_params if control_type == "Комбобокс")
    special = sum(1 for _, _, control_type, _ in all_params if control_type == "Кнопки")
    
    print(f"   Слайдеры:     {sliders:2d}")
    print(f"   Кнопки:       {buttons:2d}")
    print(f"   Комбобоксы:   {combos:2d}")
    print(f"   Специальные:  {special:2d}")
    print()
    
    print("✅ ВСЕ ПАРАМЕТРЫ ОТОБРАЖАЮТСЯ В HUD!")
    print("🎮 Используйте клавиши 1-6 или клики по вкладкам для навигации")
    print("📜 Колесо мыши для прокрутки в каждой категории")

if __name__ == "__main__":
    print_hud_documentation()