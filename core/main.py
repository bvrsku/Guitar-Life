#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main — точка входа для пакета Guitar‑Life
=========================================

Как запускать (важно):
- Файлы (__init__.py, audio.py, cellular_automaton.py, constants.py, effects.py, palettes.py, ui_components.py, и этот main.py)
  должны лежать в одной папке‑пакете (например, `guitar_life/`).
- Запускайте как модуль, чтобы сработали относительные импорты из внутренних модулей:

    python -m guitar_life.main

Горячие клавиши:
- [SPACE] — пауза/продолжить автомат
- [R] — заспавнить дополнительные клетки (ручной «пинок»)
- [1]/[2] — сменить правило клеточного автомата (вперёд/назад)
- [E] — переключить лёгкий эффект «трейлы»
- [ESC]/[Q] — выход
"""
from __future__ import annotations

import sys
import time
import math
import colorsys
from typing import Tuple

import numpy as np
import pygame

# ===== Импорт из пакета (ожидается запуск через `python -m <package>.main`) =====
from .constants import (
    GRID_W, GRID_H, CELL_SIZE, BG_COLOR, HUD_WIDTH, FPS,
    CA_RULES,
    SPAWN_BASE, SPAWN_SCALE, VOLUME_SCALE,
)
from .. import audio as audio_mod
from .cellular_automaton import step_life
from .. import cellular_automaton as ca
from ..effects import apply_trails


# ====================== Вспомогательные функции ======================

def hsv_to_rgb255(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Конвертация HSV в RGB (0..255). h в градусах (0..360)."""
    r, g, b = colorsys.hsv_to_rgb((h % 360.0) / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return int(r * 255), int(g * 255), int(b * 255)


def draw_grid_fast(surface: pygame.Surface, grid: np.ndarray, age: np.ndarray,
                    rms: float, pitch: float, max_age: int = 50) -> None:
    """Простая визуализация: оттенок вычисляем от высоты тона, яркость — от RMS, насыщенность — от возраста.
    Сделано максимально компактно и без внешних зависимостей палитр, чтобы «Main» был самодостаточным.
    """
    h = 50.0 + (math.log2(pitch / 55.0) * 60.0 if pitch > 0 else 200.0)  # грубая завязка на питч
    v = max(0.1, min(1.0, 0.2 + rms * VOLUME_SCALE))

    # Готовим пиксельную поверхность поля
    field_w = GRID_W
    field_h = GRID_H
    arr = np.zeros((field_w, field_h, 3), dtype=np.uint8)  # (w,h,3) — формат surfarray

    # Насыщенность от возраста клетки
    a_norm = np.clip(age.astype(np.float32) / float(max(1, max_age)), 0.0, 1.0)
    s = np.where(grid, 0.3 + 0.7 * a_norm, 0.0)  # живые — насыщенные, мёртвые — чёрные

    # Пересчёт HSV -> RGB поканально с векторизацией (минимум питона в цикле)
    # Чтобы избежать тяжёлого поканального HSV, дадим пару дискретных уровней s для упрощения.
    s_steps = (s * 8).astype(np.int32)
    for step in range(9):
        mask = s_steps == step
        if not mask.any():
            continue
        rgb = hsv_to_rgb255(h, step / 8.0, v)
        arr[mask] = rgb

    # Транспонируем в (w,h,3) уже готовы, blit напрямую
    pygame.surfarray.blit_array(surface, arr)


def spawn_some(grid: np.ndarray, count: int) -> None:
    """Аккуратно заспавнить клетки. Предпочтительно 2x2 блоки, иначе — точки."""
    try:
        ca.spawn_cells_stable_blocks(grid, count)
    except Exception:
        pass
    # резервный лёгкий спавн
    try:
        ca.spawn_cells_random_points(grid, max(1, count // 2))
    except Exception:
        pass


# =========================== Основной класс App ===========================

class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Guitar‑Life — Main")

        # Размеры окна: поле + простая правая панель (под будущий HUD)
        self.field_px_w = GRID_W * CELL_SIZE
        self.field_px_h = GRID_H * CELL_SIZE
        self.ui_px_w = HUD_WIDTH
        self.win_w = self.field_px_w + self.ui_px_w
        self.win_h = self.field_px_h
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.effects_trails = True

        # Сетка и возраст клеток
        self.grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        self.age = np.zeros((GRID_H, GRID_W), dtype=np.int32)

        # Параметры CA
        self.rule_index = 0
        self.rule = CA_RULES[self.rule_index]
        self.max_age = 50

        # Аудио
        self.audio_stream = None
        self.last_spawn_time = 0.0

        # Поверхности для рисования
        self.field_surface = pygame.Surface((self.field_px_w, self.field_px_h))
        self.ui_surface = pygame.Surface((self.ui_px_w, self.field_px_h))

        # Первичный спавн
        spawn_some(self.grid, 200)

        # Пробуем настроить аудио (не критично, если не получится)
        try:
            settings = audio_mod.choose_settings()
            if settings is not None:
                self.audio_stream = audio_mod.start_audio_stream(settings["device_name"])  # noqa: F841 (храним, чтобы не GC)
        except SystemExit:
            # например, sounddevice недоступен — просто продолжаем без аудио
            pass
        except Exception:
            pass

    # --------------------------- Вспомогательные ---------------------------
    def _step_automaton(self) -> None:
        new_grid = step_life(self.grid, self.rule)
        # Обновляем возраст: живые +1, мёртвые = 0
        self.age = np.where(new_grid, np.minimum(self.age + 1, self.max_age), 0)
        self.grid = new_grid

    # ----------------------------- Основной цикл -----------------------------
    def run(self) -> None:
        font = pygame.font.SysFont("consolas,dejavusansmono,consolas,menlo", 16)
        last_tick = time.perf_counter()

        while self.running:
            # --- события ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        spawn_some(self.grid, 120)
                    elif event.key == pygame.K_1:
                        self.rule_index = (self.rule_index + 1) % len(CA_RULES)
                        self.rule = CA_RULES[self.rule_index]
                    elif event.key == pygame.K_2:
                        self.rule_index = (self.rule_index - 1) % len(CA_RULES)
                        self.rule = CA_RULES[self.rule_index]
                    elif event.key == pygame.K_e:
                        self.effects_trails = not self.effects_trails

            # --- аудио обновление ---
            audio_mod.update_audio_values()
            rms, pitch = audio_mod.get_audio_values()

            # --- логика CA ---
            now = time.perf_counter()
            dt = now - last_tick
            last_tick = now

            if not self.paused:
                # Периодически даём «подкормку» от звука
                if now - self.last_spawn_time > 0.35:
                    spawn_count = int(SPAWN_BASE + SPAWN_SCALE * rms * VOLUME_SCALE * 12.0)
                    if spawn_count > 0:
                        spawn_some(self.grid, spawn_count)
                    self.last_spawn_time = now

                self._step_automaton()

            # --- отрисовка поля ---
            self.field_surface.fill(BG_COLOR)
            # Быстрый рендер в маленьком разрешении, затем апскейл до клеточного
            tiny = pygame.Surface((GRID_W, GRID_H))
            draw_grid_fast(tiny, self.grid, self.age, rms, pitch, self.max_age)
            pygame.transform.scale(tiny, (self.field_px_w, self.field_px_h), self.field_surface)

            # Эффекты
            if self.effects_trails:
                apply_trails(self.field_surface, 0.12)

            # --- UI панель (плейсхолдер вместо полноценного HUD) ---
            self.ui_surface.fill((245, 246, 248))
            text_lines = [
                f"Rule: {self.rule}  [1/2]",
                f"RMS: {rms:0.4f}",
                f"Pitch: {pitch:0.1f} Hz", 
                f"Cells alive: {int(self.grid.sum())}",
                f"Trails: {'ON' if self.effects_trails else 'OFF'}  [E]",
                f"Paused: {'YES' if self.paused else 'NO'}  [SPACE]",
                "[R] spawn • [Q/ESC] quit",
            ]
            y = 16
            for line in text_lines:
                surf = font.render(line, True, (20, 24, 28))
                self.ui_surface.blit(surf, (16, y))
                y += 24

            # --- композиция окна ---
            self.screen.blit(self.field_surface, (0, 0))
            self.screen.blit(self.ui_surface, (self.field_px_w, 0))

            pygame.display.flip()
            self.clock.tick(FPS)

        # --- финализация ---
        try:
            if self.audio_stream is not None:
                self.audio_stream.stop()
                self.audio_stream.close()
        except Exception:
            pass
        pygame.quit()


# =============================== Запускатель ===============================

def main() -> None:
    App().run()


if __name__ == "__main__":
    # NB: настоятельно рекомендуется запускать как модуль: `python -m guitar_life.main`
    # чтобы относительные импорты внутри пакета работали корректно.
    main()
