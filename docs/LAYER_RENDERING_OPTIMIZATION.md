# Guitar Life - Оптимизация рендеринга слоев

## Текущие проблемы производительности

В настоящее время система рендеринга слоев Guitar Life имеет несколько узких мест:

### 1. **Множественное масштабирование поверхностей**
```python
# Проблема: каждый слой масштабируется отдельно
rgb_surf = pygame.transform.scale(rgb_surf, scaled_size)
```

### 2. **Создание новых поверхностей на каждом кадре**
```python
# Проблема: постоянное выделение памяти
rgb_surf = pygame.surfarray.make_surface(np.transpose(color_img, (1, 0, 2)))
```

### 3. **Последовательная обработка слоев**
```python
# Проблема: слои обрабатываются по одному
for i, L in enumerate(layers):
    img = build_color_image(L.grid, L.age, L.color_mode, ...)
    self.renderer.blit_layer(img, L.mix, L.alpha_live, L.alpha_old)
```

## Рекомендуемые оптимизации

### 1. **Кэширование поверхностей слоев**

```python
class OptimizedRenderManager:
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells  
        self.cs = cell_size
        self.canvas = pygame.Surface((w_cells * cell_size, h_cells * cell_size)).convert()
        
        # Кэш поверхностей для каждого слоя
        self.layer_surfaces = {}
        self.layer_cache_dirty = {}
        
    def get_layer_surface(self, layer_id: int, size: tuple) -> pygame.Surface:
        """Получает кэшированную поверхность или создает новую"""
        if layer_id not in self.layer_surfaces:
            self.layer_surfaces[layer_id] = pygame.Surface(size).convert()
            self.layer_cache_dirty[layer_id] = True
        return self.layer_surfaces[layer_id]
```

### 2. **Batch-обработка изменений слоев**

```python
def render_layers_batch(self, layers: List[Layer], rms: float, pitch: float, cfg: dict):
    """Батчевая обработка всех слоев"""
    
    # 1. Выявляем какие слои изменились
    changed_layers = []
    for i, layer in enumerate(layers):
        layer_hash = hash((layer.grid.tobytes(), layer.age.max(), layer.color_mode))
        if getattr(layer, '_last_hash', None) != layer_hash:
            changed_layers.append((i, layer))
            layer._last_hash = layer_hash
    
    # 2. Параллельно обрабатываем только измененные слои
    if changed_layers:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for layer_idx, layer in changed_layers:
                future = executor.submit(
                    self.render_single_layer,
                    layer_idx, layer, rms, pitch, cfg
                )
                futures.append((layer_idx, future))
            
            # Собираем результаты
            for layer_idx, future in futures:
                self.layer_surfaces[layer_idx] = future.result()
```

### 3. **Оптимизированное смешивание**

```python
def optimized_blend_layers(self, layers: List[Layer]) -> pygame.Surface:
    """Эффективное смешивание слоев с предварительным альфа-композитингом"""
    
    # Группируем слои по режимам смешивания
    normal_layers = []
    additive_layers = []
    
    for layer in layers:
        if layer.mix == "Additive":
            additive_layers.append(layer)
        else:
            normal_layers.append(layer)
    
    # Сначала смешиваем Normal слои (более быстрая операция)
    base_surface = self.canvas.copy()
    for layer in normal_layers:
        if layer_id in self.layer_surfaces:
            surface = self.layer_surfaces[layer_id]
            surface.set_alpha(layer.alpha_live)
            base_surface.blit(surface, (0, 0))
    
    # Затем добавляем Additive слои (более медленная операция)
    for layer in additive_layers:
        if layer_id in self.layer_surfaces:
            surface = self.layer_surfaces[layer_id]
            surface.set_alpha(layer.alpha_live)
            surface.set_blend_mode(pygame.BLEND_RGB_ADD)
            base_surface.blit(surface, (0, 0))
    
    return base_surface
```

### 4. **Умное обновление только активных областей**

