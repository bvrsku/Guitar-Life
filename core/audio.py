#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Аудио обработка
============================

Модуль для обработки аудиосигнала и извлечения параметров.
"""

import sys
import queue
import numpy as np
from typing import Optional, Dict, Any

from .constants import SAMPLE_RATE, BLOCK_SIZE, CHANNELS, FREQ_MIN, FREQ_MAX

# Глобальные переменные аудио
audio_rms = 0.0
audio_pitch = 0.0
audio_gain = 0.0

# Очереди для передачи данных между потоками
pitch_queue = queue.Queue(maxsize=10)
rms_queue = queue.Queue(maxsize=10)

# Импорт зависимостей с обработкой ошибок
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  librosa недоступен - анализ высоты тона отключен")

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    print("⚠️  sounddevice недоступен - аудио-вход отключен")

def audio_callback(indata, frames, time_info, status):
    """Callback функция для обработки аудио данных"""
    global audio_gain
    
    if status:
        print("Audio status:", status, file=sys.stderr)
    
    # Получаем моно сигнал
    mono = indata[:, 0].astype(np.float32)
    
    # Вычисляем RMS (среднеквадратичное значение)
    rms = float(np.sqrt(np.mean(mono ** 2)))
    
    # Применяем усиление к RMS
    rms *= audio_gain
    
    # Анализ высоты тона (если librosa доступен)
    pitch = 0.0
    if LIBROSA_AVAILABLE:
        try:
            f0 = librosa.yin(mono, fmin=FREQ_MIN, fmax=FREQ_MAX, sr=SAMPLE_RATE)
            pitch = float(np.median(f0[np.isfinite(f0)])) if np.any(np.isfinite(f0)) else 0.0
        except Exception:
            pitch = 0.0
    
    # Отправляем данные в очереди
    try:
        pitch_queue.put_nowait(pitch)
        rms_queue.put_nowait(rms)
    except queue.Full:
        pass

def start_audio_stream(device_name: str):
    """Запуск аудио потока для указанного устройства"""
    if not SD_AVAILABLE:
        raise SystemExit("sounddevice недоступен — нет аудио-входа.")
    
    # Поиск устройства по имени
    device_id = None
    for i, d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i
            break
    
    if device_id is None:
        raise SystemExit("Устройство не найдено")
    
    # Создание и запуск потока
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE, 
        blocksize=BLOCK_SIZE, 
        dtype='float32',
        channels=CHANNELS, 
        device=device_id, 
        callback=audio_callback
    )
    stream.start()
    return stream

def get_available_audio_devices():
    """Получить список доступных аудио устройств"""
    if not SD_AVAILABLE:
        return []
    
    devices = []
    try:
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:  # Только устройства ввода
                devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
    except Exception as e:
        print(f"Ошибка получения аудио устройств: {e}")
    
    return devices

def update_audio_values():
    """Обновление глобальных значений аудио из очередей"""
    global audio_rms, audio_pitch
    
    # Обновляем RMS
    try:
        while True:
            audio_rms = rms_queue.get_nowait()
    except queue.Empty:
        pass
    
    # Обновляем pitch
    try:
        while True:
            audio_pitch = pitch_queue.get_nowait()
    except queue.Empty:
        pass

def get_audio_values() -> tuple[float, float]:
    """Получить текущие значения RMS и pitch"""
    return audio_rms, audio_pitch

def set_audio_gain(gain: float):
    """Установить усиление аудио"""
    global audio_gain
    audio_gain = max(0.0, gain)

def get_audio_gain() -> float:
    """Получить текущее усиление аудио"""
    return audio_gain

def choose_settings() -> Optional[Dict[str, Any]]:
    """Выбор настроек аудио (упрощенная версия)"""
    if not SD_AVAILABLE:
        print("sounddevice недоступен")
        return None
    
    devices = get_available_audio_devices()
    if not devices:
        print("Аудио устройства не найдены")
        return None
    
    print("Доступные аудио устройства:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']} ({device['channels']} каналов)")
    
    try:
        choice = input("Выберите устройство (номер): ")
        device_index = int(choice)
        if 0 <= device_index < len(devices):
            selected_device = devices[device_index]
            return {
                'device_name': selected_device['name'],
                'device_id': selected_device['id'],
                'sample_rate': SAMPLE_RATE,
                'block_size': BLOCK_SIZE,
                'channels': CHANNELS
            }
    except (ValueError, KeyboardInterrupt):
        pass
    
    return None

def frequency_to_note(frequency: float) -> str:
    """Преобразование частоты в ноту"""
    if frequency <= 0:
        return "N/A"
    
    # Базовая частота A4 = 440 Hz
    A4 = 440.0
    
    # Названия нот
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
    # Вычисляем номер полутона относительно A4
    semitones_from_A4 = 12 * np.log2(frequency / A4)
    
    # Округляем до ближайшего полутона
    semitone = int(round(semitones_from_A4))
    
    # Вычисляем октаву и ноту
    octave = 4 + (semitone + 9) // 12  # +9 потому что A находится на 9-й позиции от C
    note_index = (semitone + 9) % 12
    
    return f"{note_names[note_index]}{octave}"

def get_audio_info() -> Dict[str, Any]:
    """Получить информацию об аудио состоянии"""
    rms, pitch = get_audio_values()
    
    return {
        'rms': rms,
        'pitch': pitch,
        'note': frequency_to_note(pitch),
        'gain': get_audio_gain(),
        'librosa_available': LIBROSA_AVAILABLE,
        'sounddevice_available': SD_AVAILABLE,
        'sample_rate': SAMPLE_RATE,
        'block_size': BLOCK_SIZE,
        'channels': CHANNELS
    }

# Инициализация очередей
def init_audio():
    """Инициализация аудио системы"""
    global pitch_queue, rms_queue
    pitch_queue = queue.Queue(maxsize=10)
    rms_queue = queue.Queue(maxsize=10)
    print("🎵 Аудио система инициализирована")

def cleanup_audio():
    """Очистка ресурсов аудио системы"""
    global pitch_queue, rms_queue
    
    # Очищаем очереди
    while not pitch_queue.empty():
        try:
            pitch_queue.get_nowait()
        except queue.Empty:
            break
    
    while not rms_queue.empty():
        try:
            rms_queue.get_nowait()
        except queue.Empty:
            break
    
    print("🎵 Аудио система очищена")
