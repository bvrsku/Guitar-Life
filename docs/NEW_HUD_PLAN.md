# Guitar Life - Новый Киберпанк HUD План

## 🎯 Концепция нового HUD

**Стиль**: Киберпанк (темно-зеленый, неоновые акценты)
**Структура**: Категоризированные панели с современной навигацией
**Функциональность**: Полный доступ ко всем параметрам приложения

## 📋 Категории параметров

### 🔊 AUDIO
- **gain** - Audio gain multiplier (0.1 - 10.0)
- **rms_strength** - RMS influence strength (0 - 500)
- **color_rms_min/max** - RMS range for colors
- **pitch_tick_enable** - Enable pitch-based timing
- **pitch_tick_min/max** - Pitch timing range

### 🎨 VISUAL
- **global_v_mul** - Global brightness multiplier (0.1 - 3.0)
- **hue_offset** - Global hue shift (0 - 360°)
- **fade_start** - Age when fading starts (1 - 500)
- **fade_sat_drop** - Saturation drop % (0 - 100)
- **fade_val_drop** - Value drop % (0 - 100)
- **aging_speed** - Cell aging multiplier (0.1 - 10.0)

### 🏗️ LAYERS
- **layer_count** - Number of layers (1 - 5)
- Per-layer controls:
  - **rule** - Cellular automata rule
  - **age_palette** - Age-based color palette
  - **rms_palette** - RMS-based color palette
  - **color_mode** - Color generation mode
  - **rms_mode** - RMS application mode
  - **alpha_live/old** - Transparency levels
  - **solo/mute** - Layer visibility

### ✨ EFFECTS
- **fx.scanlines** - CRT scanlines effect
- **fx.scan_strength** - Scanlines intensity
- **fx.posterize** - Color posterization
- **fx.poster_levels** - Posterization levels
- **fx.dither** - Ordered dithering
- **fx.pixelate** - Pixelation effect
- **fx.blur** - Motion blur

### ⚡ PERFORMANCE
- **tick_ms** - Simulation speed (1 - 5000ms)
- **max_age** - Maximum cell age (1 - 1000)
- **max_cells_percent** - Grid fill limit % (10 - 100)
- **soft_clear_threshold** - Auto-clear trigger % (50 - 95)

### 🎮 ACTIONS
- **clear_type** - Clear mode selector
- **soft_mode** - Soft clear behavior
- **mirror_x/y** - Symmetry mirrors
- **auto_rule_sec** - Auto rule cycling
- **auto_palette_sec** - Auto palette cycling
- Action buttons: Clear, Random, Test, Reset, Joy Division

## 🎨 Дизайн-схема

```
┌─────────────────────────────┐
│ ◉ GUITAR LIFE CONTROL      │ ← Header
├─────────────────────────────┤
│ [AUDIO] [VISUAL] [LAYERS]   │ ← Category tabs
│ [EFFECTS] [PERF] [ACTIONS]  │
├─────────────────────────────┤
│ ████████████████████████████│ ← Content area
│ │ Gain: ████████▌    2.5x │ │   with sliders,
│ │ RMS:  ████▌        100  │ │   buttons,
│ │ ┌─────────────────────┐ │ │   comboboxes
│ │ │ Clear Type: [Full▼] │ │ │
│ │ └─────────────────────┘ │ │
│ ████████████████████████████│
├─────────────────────────────┤
│ Rule: HighLife | FPS: 120   │ ← Status bar
│ ΔT: 8.3ms | Cells: 4,434    │
└─────────────────────────────┘
```

## 🎯 Ключевые особенности

1. **Категорная навигация** - табы для группировки параметров
2. **Киберпанк стиль** - темно-зеленая тема с неоновыми акцентами
3. **Полная функциональность** - доступ ко всем 50+ параметрам
4. **Интуитивный интерфейс** - логическая группировка элементов
5. **Современный вид** - анимации, градиенты, подсветка
6. **Компактность** - оптимальное использование пространства

## 📊 Технические требования

- Совместимость с текущим API `on_hud_parameter_change`
- Поддержка скроллинга для больших категорий
- Сохранение всех текущих функций
- Улучшенная производительность рендеринга
- Адаптивность к изменению размеров