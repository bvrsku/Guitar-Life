# ✅ Изменение расположения ползунка Palette Mix

## 🎯 Цель изменения
Переместить ползунок микса палитр (Palette Mix) из левой колонки в правую, расположив его под выбором режима RMS.

## 🔧 Внесенные изменения

### Файл: `guitar_life_patched_HUD (1).py`
**Метод:** `_create_single_layer_module()` (строки ~373-393)

#### До изменения:
```python
# RMS Mode комбобокс
module['controls']['rms_mode'] = UIComboBox(
    x_right, current_y, combo_width, control_height,
    f"RMS Mode", rms_mode_options, 0
)
current_y += 35

# Spawn Method комбобокс
module['controls']['spawn_method'] = UIComboBox(
    x_left, current_y, combo_width, control_height,
    f"Spawn", spawn_options, 0
)
current_y += 35

# Palette Mix слайдер (в левой колонке)
module['controls']['palette_mix'] = UISlider(
    x_left, current_y, slider_width, control_height,
    0.0, 1.0, 0.5, f"Palette Mix", "{:.2f}"
)
current_y += 35
```

#### После изменения:
```python
# RMS Mode комбобокс
module['controls']['rms_mode'] = UIComboBox(
    x_right, current_y, combo_width, control_height,
    f"RMS Mode", rms_mode_options, 0
)

# Palette Mix слайдер (перемещен в правую колонку под RMS Mode)
module['controls']['palette_mix'] = UISlider(
    x_right, current_y + 35, slider_width, control_height,
    0.0, 1.0, 0.5, f"Palette Mix", "{:.2f}"
)
current_y += 35

# Spawn Method комбобокс
module['controls']['spawn_method'] = UIComboBox(
    x_left, current_y, combo_width, control_height,
    f"Spawn", spawn_options, 0
)
current_y += 35
```

## 📋 Новое расположение элементов

### Левая колонка (x_left):
1. Age Palette (комбобокс)
2. Alpha Live (слайдер)
3. Alpha Old (слайдер) 
4. Max Age (слайдер)
5. Rule (комбобокс)
6. Blend Mode (комбобокс)
7. Spawn Method (комбобокс)
8. Solo/Mute (кнопки)

### Правая колонка (x_right):
1. RMS Palette (комбобокс)
2. Initial Cells % (слайдер)
3. RMS Mode (комбобокс)
4. **Palette Mix (слайдер)** ← Новое расположение

## 🎨 Логика размещения
Ползунок Palette Mix логически связан с палитрами RMS, поэтому его размещение в правой колонке под элементами управления RMS делает интерфейс более интуитивным:

- **RMS Palette** → выбор палитры для RMS
- **RMS Mode** → режим применения RMS
- **Palette Mix** → баланс между Age и RMS палитрами

## 🧪 Тестирование
Создан тестовый файл `test_palette_mix_position.py` для проверки нового расположения элементов в HUD.

## 📝 Функциональность
Все функции ползунка Palette Mix сохранены:
- Диапазон: 0.0 - 1.0
- Формат отображения: два знака после запятой
- Логика микширования палитр не изменена
- Обработка событий работает без изменений