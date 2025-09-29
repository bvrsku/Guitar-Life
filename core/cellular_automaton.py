#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Клеточные автоматы
===============================

Модуль содержит правила клеточных автоматов и методы спавна клеток.
"""

import numpy as np
import random
from typing import List

from .constants import CA_RULES

# Методы спавна клеток
SPAWN_METHODS = [
    "Случайные точки",           # Классический случайный спавн
    "Стабильные блоки",          # Текущий метод (блоки 2x2)
    "Глайдеры",                  # Движущиеся паттерны
    "Осцилляторы",               # Мигающие паттерны
    "Смешанный",                 # Комбинация разных типов
    "Линии",                     # Горизонтальные/вертикальные линии
    "Кресты",                    # Крестообразные паттерны
    "Кольца",                    # Круглые структуры
]

def step_life(grid: np.ndarray, rule: str) -> np.ndarray:
    """Выполнить один шаг клеточного автомата"""
    H, W = grid.shape
    
    input_count = np.sum(grid)
    
    # ИСПРАВЛЕНИЕ: принудительно конвертируем в int, чтобы арифметика работала
    padded = np.pad(grid.astype(int), ((1,1),(1,1)), mode='constant', constant_values=0)
    neighbors = (
        padded[0:H,0:W] + padded[0:H,1:W+1] + padded[0:H,2:W+2] +
        padded[1:H+1,0:W] +                     padded[1:H+1,2:W+2] +
        padded[2:H+2,0:W] + padded[2:H+2,1:W+1] + padded[2:H+2,2:W+2]
    )
    new = np.zeros_like(grid, dtype=bool)

    if rule == "Conway":
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & (neighbors==3)
        new[survive_mask | birth_mask] = True
            
    elif rule == "HighLife":
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Day&Night":
        survive_mask = grid & (((neighbors>=3)&(neighbors<=6)) | (neighbors==7) | (neighbors==8))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6)|(neighbors==7)|(neighbors==8))
        new[survive_mask | birth_mask] = True
            
    elif rule == "Replicator":
        new[(neighbors % 2) == 1] = True
    elif rule == "Seeds":
        new[(~grid & (neighbors==2))] = True
    elif rule == "Maze":  # B3/S12345
        born = (~grid) & (neighbors==3)
        survive = grid & ((neighbors>=1)&(neighbors<=5))
        new[born | survive] = True
    elif rule == "Coral":  # B3/S45678
        born = (~grid) & (neighbors==3)
        survive = grid & ((neighbors>=4)&(neighbors<=8))
        new[born | survive] = True
    elif rule == "LifeWithoutDeath":  # B3/S012345678
        born = (~grid) & (neighbors==3)
        survive = grid
        new[born | survive] = True
                    
    elif rule == "Gnarl":  # B1/S1
        born = (~grid) & (neighbors==1)
        survive = grid & (neighbors==1)
        new[born | survive] = True
    else:
        new = grid.copy()
    
    return new

# ==================== МЕТОДЫ СПАВНА ====================

def spawn_cells_random_points(grid: np.ndarray, count: int) -> None:
    """Классический случайный спавн отдельных клеток"""
    H, W = grid.shape
    if count <= 0:
        return
    
    # Создаем случайные координаты с отступом от краев
    margin = 2
    attempts = 0
    spawned = 0
    
    while spawned < count and attempts < count * 3:  # Ограничиваем попытки
        r = random.randrange(margin, H - margin)
        c = random.randrange(margin, W - margin)
        
        # Проверяем, свободна ли клетка
        if not grid[r, c]:
            grid[r, c] = True
            spawned += 1
        
        attempts += 1

def spawn_cells_stable_blocks(grid: np.ndarray, count: int) -> None:
    """Спавн стабильных блоков 2x2 (текущий метод)"""
    H, W = grid.shape
    if count <= 0 or H < 4 or W < 4:
        return
    
    blocks_to_create = max(1, count // 4)  # Один блок = 4 клетки
    
    created_blocks = 0
    attempts = 0
    max_attempts = blocks_to_create * 10
    
    while created_blocks < blocks_to_create and attempts < max_attempts:
        # Случайные координаты с отступом для блока 2x2
        r = random.randrange(2, H - 2)
        c = random.randrange(2, W - 2)
        
        # Проверяем, свободна ли область 2x2
        if not np.any(grid[r:r+2, c:c+2]):
            # Создаем блок 2x2
            grid[r:r+2, c:c+2] = True
            created_blocks += 1
        
        attempts += 1

def spawn_cells_gliders(grid: np.ndarray, count: int) -> None:
    """Спавн глайдеров - движущихся паттернов"""
    H, W = grid.shape
    if count <= 0 or H < 10 or W < 10:
        return
    
    # Паттерн глайдера (5x5)
    glider_pattern = np.array([
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=bool)
    
    gliders_to_create = max(1, count // 5)  # Один глайдер = ~5 клеток
    
    created_gliders = 0
    attempts = 0
    max_attempts = gliders_to_create * 10
    
    while created_gliders < gliders_to_create and attempts < max_attempts:
        # Случайные координаты с отступом для глайдера
        r = random.randrange(5, H - 5)
        c = random.randrange(5, W - 5)
        
        # Проверяем, свободна ли область 5x5
        if not np.any(grid[r:r+5, c:c+5]):
            # Случайный поворот глайдера
            rotations = random.randint(0, 3)
            pattern = np.rot90(glider_pattern, rotations)
            
            # Размещаем глайдер
            grid[r:r+5, c:c+5] |= pattern
            created_gliders += 1
        
        attempts += 1

def spawn_cells_oscillators(grid: np.ndarray, count: int) -> None:
    """Спавн осцилляторов - мигающих паттернов"""
    H, W = grid.shape
    if count <= 0 or H < 6 or W < 6:
        return
    
    # Различные паттерны осцилляторов
    patterns = [
        # Blinker (период 2)
        np.array([[1, 1, 1]], dtype=bool),
        # Toad (период 2)
        np.array([
            [0, 1, 1, 1],
            [1, 1, 1, 0]
        ], dtype=bool),
        # Beacon (период 2)
        np.array([
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]
        ], dtype=bool)
    ]
    
    oscillators_to_create = max(1, count // 6)  # Приблизительно 6 клеток на осциллятор
    
    created_oscillators = 0
    attempts = 0
    max_attempts = oscillators_to_create * 10
    
    while created_oscillators < oscillators_to_create and attempts < max_attempts:
        # Выбираем случайный паттерн
        pattern = random.choice(patterns)
        ph, pw = pattern.shape
        
        # Случайные координаты с отступом
        r = random.randrange(2, H - ph - 2)
        c = random.randrange(2, W - pw - 2)
        
        # Проверяем, свободна ли область
        if not np.any(grid[r:r+ph, c:c+pw]):
            # Случайный поворот
            rotations = random.randint(0, 3)
            rotated_pattern = np.rot90(pattern, rotations)
            rph, rpw = rotated_pattern.shape
            
            # Проверяем границы после поворота
            if r + rph <= H and c + rpw <= W:
                grid[r:r+rph, c:c+rpw] |= rotated_pattern
                created_oscillators += 1
        
        attempts += 1

def spawn_cells_mixed(grid: np.ndarray, count: int) -> None:
    """Смешанный спавн различных типов паттернов"""
    if count <= 0:
        return
    
    # Разделяем count между разными типами
    types_count = 4
    per_type = count // types_count
    remainder = count % types_count
    
    # Спавним разные типы
    spawn_cells_random_points(grid, per_type + (1 if remainder > 0 else 0))
    spawn_cells_stable_blocks(grid, per_type + (1 if remainder > 1 else 0))
    spawn_cells_gliders(grid, per_type + (1 if remainder > 2 else 0))
    spawn_cells_oscillators(grid, per_type + (1 if remainder > 3 else 0))

def spawn_cells_lines(grid: np.ndarray, count: int) -> None:
    """Спавн горизонтальных и вертикальных линий"""
    H, W = grid.shape
    if count <= 0:
        return
    
    lines_to_create = max(1, count // 8)  # Приблизительно 8 клеток на линию
    
    created_lines = 0
    attempts = 0
    max_attempts = lines_to_create * 10
    
    while created_lines < lines_to_create and attempts < max_attempts:
        # Случайно выбираем горизонтальную или вертикальную линию
        horizontal = random.choice([True, False])
        
        if horizontal:
            # Горизонтальная линия
            length = random.randint(3, min(12, W - 4))
            r = random.randrange(2, H - 2)
            c = random.randrange(2, W - length - 2)
            
            # Проверяем, свободна ли область
            if not np.any(grid[r, c:c+length]):
                grid[r, c:c+length] = True
                created_lines += 1
        else:
            # Вертикальная линия
            length = random.randint(3, min(12, H - 4))
            r = random.randrange(2, H - length - 2)
            c = random.randrange(2, W - 2)
            
            # Проверяем, свободна ли область
            if not np.any(grid[r:r+length, c]):
                grid[r:r+length, c] = True
                created_lines += 1
        
        attempts += 1

def spawn_cells_crosses(grid: np.ndarray, count: int) -> None:
    """Спавн крестообразных паттернов"""
    H, W = grid.shape
    if count <= 0 or H < 8 or W < 8:
        return
    
    crosses_to_create = max(1, count // 5)  # Приблизительно 5 клеток на крест
    
    created_crosses = 0
    attempts = 0
    max_attempts = crosses_to_create * 10
    
    while created_crosses < crosses_to_create and attempts < max_attempts:
        # Размер креста
        size = random.randint(2, 4)
        
        # Центр креста
        r = random.randrange(size, H - size)
        c = random.randrange(size, W - size)
        
        # Проверяем, свободна ли область креста
        cross_clear = True
        for i in range(-size, size + 1):
            if grid[r + i, c] or grid[r, c + i]:
                cross_clear = False
                break
        
        if cross_clear:
            # Создаем крест
            for i in range(-size, size + 1):
                grid[r + i, c] = True
                grid[r, c + i] = True
            created_crosses += 1
        
        attempts += 1

def spawn_cells_rings(grid: np.ndarray, count: int) -> None:
    """Спавн кольцевых структур"""
    H, W = grid.shape
    if count <= 0 or H < 10 or W < 10:
        return
    
    rings_to_create = max(1, count // 8)  # Приблизительно 8 клеток на кольцо
    
    created_rings = 0
    attempts = 0
    max_attempts = rings_to_create * 10
    
    while created_rings < rings_to_create and attempts < max_attempts:
        # Радиус кольца
        radius = random.randint(2, 4)
        
        # Центр кольца
        r = random.randrange(radius + 1, H - radius - 1)
        c = random.randrange(radius + 1, W - radius - 1)
        
        # Создаем приблизительное кольцо
        ring_points = []
        for angle in range(0, 360, 45):  # 8 точек
            dr = int(radius * np.cos(np.radians(angle)))
            dc = int(radius * np.sin(np.radians(angle)))
            ring_points.append((r + dr, c + dc))
        
        # Проверяем, свободны ли все точки кольца
        ring_clear = True
        for rr, cc in ring_points:
            if 0 <= rr < H and 0 <= cc < W:
                if grid[rr, cc]:
                    ring_clear = False
                    break
        
        if ring_clear:
            # Создаем кольцо
            for rr, cc in ring_points:
                if 0 <= rr < H and 0 <= cc < W:
                    grid[rr, cc] = True
            created_rings += 1
        
        attempts += 1

def spawn_cells(grid: np.ndarray, count: int, method: str = "Стабильные блоки") -> None:
    """Универсальная функция спавна клеток"""
    if count <= 0:
        return
    
    if method == "Случайные точки":
        spawn_cells_random_points(grid, count)
    elif method == "Стабильные блоки":
        spawn_cells_stable_blocks(grid, count)
    elif method == "Глайдеры":
        spawn_cells_gliders(grid, count)
    elif method == "Осцилляторы":
        spawn_cells_oscillators(grid, count)
    elif method == "Смешанный":
        spawn_cells_mixed(grid, count)
    elif method == "Линии":
        spawn_cells_lines(grid, count)
    elif method == "Кресты":
        spawn_cells_crosses(grid, count)
    elif method == "Кольца":
        spawn_cells_rings(grid, count)
    else:
        # По умолчанию используем стабильные блоки
        spawn_cells_stable_blocks(grid, count)

def get_available_rules() -> List[str]:
    """Получить список доступных правил клеточных автоматов"""
    return CA_RULES.copy()

def get_available_spawn_methods() -> List[str]:
    """Получить список доступных методов спавна"""
    return SPAWN_METHODS.copy()

def get_rule_description(rule: str) -> str:
    """Получить описание правила клеточного автомата"""
    descriptions = {
        "Conway": "Классическая игра Жизнь Конвея (B3/S23)",
        "HighLife": "Высокая жизнь с дополнительным рождением при 6 соседях (B36/S23)",
        "Day&Night": "День и ночь - симметричное правило (B3678/S34678)",
        "Replicator": "Репликатор - клетки рождаются при нечетном числе соседей",
        "Seeds": "Семена - клетки рождаются при 2 соседях и сразу умирают (B2/S)",
        "Maze": "Лабиринт - создает лабиринтоподобные структуры (B3/S12345)",
        "Coral": "Коралл - растущие структуры (B3/S45678)",
        "LifeWithoutDeath": "Жизнь без смерти - клетки никогда не умирают (B3/S012345678)",
        "Gnarl": "Сучок - хаотичное правило (B1/S1)"
    }
    return descriptions.get(rule, "Conway")

def clear_grid(grid: np.ndarray, clear_type: str = "Полная очистка", percentage: float = 50.0, max_age: int = 100, age_grid: np.ndarray = None):
    """Очистка сетки различными методами"""
    if clear_type == "Полная очистка":
        grid.fill(False)
    elif clear_type == "Частичная очистка":
        # Очищаем случайный процент клеток
        H, W = grid.shape
        total_cells = H * W
        cells_to_clear = int(total_cells * percentage / 100.0)
        
        # Создаем маску для очистки
        flat_indices = np.random.choice(total_cells, cells_to_clear, replace=False)
        clear_mask = np.zeros(total_cells, dtype=bool)
        clear_mask[flat_indices] = True
        clear_mask = clear_mask.reshape(H, W)
        grid[clear_mask] = False
    elif clear_type == "Очистка по возрасту" and age_grid is not None:
        # Очищаем старые клетки 
        age_threshold = max_age * 0.8  # Очищаем клетки старше 80% от максимального возраста
        old_cells_mask = age_grid > age_threshold
        grid[old_cells_mask] = False
    elif clear_type == "Случайная очистка":
        # Случайно очищаем клетки с заданной вероятностью
        H, W = grid.shape
        random_mask = np.random.random((H, W)) < (percentage / 100.0)
        grid[random_mask] = False
