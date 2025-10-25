import tkinter as tk
from tkinter import ttk
import json

def show_modern_gui(devices):
    root = tk.Tk()
    root.title("Settings")
    root.geometry("600x500")
    
    result = None
    
    # Notebook для вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # === АУДИО ===
    audio_frame = ttk.Frame(notebook)
    notebook.add(audio_frame, text="Аудио")
    
    audio_frame_content = ttk.Frame(audio_frame, padding="20")
    audio_frame_content.pack(fill="both", expand=True)
    
    # Устройство
    ttk.Label(audio_frame_content, text="Аудио устройство:").grid(row=0, column=0, sticky="w", pady=5)
    device_names = [d['name'] for d in devices] if devices else ['default']
    device_var = tk.StringVar(value=device_names[0])
    ttk.Combobox(audio_frame_content, textvariable=device_var, values=device_names, state="readonly").grid(row=0, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Усиление
    ttk.Label(audio_frame_content, text="Усиление:").grid(row=1, column=0, sticky="w", pady=5)
    gain_var = tk.DoubleVar(value=2.5)
    ttk.Scale(audio_frame_content, from_=0.1, to=5.0, variable=gain_var).grid(row=1, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # RMS сила
    ttk.Label(audio_frame_content, text="Сила RMS (%):").grid(row=2, column=0, sticky="w", pady=5)
    rms_strength_var = tk.IntVar(value=100)
    ttk.Scale(audio_frame_content, from_=0, to=200, variable=rms_strength_var).grid(row=2, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # RMS пороги
    ttk.Label(audio_frame_content, text="RMS минимум:").grid(row=3, column=0, sticky="w", pady=5)
    rms_min_var = tk.DoubleVar(value=0.004)
    ttk.Scale(audio_frame_content, from_=0.001, to=0.1, variable=rms_min_var).grid(row=3, column=1, sticky="ew", padx=(10,0), pady=5)
    
    ttk.Label(audio_frame_content, text="RMS максимум:").grid(row=4, column=0, sticky="w", pady=5)
    rms_max_var = tk.DoubleVar(value=0.3)
    ttk.Scale(audio_frame_content, from_=0.1, to=1.0, variable=rms_max_var).grid(row=4, column=1, sticky="ew", padx=(10,0), pady=5)
    
    audio_frame_content.columnconfigure(1, weight=1)
    
    # === СЛОИ ===
    layers_frame = ttk.Frame(notebook)
    notebook.add(layers_frame, text="Слои")
    
    layers_frame_content = ttk.Frame(layers_frame, padding="20")
    layers_frame_content.pack(fill="both", expand=True)
    
    # Количество слоев
    ttk.Label(layers_frame_content, text="Количество слоев:").grid(row=0, column=0, sticky="w", pady=5)
    layer_count_var = tk.IntVar(value=3)
    ttk.Scale(layers_frame_content, from_=1, to=5, variable=layer_count_var).grid(row=0, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Разные настройки для слоев
    layers_different_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(layers_frame_content, text="Разные настройки для слоев", variable=layers_different_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
    
    layers_frame_content.columnconfigure(1, weight=1)
    
    # === ТАЙМИНГИ ===
    timing_frame = ttk.Frame(notebook)
    notebook.add(timing_frame, text="Тайминги")
    
    timing_frame_content = ttk.Frame(timing_frame, padding="20")
    timing_frame_content.pack(fill="both", expand=True)
    
    # Интервал тика
    ttk.Label(timing_frame_content, text="Интервал тика (мс):").grid(row=0, column=0, sticky="w", pady=5)
    tick_ms_var = tk.IntVar(value=120)
    ttk.Scale(timing_frame_content, from_=10, to=500, variable=tick_ms_var).grid(row=0, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Адаптивный тик
    pitch_tick_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(timing_frame_content, text="Адаптивный тик по высоте ноты", variable=pitch_tick_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
    
    timing_frame_content.columnconfigure(1, weight=1)
    
    # === ЦВЕТА ===
    color_frame = ttk.Frame(notebook)
    notebook.add(color_frame, text="Цвета")
    
    color_frame_content = ttk.Frame(color_frame, padding="20")
    color_frame_content.pack(fill="both", expand=True)
    
    # Максимальный возраст
    ttk.Label(color_frame_content, text="Максимальный возраст:").grid(row=0, column=0, sticky="w", pady=5)
    max_age_var = tk.IntVar(value=120)
    ttk.Scale(color_frame_content, from_=20, to=300, variable=max_age_var).grid(row=0, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Скорость старения
    ttk.Label(color_frame_content, text="Скорость старения:").grid(row=1, column=0, sticky="w", pady=5)
    aging_speed_var = tk.DoubleVar(value=1.0)
    ttk.Scale(color_frame_content, from_=0.1, to=5.0, variable=aging_speed_var).grid(row=1, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Начало затухания
    ttk.Label(color_frame_content, text="Начало затухания:").grid(row=2, column=0, sticky="w", pady=5)
    fade_start_var = tk.IntVar(value=60)
    ttk.Scale(color_frame_content, from_=10, to=200, variable=fade_start_var).grid(row=2, column=1, sticky="ew", padx=(10,0), pady=5)
    
    color_frame_content.columnconfigure(1, weight=1)
    
    # === ЭФФЕКТЫ ===
    fx_frame = ttk.Frame(notebook)
    notebook.add(fx_frame, text="Эффекты")
    
    fx_frame_content = ttk.Frame(fx_frame, padding="20")
    fx_frame_content.pack(fill="both", expand=True)
    
    # Основные эффекты
    trails_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(fx_frame_content, text="Следы (Trails)", variable=trails_var).grid(row=0, column=0, sticky="w", pady=5)
    
    # Сила следов
    ttk.Label(fx_frame_content, text="Сила следов:").grid(row=1, column=0, sticky="w", pady=5)
    trail_strength_var = tk.DoubleVar(value=0.06)
    ttk.Scale(fx_frame_content, from_=0.01, to=0.2, variable=trail_strength_var).grid(row=1, column=1, sticky="ew", padx=(10,0), pady=5)
    
    blur_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(fx_frame_content, text="Размытие", variable=blur_var).grid(row=2, column=0, sticky="w", pady=5)
    
    bloom_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(fx_frame_content, text="Свечение", variable=bloom_var).grid(row=3, column=0, sticky="w", pady=5)
    
    posterize_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(fx_frame_content, text="Постеризация", variable=posterize_var).grid(row=4, column=0, sticky="w", pady=5)
    
    scanlines_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(fx_frame_content, text="Сканлайны", variable=scanlines_var).grid(row=5, column=0, sticky="w", pady=5)
    
    fx_frame_content.columnconfigure(1, weight=1)
    
    # === ОЧИСТКА ===
    clear_frame = ttk.Frame(notebook)
    notebook.add(clear_frame, text="Очистка")
    
    clear_frame_content = ttk.Frame(clear_frame, padding="20")
    clear_frame_content.pack(fill="both", expand=True)
    
    # Мягкая очистка
    soft_clear_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(clear_frame_content, text="Включить мягкую очистку", variable=soft_clear_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
    
    # Максимальное заполнение
    ttk.Label(clear_frame_content, text="Макс. заполнение (%):").grid(row=1, column=0, sticky="w", pady=5)
    max_cells_var = tk.IntVar(value=50)
    ttk.Scale(clear_frame_content, from_=10, to=90, variable=max_cells_var).grid(row=1, column=1, sticky="ew", padx=(10,0), pady=5)
    
    # Порог очистки RMS
    ttk.Label(clear_frame_content, text="Порог очистки RMS:").grid(row=2, column=0, sticky="w", pady=5)
    clear_rms_var = tk.DoubleVar(value=0.004)
    ttk.Scale(clear_frame_content, from_=0.001, to=0.02, variable=clear_rms_var).grid(row=2, column=1, sticky="ew", padx=(10,0), pady=5)
    
    clear_frame_content.columnconfigure(1, weight=1)
    
    # === КНОПКИ ===
    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    def on_ok():
        nonlocal result
        
        device_name = device_var.get()
        device_index = 0
        for i, device in enumerate(devices):
            if device['name'] == device_name:
                device_index = i
                break
        
        result = {
            # Аудио
            'device': device_name,
            'device_index': device_index,
            'gain': gain_var.get(),
            'rms_strength': rms_strength_var.get(),
            'color_rms_min': rms_min_var.get(),
            'color_rms_max': rms_max_var.get(),
            
            # Слои
            'layer_count': layer_count_var.get(),
            'layers_different': layers_different_var.get(),
            
            # Тайминги
            'tick_ms': tick_ms_var.get(),
            'pitch_tick_enable': pitch_tick_var.get(),
            'pitch_tick_min_ms': 60,
            'pitch_tick_max_ms': 200,
            
            # Цвета
            'max_age': max_age_var.get(),
            'aging_speed': aging_speed_var.get(),
            'fade_start': fade_start_var.get(),
            'fade_sat_drop': 70,
            'fade_val_drop': 60,
            
            # Эффекты
            'trails': trails_var.get(),
            'trail_strength': trail_strength_var.get(),
            'blur': blur_var.get(),
            'bloom': bloom_var.get(),
            'posterize': posterize_var.get(),
            'scanlines': scanlines_var.get(),
            
            # Очистка
            'soft_clear_enable': soft_clear_var.get(),
            'max_cells_percent': max_cells_var.get(),
            'clear_rms': clear_rms_var.get(),
            
            # Дополнительные параметры по умолчанию
            'soft_mode': 'Удалять клетки',
            'soft_kill_rate': 80,
            'soft_fade_floor': 0.3,
            'soft_fade_down': 1,
            'soft_fade_up': 5,
            'soft_clear_threshold': 70,
            'age_bias': 80,
            'mirror_x': False,
            'mirror_y': False,
            'auto_rule_sec': 0,
            'auto_palette_sec': 0,
            'blur_scale': 2,
            'bloom_strength': 0.35,
            'poster_levels': 5,
            'dither': False,
            'scan_strength': 0.25,
            'pixelate': False,
            'pixel_block': 1,
            'outline': False,
            'outline_thick': 1,
            
            # Конфигурации слоев
            'layers_cfg': [
                {
                    'rule': 'Conway',
                    'age_palette': 'BrightRed->DarkRed->DarkGray->Black',
                    'rms_palette': 'Blue->Green->Yellow->Red',
                    'color_mode': 'HSV-дизайны',
                    'rms_mode': 'brightness',
                    'alpha_live': 220,
                    'alpha_old': 140,
                    'mix': 'Normal',
                    'solo': False,
                    'mute': False,
                },
                {
                    'rule': 'HighLife',
                    'age_palette': 'Ocean',
                    'rms_palette': 'Fire',
                    'color_mode': 'HSV-дизайны',
                    'rms_mode': 'brightness',
                    'alpha_live': 220,
                    'alpha_old': 140,
                    'mix': 'Normal',
                    'solo': False,
                    'mute': False,
                },
                {
                    'rule': 'Day&Night',
                    'age_palette': 'Neon',
                    'rms_palette': 'Ocean',
                    'color_mode': 'HSV-дизайны',
                    'rms_mode': 'brightness',
                    'alpha_live': 220,
                    'alpha_old': 140,
                    'mix': 'Normal',
                    'solo': False,
                    'mute': False,
                }
            ],
            
            # Старый формат fx для совместимости
            'fx': {
                'trails': trails_var.get(),
                'blur': blur_var.get(),
                'bloom': bloom_var.get(),
                'posterize': posterize_var.get(),
                'dither': False,
                'scanlines': scanlines_var.get(),
                'pixelate': False,
                'outline': False,
            }
        }
        
        # Сохраняем настройки
        try:
            with open('guitar_config.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
        
        root.quit()
    
    def on_cancel():
        nonlocal result
        result = None
        root.quit()
    
    # Кнопки
    ttk.Button(button_frame, text="Отмена", command=on_cancel).pack(side="right", padx=(5, 0))
    ttk.Button(button_frame, text="OK", command=on_ok).pack(side="right")
    
    # Загружаем существующие настройки если есть
    try:
        import os
        if os.path.exists('guitar_config.json'):
            with open('guitar_config.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Применяем настройки к GUI
            if 'device' in settings:
                device_var.set(settings['device'])
            if 'gain' in settings:
                gain_var.set(settings['gain'])
            if 'rms_strength' in settings:
                rms_strength_var.set(settings['rms_strength'])
            if 'layer_count' in settings:
                layer_count_var.set(settings['layer_count'])
            if 'tick_ms' in settings:
                tick_ms_var.set(settings['tick_ms'])
            if 'max_age' in settings:
                max_age_var.set(settings['max_age'])
            if 'aging_speed' in settings:
                aging_speed_var.set(settings['aging_speed'])
            if 'trails' in settings:
                trails_var.set(settings['trails'])
            if 'trail_strength' in settings:
                trail_strength_var.set(settings['trail_strength'])
            if 'blur' in settings:
                blur_var.set(settings['blur'])
            if 'bloom' in settings:
                bloom_var.set(settings['bloom'])
    except:
        pass
    
    root.mainloop()
    root.destroy()
    
    return result