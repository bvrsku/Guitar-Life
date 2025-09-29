
import tkinter as tk
from tkinter import ttk
import json

# ---- Options ----
CA_RULES = [
    "Conway", "HighLife", "Day&Night", "Replicator",
    "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
]

PALETTES = [
    # Основные
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth",
    # Тематические
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight",
    # Моно/контраст
    "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black",
    "Monochrome", "Sepia", "HighContrast", "LowContrast",
    # Специальные
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"
]

BLEND_MODES = ["normal", "additive", "screen", "multiply", "overlay"]

def _read_existing_settings():
    try:
        with open('guitar_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _layer_defaults(i):
    # Разные пресеты для разнообразия по умолчанию
    presets = [
        ("Conway", "BrightRed->DarkRed->DarkGray->Black", "Blue->Green->Yellow->Red"),
        ("HighLife", "Ocean", "Fire"),
        ("Day&Night", "Neon", "Ocean"),
        ("Replicator", "Sunset", "RainbowSmooth"),
        ("Seeds", "Ukraine", "Cyberpunk"),
    ]
    rule, age_pal, rms_pal = presets[i % len(presets)]
    return {
        'rule': rule,
        'age_palette': age_pal,
        'rms_palette': rms_pal,
        'alpha_live': 220,
        'alpha_old': 140,
        'mix': 'Normal',
        'solo': False,
        'mute': False,
        'rms_mode': 'brightness',
        'color_mode': 'HSV-дизайны',
    }

def show_modern_gui(devices):
    root = tk.Tk()
    root.title("Guitar Life v13 — Полные настройки")
    root.geometry("740x640")

    # Make sure popdown lists are on top of everything on Windows
    try:
        root.attributes("-topmost", False)
    except Exception:
        pass

    result = None
    settings = _read_existing_settings()

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # === AUDIO ===
    audio_frame = ttk.Frame(notebook)
    notebook.add(audio_frame, text="Аудио")
    af = ttk.Frame(audio_frame, padding=20)
    af.pack(fill="both", expand=True)

    device_names = [d.get('name','default') for d in (devices or [{'name':'default'}])]
    device_var = tk.StringVar(value=settings.get('device', device_names[0]))
    ttk.Label(af, text="Аудио устройство:").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Combobox(af, textvariable=device_var, values=device_names, state="readonly").grid(row=0, column=1, sticky="ew", padx=(8,0))

    gain_var = tk.DoubleVar(value=settings.get('gain', 2.5))
    ttk.Label(af, text="Усиление:").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Scale(af, from_=0.1, to=5.0, variable=gain_var).grid(row=1, column=1, sticky="ew", padx=(8,0))

    rms_strength_var = tk.IntVar(value=settings.get('rms_strength', 100))
    ttk.Label(af, text="Сила RMS (%):").grid(row=2, column=0, sticky="w", pady=6)
    ttk.Scale(af, from_=0, to=200, variable=rms_strength_var).grid(row=2, column=1, sticky="ew", padx=(8,0))

    rms_min_var = tk.DoubleVar(value=settings.get('color_rms_min', 0.004))
    ttk.Label(af, text="RMS минимум:").grid(row=3, column=0, sticky="w", pady=6)
    ttk.Scale(af, from_=0.001, to=0.1, variable=rms_min_var).grid(row=3, column=1, sticky="ew", padx=(8,0))

    rms_max_var = tk.DoubleVar(value=settings.get('color_rms_max', 0.3))
    ttk.Label(af, text="RMS максимум:").grid(row=4, column=0, sticky="w", pady=6)
    ttk.Scale(af, from_=0.1, to=1.0, variable=rms_max_var).grid(row=4, column=1, sticky="ew", padx=(8,0))

    af.columnconfigure(1, weight=1)

    # === LAYERS ===
    layers_tab = ttk.Frame(notebook)
    notebook.add(layers_tab, text="Слои")

    lt_top = ttk.Frame(layers_tab, padding=(12, 10, 12, 0))
    lt_top.pack(fill="x")
    layer_count_var = tk.IntVar(value=int(settings.get('layer_count', 3)))

    ttk.Label(lt_top, text="Количество слоёв:").pack(side="left")
    def _apply_count(val=None):
        try:
            build_layer_blocks(int(float(layer_count_var.get())))
        except Exception:
            pass

    # use Spinbox to avoid slider precision and to not overlap with dropdowns
    sb = ttk.Spinbox(lt_top, from_=1, to=8, textvariable=layer_count_var, width=5, command=_apply_count)
    sb.pack(side="left", padx=(8, 16))

    # Scrollable area for layer blocks
    canvas = tk.Canvas(layers_tab, highlightthickness=0)
    vs = ttk.Scrollbar(layers_tab, orient="vertical", command=canvas.yview)
    scroll = ttk.Frame(canvas)
    scroll_id = canvas.create_window((0, 0), window=scroll, anchor="nw")
    canvas.configure(yscrollcommand=vs.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(12,0), pady=(6,12))
    vs.pack(side="right", fill="y", pady=(6,12))

    def _on_frame_config(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll.bind("<Configure>", _on_frame_config)

    def _on_canvas_config(event):
        canvas.itemconfig(scroll_id, width=event.width)
    canvas.bind("<Configure>", _on_canvas_config)

    layer_vars = []  # list of dicts per layer

    def build_layer_blocks(n):
        # clear old
        nonlocal layer_vars
        for child in list(scroll.winfo_children()):
            child.destroy()
        layer_vars = []

        # existing cfg or defaults
        existing_cfg = settings.get('layers_cfg') or []
        for i in range(n):
            cfg = existing_cfg[i] if i < len(existing_cfg) else _layer_defaults(i)

            lf = ttk.LabelFrame(scroll, text=f"Layer {i+1}", padding=12)
            lf.pack(fill="x", expand=True, pady=6)

            row = 0
            # Rule
            ttk.Label(lf, text="Rule:").grid(row=row, column=0, sticky="w", pady=4)
            rule_var = tk.StringVar(value=cfg.get('rule', 'Conway'))
            ttk.Combobox(lf, values=CA_RULES, textvariable=rule_var, state="readonly").grid(row=row, column=1, sticky="ew", padx=(8,0), pady=4); row += 1

            # Age palette
            ttk.Label(lf, text="Age palette:").grid(row=row, column=0, sticky="w", pady=4)
            age_var = tk.StringVar(value=cfg.get('age_palette', 'Blue->Green->Yellow->Red'))
            ttk.Combobox(lf, values=PALETTES, textvariable=age_var, state="readonly").grid(row=row, column=1, sticky="ew", padx=(8,0), pady=4); row += 1

            # RMS palette
            ttk.Label(lf, text="RMS palette:").grid(row=row, column=0, sticky="w", pady=4)
            rms_var = tk.StringVar(value=cfg.get('rms_palette', 'Blue->Green->Yellow->Red'))
            ttk.Combobox(lf, values=PALETTES, textvariable=rms_var, state="readonly").grid(row=row, column=1, sticky="ew", padx=(8,0), pady=4); row += 1

            # Alpha / Transparency
            ttk.Label(lf, text="Alpha / Прозрачность (0–255):").grid(row=row, column=0, sticky="w", pady=4)
            alpha_var = tk.IntVar(value=int(cfg.get('alpha_live', 220)))
            # scale with live label
            s = ttk.Scale(lf, from_=0, to=255, variable=alpha_var)
            s.grid(row=row, column=1, sticky="ew", padx=(8,0), pady=4); row += 1

            # Blend mode
            ttk.Label(lf, text="Blend Mode:").grid(row=row, column=0, sticky="w", pady=4)
            mix_init = str(cfg.get('mix', 'Normal')).lower()
            mix_var = tk.StringVar(value=mix_init if mix_init in BLEND_MODES else "normal")
            ttk.Combobox(lf, values=BLEND_MODES, textvariable=mix_var, state="readonly").grid(row=row, column=1, sticky="ew", padx=(8,0), pady=4); row += 1

            lf.columnconfigure(1, weight=1)

            layer_vars.append({
                'rule': rule_var,
                'age_palette': age_var,
                'rms_palette': rms_var,
                'alpha': alpha_var,
                'mix': mix_var
            })

    build_layer_blocks(int(layer_count_var.get()))

    # === TIMING ===
    timing_tab = ttk.Frame(notebook)
    notebook.add(timing_tab, text="Тайминги")
    tf = ttk.Frame(timing_tab, padding=20); tf.pack(fill="both", expand=True)

    tick_ms_var = tk.IntVar(value=settings.get('tick_ms', 120))
    ttk.Label(tf, text="Интервал тика (мс):").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Scale(tf, from_=10, to=500, variable=tick_ms_var).grid(row=0, column=1, sticky="ew", padx=(8,0), pady=6)

    pitch_tick_var = tk.BooleanVar(value=settings.get('pitch_tick_enable', False))
    ttk.Checkbutton(tf, text="Адаптивный тик по высоте ноты", variable=pitch_tick_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=6)
    tf.columnconfigure(1, weight=1)

    # === EFFECTS ===
    fx_tab = ttk.Frame(notebook)
    notebook.add(fx_tab, text="Эффекты")
    fx = ttk.Frame(fx_tab, padding=20); fx.pack(fill="both", expand=True)

    trails_var = tk.BooleanVar(value=settings.get('trails', True))
    ttk.Checkbutton(fx, text="Следы (Trails)", variable=trails_var).grid(row=0, column=0, sticky="w", pady=6)
    trail_strength_var = tk.DoubleVar(value=settings.get('trail_strength', 0.06))
    ttk.Label(fx, text="Сила следов:").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Scale(fx, from_=0.01, to=0.2, variable=trail_strength_var).grid(row=1, column=1, sticky="ew", padx=(8,0), pady=6)

    blur_var = tk.BooleanVar(value=settings.get('blur', False))
    ttk.Checkbutton(fx, text="Размытие", variable=blur_var).grid(row=2, column=0, sticky="w", pady=6)
    bloom_var = tk.BooleanVar(value=settings.get('bloom', False))
    ttk.Checkbutton(fx, text="Свечение", variable=bloom_var).grid(row=3, column=0, sticky="w", pady=6)
    posterize_var = tk.BooleanVar(value=settings.get('posterize', False))
    ttk.Checkbutton(fx, text="Постеризация", variable=posterize_var).grid(row=4, column=0, sticky="w", pady=6)
    scanlines_var = tk.BooleanVar(value=settings.get('scanlines', False))
    ttk.Checkbutton(fx, text="Сканлайны", variable=scanlines_var).grid(row=5, column=0, sticky="w", pady=6)
    fx.columnconfigure(1, weight=1)

    # === CLEAR ===
    clear_tab = ttk.Frame(notebook)
    notebook.add(clear_tab, text="Очистка")
    cl = ttk.Frame(clear_tab, padding=20); cl.pack(fill="both", expand=True)
    soft_clear_var = tk.BooleanVar(value=settings.get('soft_clear_enable', True))
    ttk.Checkbutton(cl, text="Включить мягкую очистку", variable=soft_clear_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=6)
    max_cells_var = tk.IntVar(value=settings.get('max_cells_percent', 50))
    ttk.Label(cl, text="Макс. заполнение (%):").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Scale(cl, from_=10, to=90, variable=max_cells_var).grid(row=1, column=1, sticky="ew", padx=(8,0), pady=6)
    clear_rms_var = tk.DoubleVar(value=settings.get('clear_rms', 0.004))
    ttk.Label(cl, text="Порог очистки RMS:").grid(row=2, column=0, sticky="w", pady=6)
    ttk.Scale(cl, from_=0.001, to=0.02, variable=clear_rms_var).grid(row=2, column=1, sticky="ew", padx=(8,0), pady=6)
    cl.columnconfigure(1, weight=1)

    # === BUTTONS ===
    btns = ttk.Frame(root); btns.pack(fill="x", padx=10, pady=(0,10))
    def on_ok():
        nonlocal result
        # Map chosen device back to index, default to 0
        device_name = device_var.get()
        device_index = 0
        for idx, d in enumerate(devices or []):
            if d.get('name') == device_name:
                device_index = idx
                break

        # collect layers
        n = int(float(layer_count_var.get()))
        layers_cfg = []
        for i in range(n):
            lv = layer_vars[i]
            alpha = int(lv['alpha'].get())
            layers_cfg.append({
                'rule': lv['rule'].get(),
                'age_palette': lv['age_palette'].get(),
                'rms_palette': lv['rms_palette'].get(),
                'color_mode': 'HSV-дизайны',
                'rms_mode': 'palette' if lv['rms_palette'].get() else 'brightness',
                'alpha_live': alpha,
                'alpha_old': alpha,
                'mix': lv['mix'].get().capitalize(),  # "normal" -> "Normal"
                'solo': False,
                'mute': False,
            })

        result = {
            # Audio
            'device': device_name,
            'device_index': device_index,
            'gain': float(gain_var.get()),
            'rms_strength': int(rms_strength_var.get()),
            'color_rms_min': float(rms_min_var.get()),
            'color_rms_max': float(rms_max_var.get()),

            # Layers
            'layer_count': n,
            'layers_different': True,  # теперь всегда независимые параметры
            'layers_cfg': layers_cfg,

            # Timing
            'tick_ms': int(tick_ms_var.get()),
            'pitch_tick_enable': bool(pitch_tick_var.get()),
            'pitch_tick_min_ms': 60,
            'pitch_tick_max_ms': 200,

            # FX
            'trails': bool(trails_var.get()),
            'trail_strength': float(trail_strength_var.get()),
            'blur': bool(blur_var.get()),
            'bloom': bool(bloom_var.get()),
            'posterize': bool(posterize_var.get()),
            'scanlines': bool(scanlines_var.get()),

            # Clear
            'soft_clear_enable': bool(soft_clear_var.get()),
            'max_cells_percent': int(max_cells_var.get()),
            'clear_rms': float(clear_rms_var.get()),

            # Старый формат для совместимости
            'fx': {
                'trails': bool(trails_var.get()),
                'blur': bool(blur_var.get()),
                'bloom': bool(bloom_var.get()),
                'posterize': bool(posterize_var.get()),
                'dither': False,
                'scanlines': bool(scanlines_var.get()),
                'pixelate': False,
                'outline': False,
            }
        }

        try:
            with open('guitar_config.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Ошибка сохранения настроек:", e)
        root.quit()

    def on_cancel():
        nonlocal result
        result = None
        root.quit()

    ttk.Button(btns, text="Отмена", command=on_cancel).pack(side="right", padx=(6,0))
    ttk.Button(btns, text="OK", command=on_ok).pack(side="right")

    root.mainloop()
    root.destroy()
    return result

if __name__ == "__main__":
    # Demo without devices list
    print(show_modern_gui([{'name': 'default'}]))
