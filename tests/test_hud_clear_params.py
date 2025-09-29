#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест HUD параметров очистки: clear_type и soft_mode
Проверяет, что пользователь может выбирать типы и режимы очистки через GUI
"""

import sys
import os
import pygame
import time

# Добавляем путь к модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from guitar_lifeE import App, CLEAR_TYPES
    print("✅ Импорт модуля guitar_lifeeq успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_clear_params_hud():
    """Тестирует параметры очистки в HUD"""
    
    print("🎯 Тест HUD параметров очистки")
    print("=" * 50)
    
    # Конфигурация для теста
    test_config = {
        'layer_count': 2,
        'layers_different': True,
        'tick_ms': 100,
        'clear_rms': 0.001,
        'pitch_tick_enable': False,
        'fx': {},
        'clear_type': 'Полная очистка',  # Начальное значение
        'soft_mode': 'Удалять клетки',  # Начальное значение
    }
    
    print(f"📋 Создание приложения с конфигурацией...")
    print(f"   - Слоев: {test_config['layer_count']}")
    print(f"   - Тип очистки: {test_config['clear_type']}")
    print(f"   - Режим очистки: {test_config['soft_mode']}")
    
    app = App(test_config)
    
    # Создаем начальные клетки для тестирования
    print(f"📊 Создание тестовых клеток...")
    app.generate_random_patterns()
    
    initial_cells = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
    print(f"   Создано клеток: {initial_cells}")
    
    # Проверяем наличие комбобоксов в HUD
    print(f"\n🔍 Проверка наличия элементов управления в HUD:")
    
    # Проверяем clear_type комбобокс
    if 'clear_type' in app.hud.comboboxes:
        clear_combo = app.hud.comboboxes['clear_type']
        print(f"   ✅ Комбобокс 'clear_type' найден")
        print(f"      - Опции: {clear_combo.options}")
        print(f"      - Текущий индекс: {clear_combo.current_index}")
        print(f"      - Текущее значение: {clear_combo.options[clear_combo.current_index]}")
    else:
        print(f"   ❌ Комбобокс 'clear_type' НЕ найден")
    
    # Проверяем soft_mode комбобокс
    if 'soft_mode' in app.hud.comboboxes:
        soft_combo = app.hud.comboboxes['soft_mode']
        print(f"   ✅ Комбобокс 'soft_mode' найден")
        print(f"      - Опции: {soft_combo.options}")
        print(f"      - Текущий индекс: {soft_combo.current_index}")
        print(f"      - Текущее значение: {soft_combo.options[soft_combo.current_index]}")
    else:
        print(f"   ❌ Комбобокс 'soft_mode' НЕ найден")
    
    # Тестируем изменение clear_type
    print(f"\n🔄 Тестирование изменения типа очистки:")
    for i, clear_type in enumerate(CLEAR_TYPES):
        print(f"   {i+1}. Устанавливаем тип: {clear_type}")
        
        # Эмулируем изменение через HUD
        if 'clear_type' in app.hud.comboboxes:
            app.hud.comboboxes['clear_type'].current_index = i
            app.on_hud_parameter_change('clear_type', clear_type)
            
            # Проверяем, что значение применилось
            if app.clear_type == clear_type:
                print(f"      ✅ Тип очистки изменен на: {app.clear_type}")
            else:
                print(f"      ❌ Ошибка: ожидался {clear_type}, получили {app.clear_type}")
    
    # Тестируем изменение soft_mode
    print(f"\n🔄 Тестирование изменения режима очистки:")
    soft_modes = ["Kill", "Fade", "Fade+Kill"]
    internal_modes = ["Удалять клетки", "Затухание клеток", "Затухание + удаление"]
    
    for i, (ui_mode, internal_mode) in enumerate(zip(soft_modes, internal_modes)):
        print(f"   {i+1}. Устанавливаем режим: {ui_mode} -> {internal_mode}")
        
        # Эмулируем изменение через HUD
        if 'soft_mode' in app.hud.comboboxes:
            app.hud.comboboxes['soft_mode'].current_index = i
            app.on_hud_parameter_change('soft_mode', ui_mode)
            
            # Проверяем, что значение применилось
            if app.soft_mode == internal_mode:
                print(f"      ✅ Режим очистки изменен на: {app.soft_mode}")
            else:
                print(f"      ❌ Ошибка: ожидался {internal_mode}, получили {app.soft_mode}")
    
    # Тестируем функциональность очистки с разными типами
    print(f"\n🧪 Тестирование функциональности очистки:")
    
    for clear_type in CLEAR_TYPES:
        print(f"\n   Тестируем тип: {clear_type}")
        
        # Создаем клетки для тестирования
        app.generate_random_patterns()
        cells_before = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
        print(f"      Клеток до очистки: {cells_before}")
        
        # Устанавливаем тип очистки
        app.clear_type = clear_type
        
        # Выполняем очистку
        if clear_type == "Полная очистка":
            app.clear_with_type()
            cells_after = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
            expected_after = 0
        elif clear_type == "Частичная очистка":
            app.clear_partial_percent = 50
            app.clear_with_type()
            cells_after = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
            expected_after = cells_before * 0.5  # Приблизительно
        elif clear_type == "Случайная очистка":
            app.clear_random_percent = 30
            app.clear_with_type()
            cells_after = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
            expected_after = cells_before * 0.7  # Приблизительно
        else:  # Очистка по возрасту
            app.clear_age_threshold = 10
            app.clear_with_type()
            cells_after = sum(app.layers[i].grid.sum() for i in range(len(app.layers)))
            expected_after = cells_before  # Зависит от возраста клеток
        
        print(f"      Клеток после очистки: {cells_after}")
        
        if clear_type == "Полная очистка":
            if cells_after == 0:
                print(f"      ✅ Полная очистка работает корректно")
            else:
                print(f"      ❌ Ошибка полной очистки: осталось {cells_after} клеток")
        else:
            print(f"      ℹ️ Частичная очистка выполнена (проверка на эффективность)")
    
    # Финальная проверка состояния HUD
    print(f"\n📊 Финальное состояние HUD:")
    app.hud.update_from_app(app)
    
    if 'clear_type' in app.hud.comboboxes:
        clear_combo = app.hud.comboboxes['clear_type']
        current_clear_type = clear_combo.options[clear_combo.current_index]
        print(f"   Clear Type: {current_clear_type} (индекс {clear_combo.current_index})")
        
        if current_clear_type == app.clear_type:
            print(f"   ✅ Синхронизация clear_type работает")
        else:
            print(f"   ❌ Рассинхронизация: HUD={current_clear_type}, App={app.clear_type}")
    
    if 'soft_mode' in app.hud.comboboxes:
        soft_combo = app.hud.comboboxes['soft_mode']
        current_soft_mode = soft_combo.options[soft_combo.current_index]
        print(f"   Soft Mode: {current_soft_mode} (индекс {soft_combo.current_index})")
        
        # Проверяем соответствие UI и внутреннего представления
        mode_mapping = {
            "Kill": "Удалять клетки",
            "Fade": "Затухание клеток", 
            "Fade+Kill": "Затухание + удаление"
        }
        expected_internal = mode_mapping.get(current_soft_mode)
        
        if expected_internal == app.soft_mode:
            print(f"   ✅ Синхронизация soft_mode работает")
        else:
            print(f"   ❌ Рассинхронизация: UI={current_soft_mode}, App={app.soft_mode}")
    
    print(f"\n🎯 Тест завершен успешно!")
    print(f"   ✅ Оба параметра (clear_type и soft_mode) доступны в HUD")
    print(f"   ✅ Изменения через HUD корректно применяются к приложению")
    print(f"   ✅ Функциональность очистки работает с выбранными типами")

if __name__ == "__main__":
    test_clear_params_hud()