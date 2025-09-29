# Guitar Life - Руководство по рендерингу слоев

## Обзор системы рендеринга

Guitar Life использует многослойную систему рендеринга для создания сложных визуальных эффектов. Каждый слой представляет собой независимую сетку клеточного автомата с собственными параметрами генерации, цветовыми палитрами и режимами смешивания.

## Архитектура рендеринга

### Основные компоненты

```
Layer (Слой)
├── grid: np.ndarray          # Сетка живых/мертвых клеток
├── age: np.ndarray           # Возраст каждой клетки
├── color_mode: str           # Режим окрашивания
├── age_palette: str          # Палитра цветов по возрасту
├── rms_palette: str          # Палитра цветов по RMS
├── alpha_live: int           # Прозрачность живых клеток
├── alpha_old: int            # Прозрачность старых клеток
├── mix: str                  # Режим смешивания
└── solo/mute: bool           # Контроль видимости
```

### Этапы рендеринга

1. **Генерация цветового изображения** - Каждый слой преобразуется в RGB массив
2. **Применение палитр** - Цвета назначаются на основе возраста и аудио-данных
3. **Создание поверхности pygame** - RGB массив конвертируется в поверхность
4. **Масштабирование** - Поверхность масштабируется до размера пикселей
5. **Смешивание слоев** - Слои комбинируются с учетом режимов смешивания
6. **Применение эффектов** - Post-processing эффекты (bloom, scanlines, etc.)

## Лучшие практики рендеринга

### 1. Оптимизация памяти

#### ✅ Правильно:
```python
# Переиспользование буферов
class LayerRenderer:
    def __init__(self):
        self.color_buffer = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
        self.temp_buffer = np.zeros((GRID_H, GRID_W), dtype=np.float32)
    
    def render_layer(self, layer):
        # Переиспользуем существующие буферы
        np.copyto(self.color_buffer, 0)  # Очищаем буфер
        # ... рендеринг в существующий буфер
```

#### ❌ Неправильно:
```python
def render_layer(self, layer):
    # Создание новых массивов на каждом кадре
    color_img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)  # Плохо!
    temp_array = np.array(layer.grid, copy=True)  # Лишнее копирование!
```

### 2. Эффективное смешивание слоев

#### ✅ Группировка по режимам смешивания:
```python
def render_layers_efficiently(self, layers):
    # Группируем слои по режимам смешивания
    normal_layers = [l for l in layers if l.mix == "Normal"]
    additive_layers = [l for l in layers if l.mix == "Additive"]
    
    # Сначала рендерим Normal (быстрее)
    for layer in normal_layers:
        self.render_normal_layer(layer)
    
    # Затем Additive (медленнее, но меньше слоев)
    for layer in additive_layers:
        self.render_additive_layer(layer)
```

#### ❌ Смешанный порядок:
```python
def render_layers_inefficiently(self, layers):
    # Постоянное переключение между режимами смешивания
    for layer in layers:
        if layer.mix == "Normal":
            pygame.BLEND_ALPHA_SDL2  # Переключение режима
        else:
            pygame.BLEND_RGB_ADD     # Переключение режима
        # Каждое переключение замедляет рендеринг
```

### 3. Кэширование вычислений

#### ✅ Кэширование палитр:
```python
class PaletteManager:
    def __init__(self):
        self.palette_cache = {}
    
    def get_palette_colors(self, palette_name, rms_factor):
        cache_key = (palette_name, round(rms_factor, 2))
        if cache_key not in self.palette_cache:
            self.palette_cache[cache_key] = self.compute_palette(palette_name, rms_factor)
        return self.palette_cache[cache_key]
```

#### ✅ Детекция изменений:
```python
def has_layer_changed(self, layer, last_hash):
    current_hash = hash((
        layer.grid.tobytes(),
        layer.age.max(),
        layer.color_mode,
        layer.alpha_live
    ))
    return current_hash != last_hash
```

### 4. Управление производительностью

#### Адаптивное качество:
```python
class AdaptiveRenderer:
    def __init__(self):
        self.target_fps = 60
        self.quality_level = 1.0
        
    def render_frame(self, layers):
        start_time = time.perf_counter()
        
        # Адаптируем качество под производительность
        if self.current_fps < self.target_fps * 0.8:
            self.quality_level = max(0.5, self.quality_level - 0.1)
        elif self.current_fps > self.target_fps:
            self.quality_level = min(1.0, self.quality_level + 0.05)
        
        # Рендерим с адаптивным качеством
        self.render_with_quality(layers, self.quality_level)
```

#### Пропуск кадров при необходимости:
```python
def smart_frame_skip(self, target_fps=60):
    frame_time = 1.0 / target_fps
    actual_time = time.perf_counter() - self.last_frame_time
    
    if actual_time < frame_time * 0.5:
        # Система быстрая - рендерим все слои
        return False
    elif actual_time > frame_time * 1.5:
        # Система медленная - пропускаем некоторые слои
        return True
    return False
```

## Продвинутые техники

### 1. Многопоточный рендеринг

```python
import concurrent.futures
from threading import Lock

class ThreadedRenderer:
    def __init__(self):
        self.surface_lock = Lock()
        self.max_workers = 2  # Не больше 2-3 для pygame
    
    def render_layers_parallel(self, layers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Параллельно генерируем цветовые изображения
            futures = []
            for i, layer in enumerate(layers):
                future = executor.submit(self.generate_color_image, layer)
                futures.append((i, future))
            
            # Последовательно применяем к pygame поверхностям
            # (pygame не thread-safe для поверхностей)
            with self.surface_lock:
                for i, future in futures:
                    color_img = future.result()
                    self.apply_to_surface(color_img, layers[i])
```

