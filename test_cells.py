# This file has been deleted.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест отображения клеток
"""

import pygame
import numpy as np
import sys

# Инициализация
pygame.init()

# Настройки
GRID_W, GRID_H = 120, 70
CELL_SIZE = 8
BG_COLOR = (10, 10, 12)

# Создание экрана
screen_width = GRID_W * CELL_SIZE
screen_height = GRID_H * CELL_SIZE
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Test Cells")

# Создание сетки с клетками
grid = np.zeros((GRID_H, GRID_W), dtype=bool)

# Создаем простой паттерн - несколько клеток в центре
center_y, center_x = GRID_H // 2, GRID_W // 2
for dy in range(-2, 3):
    for dx in range(-2, 3):
        y, x = center_y + dy, center_x + dx
        if 0 <= y < GRID_H and 0 <= x < GRID_W:
            grid[y, x] = True

print(f"🎲 Создано {np.sum(grid)} тестовых клеток")

# Основной цикл
clock = pygame.time.Clock()
running = True
frame_count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Очищаем экран
    screen.fill(BG_COLOR)
    
    # Рисуем клетки
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y, x]:
                cell_rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE, 
                    CELL_SIZE, CELL_SIZE
                )
                # Простой цвет - белый
                pygame.draw.rect(screen, (255, 255, 255), cell_rect)
    
    # Обновляем экран
    pygame.display.flip()
    clock.tick(60)
    
    frame_count += 1
    if frame_count == 10:
        print("✅ Тест работает - клетки должны быть видны!")

pygame.quit()
print("👋 Тест завершен")
