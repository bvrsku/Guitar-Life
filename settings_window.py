import tkinter as tk
from tkinter import ttk
import threading
import queue
import json
import os


class SettingsWindow:
    def __init__(self, app_instance):
        self.app = app_instance
        self.window = None
        self.is_running = False
        
        self.settings_queue = queue.Queue()
        
        self.vars = {}
        
    def start(self):
        """Запускает окно настроек в отдельном потоке"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._run_window, daemon=True)
            thread.start()
    
    def _run_window(self):
        """Создает и запускает GUI окно"""
        try:
            self.window = tk.Tk()
            self.window.title("Guitar Life - Settings")
            self.window.geometry("400x600")
            
            # интерфейс
            self._create_interface()
            
            # Обновляем значения из приложения
            self._update_from_app()
            
            # цикл обновления
            self.window.after(100, self._update_loop)
            
            self.window.mainloop()
            
        finally:
            self.is_running = False
           
    
    def _create_interface(self):
        """элементы интерфейса"""
        # Основные параметры
        main_frame = ttk.LabelFrame(self.window, text="Основные параметры")
        main_frame.pack(fill="x", padx=10, pady=5)
        
        # Tick interval
        tk.Label(main_frame, text="Tick Interval (ms):").grid(row=0, column=0, sticky="w")
        self.vars['tick_ms'] = tk.StringVar()
        tick_entry = tk.Entry(main_frame, textvariable=self.vars['tick_ms'], width=10)
        tick_entry.grid(row=0, column=1, sticky="w")
        tick_entry.bind('<Return>', lambda e: self._send_change('tick_ms', self.vars['tick_ms'].get()))
        
        # RMS Strength
        tk.Label(main_frame, text="RMS Strength:").grid(row=1, column=0, sticky="w")
        self.vars['rms_strength'] = tk.StringVar()
        rms_entry = tk.Entry(main_frame, textvariable=self.vars['rms_strength'], width=10)
        rms_entry.grid(row=1, column=1, sticky="w")
        rms_entry.bind('<Return>', lambda e: self._send_change('rms_strength', self.vars['rms_strength'].get()))
        
        # Max Age
        tk.Label(main_frame, text="Max Age:").grid(row=2, column=0, sticky="w")
        self.vars['max_age'] = tk.StringVar()
        age_entry = tk.Entry(main_frame, textvariable=self.vars['max_age'], width=10)
        age_entry.grid(row=2, column=1, sticky="w")
        age_entry.bind('<Return>', lambda e: self._send_change('max_age', self.vars['max_age'].get()))
        
        # Aging Speed
        tk.Label(main_frame, text="Aging Speed:").grid(row=3, column=0, sticky="w")
        self.vars['aging_speed'] = tk.StringVar()
        aging_entry = tk.Entry(main_frame, textvariable=self.vars['aging_speed'], width=10)
        aging_entry.grid(row=3, column=1, sticky="w")
        aging_entry.bind('<Return>', lambda e: self._send_change('aging_speed', self.vars['aging_speed'].get()))
        
        # FX эффекты
        fx_frame = ttk.LabelFrame(self.window, text="Эффекты")
        fx_frame.pack(fill="x", padx=10, pady=5)
        
        fx_effects = ['trails', 'blur', 'bloom', 'posterize', 'dither', 'scanlines', 'pixelate', 'outline']
        self.fx_vars = {}
        
        for i, fx in enumerate(fx_effects):
            self.fx_vars[fx] = tk.BooleanVar()
            cb = tk.Checkbutton(fx_frame, text=fx.capitalize(), variable=self.fx_vars[fx],
                               command=lambda fx=fx: self._send_change(f'fx_{fx}', self.fx_vars[fx].get()))
            cb.grid(row=i//2, column=i%2, sticky="w")
        
        # Слои
        layers_frame = ttk.LabelFrame(self.window, text="Слои")
        layers_frame.pack(fill="x", padx=10, pady=5)
        
        # Количество слоев
        tk.Label(layers_frame, text="Количество слоев:").grid(row=0, column=0, sticky="w")
        self.vars['layer_count'] = tk.StringVar()
        layer_count_cb = ttk.Combobox(layers_frame, textvariable=self.vars['layer_count'], 
                                     values=['1', '2', '3', '4', '5'], width=5)
        layer_count_cb.grid(row=0, column=1, sticky="w")
        layer_count_cb.bind('<<ComboboxSelected>>', lambda e: self._send_change('layer_count', self.vars['layer_count'].get()))
        
        # Действия
        actions_frame = ttk.LabelFrame(self.window, text="Действия")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Random Pattern", 
                  command=lambda: self._send_change('random_pattern', True)).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Clear", 
                  command=lambda: self._send_change('clear', True)).pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Test Pattern", 
                  command=lambda: self._send_change('test', True)).pack(side="left", padx=5)
        
        # Статус
        status_frame = ttk.LabelFrame(self.window, text="Статус")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.status_text = tk.Text(status_frame, height=8, width=40)
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _send_change(self, param_name, value):
        """Отправляет изменение в основное приложение"""
        try:
            self.settings_queue.put((param_name, value))
            self._log(f"Изменено: {param_name} = {value}")
        except Exception as e:
            self._log(f"Ошибка отправки: {e}")
    
    def _update_from_app(self):
        """Обновляет значения из основного приложения"""
        try:
            if hasattr(self.app, 'tick_ms'):
                self.vars['tick_ms'].set(str(self.app.tick_ms))
            if hasattr(self.app, 'rms_strength'):
                self.vars['rms_strength'].set(str(self.app.rms_strength))
            if hasattr(self.app, 'max_age'):
                self.vars['max_age'].set(str(self.app.max_age))
            if hasattr(self.app, 'aging_speed'):
                self.vars['aging_speed'].set(str(self.app.aging_speed))
            if hasattr(self.app, 'layers'):
                self.vars['layer_count'].set(str(len(self.app.layers)))
            
            # Обновляем FX
            if hasattr(self.app, 'fx'):
                for fx_name, var in self.fx_vars.items():
                    var.set(self.app.fx.get(fx_name, False))
                    
        except Exception as e:
            self._log(f"Ошибка обновления: {e}")
    
    def _update_loop(self):
        """Цикл обновления статуса"""
        try:
            # Обновляем статус
            if hasattr(self.app, 'layers') and self.app.layers:
                import numpy as np
                status_lines = []
                status_lines.append(f"Активных слоев: {len([l for l in self.app.layers if not getattr(l, 'mute', False)])}")
                
                total_cells = sum(np.sum(getattr(l, 'grid', np.array([]))) for l in self.app.layers)
                status_lines.append(f"Всего клеток: {total_cells}")
                
                if hasattr(self.app, '_profile_counter'):
                    status_lines.append(f"Кадров: {self.app._profile_counter}")
                
                # Обновляем текст статуса
                current_text = '\n'.join(status_lines[-10:])  # Последние 10 строк
                self.status_text.delete('1.0', tk.END)
                self.status_text.insert('1.0', current_text)
                
        except Exception as e:
            pass
        
        # Планируем следующее обновление
        if self.is_running and self.window:
            self.window.after(500, self._update_loop)
    
    def _log(self, message):
        """Добавляет сообщение в лог"""
        try:
            if self.window and hasattr(self, 'status_text'):
                self.status_text.insert(tk.END, f"\n{message}")
                self.status_text.see(tk.END)
        except:
            pass
    
    def get_pending_changes(self):
        """Возвращает ожидающие изменения"""
        changes = []
        try:
            while True:
                changes.append(self.settings_queue.get_nowait())
        except queue.Empty:
            pass
        return changes
    
    def stop(self):
        """Останавливает окно настроек"""
        self.is_running = False
        if self.window:
            try:
                self.window.quit()
                self.window.destroy()
            except:
                pass