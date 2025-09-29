#!/usr/bin/env python3
"""
Упрощенный тест обработчика параметров
"""

class MockApp:
    """Имитация класса App для тестирования"""
    def __init__(self):
        # Инициализируем все параметры визуализации
        self.global_v_mul = 1.0
        self.hue_offset = 0
        self.aging_speed = 1.0
        self.fade_start = 60
        self.fade_sat_drop = 70
        self.fade_val_drop = 60
        self.max_age = 120
        self.tick_ms = 100
        self.rms_strength = 100
        self.gain = 1.0
        self.sel = {'clear_rms': 0.1}
        self.color_rms_min = 0.05
        self.color_rms_max = 0.9
        self.soft_kill_rate = 5
        self.soft_fade_floor = 0.1
        self.soft_fade_down = 10
        self.soft_fade_up = 20
        self.max_cells_percent = 80
        self.soft_clear_threshold = 50

    def on_hud_parameter_change(self, param_name: str, value):
        """Копия обработчика из основного приложения"""
        # Более информативный вывод
        if param_name.startswith('fx_'):
            fx_name = param_name[3:]
            status = "ON" if value else "OFF"
            print(f"🎨 FX {fx_name.upper()}: {status}")
        elif isinstance(value, bool):
            status = "✓" if value else "✗"
            print(f"⚙️ {param_name}: {status}")
        else:
            print(f"🎛️ {param_name}: {value}")
        
        # Защита от некорректных значений
        try:
            # Обновляем параметры приложения
            if param_name == 'tick_ms':
                self.tick_ms = int(max(1, min(5000, float(value))))
            elif param_name == 'rms_strength':
                self.rms_strength = int(max(0, min(500, float(value))))
            elif param_name == 'gain':
                self.gain = float(max(0.1, min(10.0, float(value))))
            elif param_name == 'max_age':
                self.max_age = int(max(1, min(1000, float(value))))
            elif param_name == 'aging_speed':
                self.aging_speed = float(max(0.1, min(10.0, float(value))))
            elif param_name == 'global_v_mul':
                self.global_v_mul = float(max(0.1, min(3.0, float(value))))
            elif param_name == 'hue_offset':
                self.hue_offset = float(max(0, min(360, float(value))))
            elif param_name == 'fade_sat_drop':
                self.fade_sat_drop = float(max(0, min(100, float(value))))
            elif param_name == 'fade_val_drop':
                self.fade_val_drop = float(max(0, min(100, float(value))))
            elif param_name == 'fade_start':
                self.fade_start = int(max(1, min(500, float(value))))
            elif param_name == 'clear_rms':
                self.sel['clear_rms'] = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'color_rms_min':
                self.color_rms_min = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'color_rms_max':
                self.color_rms_max = float(max(0.001, min(1.0, float(value))))
            elif param_name == 'soft_kill_rate':
                self.soft_kill_rate = int(max(0, min(100, float(value))))
            elif param_name == 'soft_fade_floor':
                self.soft_fade_floor = float(max(0.0, min(1.0, float(value))))
            elif param_name == 'soft_fade_down':
                self.soft_fade_down = int(max(1, min(100, float(value))))
            elif param_name == 'soft_fade_up':
                self.soft_fade_up = int(max(1, min(100, float(value))))
            elif param_name == 'max_cells_percent':
                self.max_cells_percent = int(max(10, min(100, float(value))))
            elif param_name == 'soft_clear_threshold':
                self.soft_clear_threshold = int(max(10, min(100, float(value))))
            else:
                print(f"⚠️ Неизвестный параметр: {param_name}")
                return False
                
            return True
        except Exception as e:
            print(f"❌ Ошибка обработки {param_name}: {e}")
            return False

# Тестирование
print("🧪 Тестирование обработчика параметров...")
print("=" * 50)

app = MockApp()

# Тестовые параметры из VISUAL категории
visual_params = {
    'global_v_mul': 2.5,
    'hue_offset': 180,
    'aging_speed': 5.0,
    'fade_start': 100,
    'fade_sat_drop': 50,
    'fade_val_drop': 40,
    'max_age': 200,
}

print("📊 Начальные значения:")
for param in visual_params.keys():
    initial_value = getattr(app, param)
    print(f"  {param}: {initial_value}")

print("\n🔄 Тестируем изменение параметров...")

success_count = 0
total_count = len(visual_params)

for param, test_value in visual_params.items():
    print(f"\n🎛️ Тестируем {param} = {test_value}")
    
    # Сохраняем старое значение
    old_value = getattr(app, param)
    
    # Применяем изменение
    success = app.on_hud_parameter_change(param, test_value)
    
    # Проверяем новое значение
    new_value = getattr(app, param)
    
    if success and abs(float(new_value) - float(test_value)) < 0.01:
        print(f"  ✅ {param}: {old_value} → {new_value} (успешно)")
        success_count += 1
    else:
        print(f"  ❌ {param}: {old_value} → {new_value} (ОШИБКА, ожидалось {test_value})")

print(f"\n📈 Результат: {success_count}/{total_count} параметров применено успешно")

if success_count == total_count:
    print("✅ Все параметры VISUAL категории обрабатываются правильно!")
    print("🔍 Проблема может быть в том, что параметры не используются при рендеринге.")
else:
    print("❌ Есть проблемы с обработкой параметров!")

print("\n🎨 Проверяем использование параметров в рендеринге...")
print("(Для этого нужно проверить код рендеринга в основном приложении)")

print("\n💡 Рекомендации:")
print("1. Убедитесь, что CyberHUD вызывает on_parameter_change при изменении слайдеров")
print("2. Проверьте, что параметры используются в методах рендеринга")
print("3. Убедитесь, что update_callbacks() вызывается после инициализации HUD")