```python
class RegionBasedRenderer:
    def __init__(self, w_cells: int, h_cells: int, cell_size: int):
        self.wc = w_cells
        self.hc = h_cells
        self.cs = cell_size
        self.dirty_regions = set()  # Области требующие перерисовки
        
    def mark_dirty_region(self, x: int, y: int, w: int, h: int):
        """Отмечает область как требующую обновления"""
        # Группируем соседние области для оптимизации
        region = (x // 16 * 16, y // 16 * 16, 
                 min(16, w), min(16, h))  # 16x16 блоки
        self.dirty_regions.add(region)
    
    def update_dirty_regions_only(self, layers: List[Layer]):
        """Обновляет только области где произошли изменения"""
        for region in self.dirty_regions:
            x, y, w, h = region
            region_rect = pygame.Rect(x * self.cs, y * self.cs, 
                                    w * self.cs, h * self.cs)
            
            # Рендерим только эту область для всех слоев
            for layer in layers:
                layer_region = self.extract_layer_region(layer, x, y, w, h)
                if layer_region is not None:
                    self.blit_region(layer_region, region_rect, layer.mix)
        
        self.dirty_regions.clear()
```

### 5. **Предварительная обработка цветовых палитр**

```python
class PaletteCache:
    def __init__(self):
        self.cached_palettes = {}
        
    def get_palette_colors(self, palette_name: str, steps: int = 256) -> np.ndarray:
        """Возвращает предвычисленную палитру цветов"""
        cache_key = (palette_name, steps)
        
        if cache_key not in self.cached_palettes:
            colors = self.compute_palette(palette_name, steps)
            self.cached_palettes[cache_key] = colors
            
        return self.cached_palettes[cache_key]
    
    def compute_palette(self, palette_name: str, steps: int) -> np.ndarray:
        """Предвычисляет всю палитру заранее"""
        palette_colors = np.zeros((steps, 3), dtype=np.uint8)
        
        for i in range(steps):
            # Вычисляем цвет для каждого шага палитры
            age_factor = i / max(1, steps - 1)
            color = self.interpolate_palette_color(palette_name, age_factor)
            palette_colors[i] = color
            
        return palette_colors
```

## Практические советы по оптимизации

### 1. **Используйте профилировщик**
```python
import cProfile
import pstats

def profile_rendering():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Ваш код рендеринга здесь
    app.render(rms, pitch)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Топ 10 функций по времени
```

### 2. **Оптимизация настроек pygame**
```python
# В начале инициализации
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

# Используйте аппаратное ускорение если доступно
screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
```

### 3. **Минимизация копирования данных**
```python
def build_color_image_optimized(grid: np.ndarray, age: np.ndarray, 
                               palette_cache: PaletteCache) -> np.ndarray:
    """Оптимизированная версия без лишних копирований"""
    h, w = grid.shape
    
    # Используем view вместо copy где возможно
    age_normalized = np.clip(age / max_age, 0, 1)
    
    # Прямое индексирование в предвычисленную палитру
    palette_indices = (age_normalized * 255).astype(np.uint8)
    palette_colors = palette_cache.get_palette_colors("current_palette")
    
    # Векторизованное присвоение цветов
    color_img = palette_colors[palette_indices]
    
    # Обнуляем мертвые клетки без копирования
    color_img[~grid] = [0, 0, 0]
    
    return color_img
```

### 4. **Мониторинг производительности**
```python
class PerformanceMonitor:
    def __init__(self):
        self.frame_times = []
        self.render_times = []
        
    def start_frame(self):
        self.frame_start = time.perf_counter()
        
    def end_frame(self):
        frame_time = time.perf_counter() - self.frame_start
        self.frame_times.append(frame_time)
        
        # Ведем скользящее среднее
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            
    def get_fps(self) -> float:
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
    def print_stats(self):
        fps = self.get_fps()
        print(f"🎯 FPS: {fps:.1f} | Frame time: {self.frame_times[-1]*1000:.1f}ms")
```

## Приоритет оптимизаций

1. **Высокий приоритет**: Кэширование поверхностей слоев
2. **Средний приоритет**: Batch-обработка изменений
3. **Низкий приоритет**: Региональное обновление (только для очень больших сеток)

Эти оптимизации могут повысить производительность рендеринга в 2-3 раза, особенно при работе с множественными слоями.