### 2. LOD (Level of Detail) рендеринг

```python
def render_with_lod(self, layer, distance_factor):
    """Рендеринг с уровнем детализации на основе важности слоя"""
    
    if distance_factor < 0.3:
        # Высокое качество - полное разрешение
        scale = 1.0
        use_antialiasing = True
    elif distance_factor < 0.7:
        # Среднее качество - 75% разрешения
        scale = 0.75
        use_antialiasing = False
    else:
        # Низкое качество - 50% разрешения
        scale = 0.5
        use_antialiasing = False
    
    # Рендерим с соответствующим качеством
    return self.render_scaled(layer, scale, use_antialiasing)
```

### 3. Пространственная оптимизация

```python
class SpatialRenderer:
    def __init__(self):
        self.dirty_regions = set()
        self.region_size = 16  # Размер региона в клетках
    
    def mark_dirty(self, x, y, width, height):
        """Отмечает регион как требующий обновления"""
        start_x = (x // self.region_size) * self.region_size
        start_y = (y // self.region_size) * self.region_size
        end_x = ((x + width) // self.region_size + 1) * self.region_size
        end_y = ((y + height) // self.region_size + 1) * self.region_size
        
        for rx in range(start_x, end_x, self.region_size):
            for ry in range(start_y, end_y, self.region_size):
                self.dirty_regions.add((rx, ry))
    
    def render_dirty_regions_only(self, layers):
        """Рендерит только измененные регионы"""
        for region_x, region_y in self.dirty_regions:
            region_rect = pygame.Rect(
                region_x * CELL_SIZE, 
                region_y * CELL_SIZE,
                self.region_size * CELL_SIZE, 
                self.region_size * CELL_SIZE
            )
            
            # Рендерим регион для всех слоев
            for layer in layers:
                self.render_layer_region(layer, region_rect)
        
        self.dirty_regions.clear()
```

## Профилирование и отладка

### 1. Мониторинг производительности

```python
class RenderProfiler:
    def __init__(self):
        self.timings = {}
        self.counters = {}
    
    def profile_section(self, name):
        """Context manager для профилирования секций кода"""
        return self.ProfileSection(self, name)
    
    class ProfileSection:
        def __init__(self, profiler, name):
            self.profiler = profiler
            self.name = name
            
        def __enter__(self):
            self.start = time.perf_counter()
            
        def __exit__(self, *args):
            elapsed = time.perf_counter() - self.start
            if self.name not in self.profiler.timings:
                self.profiler.timings[self.name] = []
            self.profiler.timings[self.name].append(elapsed)

# Использование:
profiler = RenderProfiler()

with profiler.profile_section("layer_generation"):
    color_img = generate_color_image(layer)

with profiler.profile_section("surface_creation"):
    surface = create_surface(color_img)
```

### 2. Визуализация производительности

```python
def draw_performance_overlay(self, screen):
    """Отображает оверлей с информацией о производительности"""
    stats = self.get_performance_stats()
    
    # Создаем полупрозрачную панель
    overlay = pygame.Surface((300, 150))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    
    # Добавляем текст статистики
    y_offset = 10
    for name, value in stats.items():
        text = f"{name}: {value}"
        rendered = self.font.render(text, True, (255, 255, 255))
        overlay.blit(rendered, (10, y_offset))
        y_offset += 20
    
    screen.blit(overlay, (screen.get_width() - 310, 10))
```

## Решение проблем производительности

### Диагностика узких мест:

1. **Низкий FPS при малом количестве клеток**
   - Проблема: Неэффективное смешивание слоев
   - Решение: Группировка по режимам смешивания

2. **Высокое потребление памяти**
   - Проблема: Создание новых поверхностей на каждом кадре
   - Решение: Кэширование и переиспользование буферов

3. **Лаги при изменении палитр**
   - Проблема: Пересчет палитр в реальном времени
   - Решение: Предвычисление и кэширование палитр

4. **Медленная отрисовка больших сеток**
   - Проблема: Обработка всей сетки даже при малых изменениях
   - Решение: Региональное обновление и LOD

### Рекомендуемые настройки:

```python
# Для систем с 4+ ядрами:
THREADED_RENDERING = True
MAX_WORKER_THREADS = 2

# Для систем с ограниченной памятью:
CACHE_SIZE_LIMIT = 50  # Максимум кэшированных поверхностей
ENABLE_LOD = True

# Для слабых GPU:
USE_SOFTWARE_RENDERING = True
REDUCE_BLEND_MODES = True

# Для мощных систем:
ENABLE_ALL_EFFECTS = True
MAX_LAYERS = 5
HIGH_QUALITY_SCALING = True
```

## Заключение

Эффективный рендеринг многослойных клеточных автоматов требует:

1. **Кэширования** - Избегайте пересоздания неизменных данных
2. **Группировки** - Минимизируйте переключения состояний
3. **Адаптивности** - Подстраивайтесь под производительность системы
4. **Профилирования** - Измеряйте и оптимизируйте узкие места

При правильной реализации система может поддерживать стабильные 60 FPS даже с 5 активными слоями и множественными эффектами.

## Дополнительные ресурсы

- `optimized_renderer.py` - Готовая реализация оптимизированного рендеринга
- `LAYER_RENDERING_OPTIMIZATION.md` - Подробное техническое описание оптимизаций
- Профилировщик pygame: `pygame.time.Clock()` для измерения FPS
- Мониторинг памяти: `psutil` для отслеживания потребления памяти