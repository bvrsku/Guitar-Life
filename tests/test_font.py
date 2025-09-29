#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import sys

pygame.init()

# Создаем окно
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Font Test")

# Создаем разные шрифты
try:
    font1 = pygame.font.SysFont("segoe ui", 16, bold=True)
    print("Segoe UI font loaded successfully")
except:
    font1 = pygame.font.Font(None, 16)
    print("Using default font")

try:
    font2 = pygame.font.SysFont("arial", 16, bold=True)
    print("Arial font loaded successfully")
except:
    font2 = pygame.font.Font(None, 16)
    print("Using default font for Arial")

# Тестовые строки
test_strings = [
    "Tick (ms)",
    "RMS Power (%)",
    "Max Age",
    "CONTROL PANEL",
    "Active: 0",
    "Test 123"
]

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((30, 30, 40))
    
    y = 50
    for i, text in enumerate(test_strings):
        # Тестируем оба шрифта
        try:
            surface1 = font1.render(text, True, (255, 255, 255))
            screen.blit(surface1, (50, y))
            
            surface2 = font2.render(text, True, (200, 200, 255))
            screen.blit(surface2, (400, y))
        except Exception as e:
            print(f"Error rendering '{text}': {e}")
            
        y += 30
    
    # Заголовки колонок
    header1 = font1.render("Segoe UI", True, (255, 255, 0))
    header2 = font2.render("Arial", True, (255, 255, 0))
    screen.blit(header1, (50, 20))
    screen.blit(header2, (400, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()