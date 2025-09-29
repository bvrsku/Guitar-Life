#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Главное приложение
===============================

Структурированная версия Guitar Life с разделением на модули.
"""

import pygame
import sys
import numpy as np
from typing import Optional

# Импорты из наших модулей
from core.constants import *
from core.audio import init_audio, cleanup_audio, choose_settings, start_audio_stream, update_audio_values
from core.cellular_automaton import step_life, spawn_cells, clear_grid
from core.palettes import PALETTE_STATE
from core.effects import apply_effect
from core.ui_components import SimpleColors
2
def main():
    """Главная функция приложения"""
    print("🎸 Guitar Life - Структурированная версия")
    print("=" * 50)
    
    # Инициализация pygame
    pygame.init()
    
    try:
        # Инициализация аудио системы
        init_audio()
        
        # Выбор аудио настроек
        audio_settings = choose_settings()
        if not audio_settings:
            print("⚠️  Запуск без аудио")
            audio_stream = None
        else:
            print(f"🎵 Выбрано устройство: {audio_settings['device_name']}")
            try:
                audio_stream = start_audio_stream(audio_settings['device_name'])
                print("✅ Аудио поток запущен")
            except Exception as e:
                print(f"❌ Ошибка запуска аудио: {e}")
                audio_stream = None
        
        # Создание окна
        screen_width = GRID_W * CELL_SIZE + HUD_WIDTH
        screen_height = GRID_H * CELL_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Guitar Life - Structured")
        
        # Инициализация игрового поля
        grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        age_grid = np.zeros((GRID_H, GRID_W), dtype=np.uint16)
        
        # Начальный спавн клеток
        spawn_cells(grid, 30, "Стабильные блоки")
        print(f"🎲 Начальный спавн: {np.sum(grid)} клеток")
        
        # Основные переменные
        clock = pygame.time.Clock()
        running = True
        paused = False
        current_rule = "Conway"
        spawn_method = "Стабильные блоки"
        
        # Счетчики и таймеры
        generation = 0
        frame_count = 0
        fps_timer = 0
        fps_display = 60
        
        print("🚀 Приложение запущено! Нажмите ESC для выхода")
        
        # Главный цикл
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        print(f"{'⏸️  Пауза' if paused else '▶️  Продолжение'}")
                    elif event.key == pygame.K_c:
                        clear_grid(grid, "Полная очистка")
                        age_grid.fill(0)
                        generation = 0
                        print("🧹 Поле очищено")
                    elif event.key == pygame.K_r:
                        # Случайный спавн
                        spawn_cells(grid, 50, spawn_method)
                        print(f"🎲 Спавн клеток методом: {spawn_method}")
                    elif event.key == pygame.K_1:
                        current_rule = "Conway"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_2:
                        current_rule = "HighLife"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_3:
                        current_rule = "Day&Night"
                        print(f"📋 Правило: {current_rule}")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Рисование мышью
                    mouse_x, mouse_y = event.pos
                    if mouse_x < GRID_W * CELL_SIZE:
                        grid_x = mouse_x // CELL_SIZE
                        grid_y = mouse_y // CELL_SIZE
                        if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                            grid[grid_y, grid_x] = not grid[grid_y, grid_x]
                            if grid[grid_y, grid_x]:
                                age_grid[grid_y, grid_x] = 0
                elif event.type == pygame.MOUSEMOTION:
                    # Рисование при перетаскивании
                    if pygame.mouse.get_pressed()[0]:  # Левая кнопка нажата
                        mouse_x, mouse_y = event.pos
                        if mouse_x < GRID_W * CELL_SIZE:
                            grid_x = mouse_x // CELL_SIZE
                            grid_y = mouse_y // CELL_SIZE
                            if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                                grid[grid_y, grid_x] = True
                                age_grid[grid_y, grid_x] = 0
            
            # Обновление аудио значений
            if audio_stream:
                update_audio_values()
            
            # Симуляция (если не на паузе)
            if not paused:
                # Обновляем возраст живых клеток
                age_grid[grid] += 1
                
                # Каждые несколько кадров делаем шаг автомата
                if frame_count % 3 == 0:  # Замедляем симуляцию
                    new_grid = step_life(grid, current_rule)
                    
                    # Сбрасываем возраст новых клеток
                    new_cells = new_grid & ~grid
                    age_grid[new_cells] = 0
                    
                    # Обнуляем возраст мертвых клеток
                    dead_cells = ~new_grid & grid
                    age_grid[dead_cells] = 0
                    
                    grid[:] = new_grid
                    generation += 1
            
            # Отрисовка
            screen.fill(BG_COLOR)
            
            # Отрисовка сетки (опционально)
            grid_color = (30, 30, 35)
            for x in range(0, GRID_W * CELL_SIZE, CELL_SIZE):
                pygame.draw.line(screen, grid_color, (x, 0), (x, GRID_H * CELL_SIZE))
            for y in range(0, GRID_H * CELL_SIZE, CELL_SIZE):
                pygame.draw.line(screen, grid_color, (0, y), (GRID_W * CELL_SIZE, y))
            
            # Отрисовка клеток
            for y in range(GRID_H):
                for x in range(GRID_W):
                    cell_rect = pygame.Rect(
                        x * CELL_SIZE, y * CELL_SIZE, 
                        CELL_SIZE, CELL_SIZE
                    )
                    
                    if grid[y, x]:
                        # Яркая цветовая схема на основе возраста
                        age = age_grid[y, x]
                        # Используем более яркие цвета
                        if age < 5:
                            color = (255, 255, 100)  # Желтый для молодых клеток
                        elif age < 15:
                            color = (255, 150, 50)   # Оранжевый
                        elif age < 30:
                            color = (255, 100, 100)  # Красный
                        else:
                            color = (150, 50, 200)   # Фиолетовый для старых
                        
                        pygame.draw.rect(screen, color, cell_rect)
                        # Добавляем небольшую границу для лучшей видимости
                        pygame.draw.rect(screen, (255, 255, 255), cell_rect, 1)
            
            # Улучшенный HUD
            hud_x = GRID_W * CELL_SIZE + 10
            font = pygame.font.Font(None, 20)
            title_font = pygame.font.Font(None, 28)
            
            # Фон HUD
            hud_rect = pygame.Rect(GRID_W * CELL_SIZE, 0, HUD_WIDTH, GRID_H * CELL_SIZE)
            pygame.draw.rect(screen, (25, 25, 30), hud_rect)
            pygame.draw.line(screen, (60, 60, 70), (GRID_W * CELL_SIZE, 0), (GRID_W * CELL_SIZE, GRID_H * CELL_SIZE), 2)
            
            # Заголовок
            title = title_font.render("Guitar Life", True, (255, 255, 255))
            screen.blit(title, (hud_x, 20))
            
            # Обновляем FPS каждые 30 кадров
            if frame_count % 30 == 0:
                current_time = pygame.time.get_ticks()
                if fps_timer > 0:
                    fps_display = int(30000 / (current_time - fps_timer))
                fps_timer = current_time
            
            # Статистика
            stats_y = 60
            stats = [
                f"Generation: {generation}",
                f"Rule: {current_rule}",
                f"Cells: {np.sum(grid)}",
                f"FPS: {fps_display}",
                f"Status: {'PAUSED' if paused else 'RUNNING'}",
            ]
            
            for i, text in enumerate(stats):
                if "PAUSED" in text:
                    color = (255, 200, 100)  # Желтый для паузы
                elif "RUNNING" in text:
                    color = (100, 255, 100)  # Зеленый для работы
                else:
                    color = (200, 200, 255)  # Голубой для статистики
                
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (hud_x, stats_y + i * 25))
            
            # Управление
            controls_y = stats_y + len(stats) * 25 + 30
            controls_title = font.render("Controls:", True, (255, 255, 255))
            screen.blit(controls_title, (hud_x, controls_y))
            
            controls = [
                "SPACE - Pause/Resume",
                "C - Clear field", 
                "R - Random spawn",
                "1,2,3 - Change rules",
                "Mouse - Draw cells",
                "ESC - Exit"
            ]
            
            for i, text in enumerate(controls):
                color = (180, 180, 200)
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (hud_x, controls_y + 30 + i * 22))
            
            # Обновление экрана
            pygame.display.flip()
            clock.tick(FPS)
            frame_count += 1
        
    except KeyboardInterrupt:
        print("\n👋 Выход по Ctrl+C")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Очистка ресурсов
        try:
            if 'audio_stream' in locals() and audio_stream:
                audio_stream.stop()
                audio_stream.close()
        except:
            pass
        
        cleanup_audio()
        pygame.quit()
        print("✅ Ресурсы очищены")

if __name__ == "__main__":
    main()
