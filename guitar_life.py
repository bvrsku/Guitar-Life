
import sys
import math
import random
import queue
import numpy as np
import pygame
import sounddevice as sd
import librosa
import tkinter as tk
from tkinter import ttk
--------------------
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CHANNELS = 1
FPS = 60
TICK_MS = 120
GRID_W = 120
GRID_H = 70
CELL_SIZE = 8
BG_COLOR = (10, 10, 12)
CELL_COLOR = (56, 189, 248)
SPAWN_BASE = 5
SPAWN_SCALE = 380
FREQ_MIN = 70.0 
FREQ_MAX = 500.0    
MIN_NOTE_FREQ = 60.0
VOLUME_SCALE = 8.0


 --------------------
def choose_settings():
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    root = tk.Tk()
    root.title("Настройки")

    tk.Label(root, text="Выберите входное устройство:").pack(padx=10, pady=5)
    device_var = tk.StringVar(value=input_devices[0]['name'])
    device_combo = ttk.Combobox(root, values=[d['name'] for d in input_devices], textvariable=device_var, state='readonly')
    device_combo.pack(padx=10, pady=5)

    tk.Label(root, text="Выберите правило клеточного автомата:").pack(padx=10, pady=5)
    rules = ["Conway", "HighLife", "Seeds"]
    rule_var = tk.StringVar(value=rules[0])
    rule_combo = ttk.Combobox(root, values=rules, textvariable=rule_var, state='readonly')
    rule_combo.pack(padx=10, pady=5)

    selection = {}

    def on_ok():
        selection['device'] = device_combo.get()
        selection['rule'] = rule_combo.get()
        root.destroy()

    tk.Button(root, text="OK", command=on_ok).pack(pady=10)
    root.mainloop()
    return selection

------------------
def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status, file=sys.stderr)
    mono = indata[:, 0].astype(np.float32)
    rms = np.sqrt(np.mean(mono ** 2))
    try:
        f0 = librosa.yin(mono, fmin=FREQ_MIN, fmax=FREQ_MAX, sr=SAMPLE_RATE)
        pitch = np.median(f0[np.isfinite(f0)])
    except Exception:
        pitch = 0.0
    try:
        pitch_queue.put_nowait(pitch)
        rms_queue.put_nowait(rms)
    except queue.Full:
        pass

def start_audio_stream(device_name):
    global stream
    device_id = None
    for i,d in enumerate(sd.query_devices()):
        if d['name'] == device_name:
            device_id = i
            break
    if device_id is None:
        print("Устройство не найдено!")
        sys.exit(1)

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype='float32',
        channels=CHANNELS,
        device=device_id,
        callback=audio_callback
    )
 
 --------------------
def step_life(grid, rule):
    H, W = grid.shape
    new = np.zeros_like(grid, dtype=bool)
    padded = np.pad(grid, ((1,1),(1,1)), mode='constant', constant_values=0)
    neighbors = sum([
        padded[0:H,0:W], padded[0:H,1:W+1], padded[0:H,2:W+2],
        padded[1:H+1,0:W], padded[1:H+1,2:W+2],
        padded[2:H+2,0:W], padded[2:H+2,1:W+1], padded[2:H+2,2:W+2],
    ])

    if rule == "Conway":
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & (neighbors==3))] = True
    elif rule == "HighLife":
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & ((neighbors==3)|(neighbors==6)))] = True
    elif rule == "Seeds":
        new[(~grid & (neighbors==2))] = True
    else:
        new = grid.copy()

    return new

def spawn_cells(grid, count):
    H, W = grid.shape
    if count <= 0: return
    clusters = max(1, count//60)
    left = count
    for _ in range(clusters):
        cr = random.randrange(0,H)
        cc = random.randrange(0,W)
        radius = max(1, random.randint(2,8))
        per = min(left, max(1,count//clusters))
        for i in range(per):
            ang = random.random()*math.tau
            r = cr + int(math.cos(ang)*(random.random()*radius))
            c = cc + int(math.sin(ang)*(random.random()*radius))
            if 0<=r<H and 0<=c<W:
                grid[r,c]=True
        left -= per

# -------------------- Основной цикл --------------------
def run_app(rule):
    pygame.init()
    screen = pygame.display.set_mode((GRID_W*CELL_SIZE, GRID_H*CELL_SIZE))
    pygame.display.set_caption("Guitar-driven Cellular Automaton")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)
    grid = np.zeros((GRID_H, GRID_W), dtype=bool)
    for _ in range(200):
        r = random.randrange(0, GRID_H)
        c = random.randrange(0, GRID_W)
        grid[r,c]=True

    last_tick = pygame.time.get_ticks()
    global running
    detected_freq = 0.0
    detected_rms = 0.0
    spawn_count = 0

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running=False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    grid[:,:]=False
                elif ev.key == pygame.K_r:
                    grid = np.random.rand(GRID_H,GRID_W)<0.12

        try:
            while True: detected_freq = pitch_queue.get_nowait() or detected_freq
        except queue.Empty: pass
        try:
            while True: detected_rms = rms_queue.get_nowait() or detected_rms
        except queue.Empty: pass

        # Очистка поля при тихом сигнале или игнорирование низких частот < 20 Hz
        if detected_rms < 0.01:
            grid[:,:] = False
            spawn_count = 0
        else:
            if detected_freq > MIN_NOTE_FREQ:  # игнорируем <20 Hz
                f_clamped = max(FREQ_MIN, min(FREQ_MAX, detected_freq))
                t = (f_clamped-FREQ_MIN)/(FREQ_MAX-FREQ_MIN)
                base = 1.0 - t
                vol = min(detected_rms*VOLUME_SCALE,1.0)
                spawn_count = int(SPAWN_BASE + SPAWN_SCALE*base*vol)
            else:
                spawn_count = 0

        now = pygame.time.get_ticks()
        if now-last_tick >= TICK_MS:
            if spawn_count>0: spawn_cells(grid, spawn_count)
            grid = step_life(grid, rule)
            last_tick = now

        screen.fill(BG_COLOR)
        for r in range(GRID_H):
            trues = np.nonzero(grid[r])[0]
            for c in trues:
                rect = pygame.Rect(c*CELL_SIZE,r*CELL_SIZE,CELL_SIZE-1,CELL_SIZE-1)
                screen.fill(CELL_COLOR, rect)

        hud_y = 6
        txt_surf = font.render(
            f"Rule: {rule} | Freq: {detected_freq:.1f} Hz | RMS: {detected_rms:.4f} | Spawn/tick: {spawn_count} | (C очистка, R seed, Esc выход)",
            True,(200,200,200)
        )
        screen.blit(txt_surf, (6,hud_y))
        pygame.display.flip()
        clock.tick(FPS)

    try:
        stream.stop()
        stream.close()
    except: pass
    pygame.quit()

 --------------------
if __name__=="__main__":
    print("Настройки...")
    sel = choose_settings()
    try:
        start_audio_stream(sel['device'])
    except Exception as e:
        print("Не удалось открыть аудио-стрим:", e, file=sys.stderr)
        sys.exit(1)
    try:
        run_app(sel['rule'])
    except KeyboardInterrupt: pass
    finally: running=False
