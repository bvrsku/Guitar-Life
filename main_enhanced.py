#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Улучшенная структурированная версия
================================================

Демонстрирует все возможности структурированных модулей.
"""

import pygame
import sys
import numpy as np
import time
from typing import Optional

# Импорты из наших модулей
from core.constants import *
from core.audio import init_audio, cleanup_audio, choose_settings, start_audio_stream, update_audio_values, get_audio_values
from core.cellular_automaton import step_life, spawn_cells, clear_grid, get_available_rules, get_available_spawn_methods
from core.palettes import PALETTE_STATE, hue_fire_from_t, _cached_hsv_to_rgb, get_hsv_design_palettes
from core.effects import apply_effect, AVAILABLE_EFFECTS
from core.ui_components import SimpleColors

def get_palette_color(age: int, max_age: int = 50, palette_name: str = "Fire") -> tuple:
    """Получить цвет из палитры на основе возраста"""
    if max_age <= 1:
        t = 1.0
    else:
        t = min(1.0, age / max_age)
    
    # Используем палитру Fire для демонстрации
    h, s, v = hue_fire_from_t(t)
    return _cached_hsv_to_rgb(h, s, v)

def main():
    """Главная функция приложения"""
    print("🎸 Guitar Life - Улучшенная структурированная версия")
    print("=" * 60)
    
    # Инициализация pygame
    pygame.init()
    
    try:
        # Инициализация аудио системы
        init_audio()
        
        # Выбор аудио настроек (упрощенно)
        print("🎵 Аудио система инициализирована")
        audio_stream = None  # Для простоты отключаем аудио
        
        # Создание окна
        screen_width = GRID_W * CELL_SIZE + HUD_WIDTH
        screen_height = GRID_H * CELL_SIZE
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Guitar Life - Enhanced Structured")
        
        # Инициализация игрового поля
        grid = np.zeros((GRID_H, GRID_W), dtype=bool)
        age_grid = np.zeros((GRID_H, GRID_W), dtype=np.uint16)
        
        # Начальный спавн клеток
        spawn_cells(grid, 50, "Глайдеры")
        spawn_cells(grid, 30, "Осцилляторы")
        print(f"🎲 Начальный спавн: {np.sum(grid)} клеток")
        
        # Основные переменные
        clock = pygame.time.Clock()
        running = True
        paused = False
        
        # Настройки
        current_rule = "Conway"
        spawn_method = "Стабильные блоки"
        current_palette = "Fire"
        show_grid = True
        show_effects = False
        current_effect = "trails"
        
        # Счетчики и таймеры
        generation = 0
        frame_count = 0
        fps_timer = 0
        fps_display = 60
        
        # Получаем доступные опции
        available_rules = get_available_rules()
        available_spawn_methods = get_available_spawn_methods()
        available_palettes = get_hsv_design_palettes()[:10]  # Первые 10 для демонстрации
        
        print("🚀 Приложение запущено!")
        print("📋 Доступные правила:", ", ".join(available_rules))
        print("🎨 Доступные палитры:", ", ".join(available_palettes[:5]) + "...")
        print("✨ Доступные эффекты:", ", ".join(AVAILABLE_EFFECTS[:5]) + "...")
        
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
                        spawn_cells(grid, 30, spawn_method)
                        print(f"🎲 Спавн клеток методом: {spawn_method}")
                    elif event.key == pygame.K_g:
                        show_grid = not show_grid
                        print(f"🔲 Сетка: {'включена' if show_grid else 'выключена'}")
                    elif event.key == pygame.K_e:
                        show_effects = not show_effects
                        print(f"✨ Эффекты: {'включены' if show_effects else 'выключены'}")
                    elif event.key == pygame.K_1:
                        current_rule = available_rules[0] if available_rules else "Conway"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_2:
                        current_rule = available_rules[1] if len(available_rules) > 1 else "HighLife"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_3:
                        current_rule = available_rules[2] if len(available_rules) > 2 else "Day&Night"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_4:
                        current_rule = available_rules[3] if len(available_rules) > 3 else "Seeds"
                        print(f"📋 Правило: {current_rule}")
                    elif event.key == pygame.K_TAB:
                        # Переключение метода спавна
                        current_idx = available_spawn_methods.index(spawn_method) if spawn_method in available_spawn_methods else 0
                        spawn_method = available_spawn_methods[(current_idx + 1) % len(available_spawn_methods)]
                        print(f"🎲 Метод спавна: {spawn_method}")
                    elif event.key == pygame.K_p:
                        # Переключение палитры
                        current_idx = available_palettes.index(current_palette) if current_palette in available_palettes else 0
                        current_palette = available_palettes[(current_idx + 1) % len(available_palettes)]
                        print(f"🎨 Палитра: {current_palette}")
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Рисование мышью
                    mouse_x, mouse_y = event.pos
                    if mouse_x < GRID_W * CELL_SIZE:
                        grid_x = mouse_x // CELL_SIZE
                        grid_y = mouse_y // CELL_SIZE
                        if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                            if event.button == 1:  # Левая кнопка - добавить
                                grid[grid_y, grid_x] = True
                                age_grid[grid_y, grid_x] = 0
                            elif event.button == 3:  # Правая кнопка - удалить
                                grid[grid_y, grid_x] = False
                                age_grid[grid_y, grid_x] = 0
                                
                elif event.type == pygame.MOUSEMOTION:
                    # Рисование при перетаскивании
                    buttons = pygame.mouse.get_pressed()
                    if buttons[0] or buttons[2]:  # Левая или правая кнопка
                        mouse_x, mouse_y = event.pos
                        if mouse_x < GRID_W * CELL_SIZE:
                            grid_x = mouse_x // CELL_SIZE
                            grid_y = mouse_y // CELL_SIZE
                            if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                                if buttons[0]:  # Левая - добавить
                                    grid[grid_y, grid_x] = True
                                    age_grid[grid_y, grid_x] = 0
                                elif buttons[2]:  # Правая - удалить
                                    grid[grid_y, grid_x] = False
                                    age_grid[grid_y, grid_x] = 0
            
            # Обновление аудио значений
            if audio_stream:
                update_audio_values()
            
            # Симуляция (если не на паузе)
            if not paused:
                # Обновляем возраст живых клеток
                age_grid[grid] += 1
                
                # Каждые несколько кадров делаем шаг автомата
                if frame_count % 5 == 0:  # Замедляем симуляцию
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
            if show_grid:
                grid_color = (30, 30, 35)
                for x in range(0, GRID_W * CELL_SIZE, CELL_SIZE):
                    pygame.draw.line(screen, grid_color, (x, 0), (x, GRID_H * CELL_SIZE))
                for y in range(0, GRID_H * CELL_SIZE, CELL_SIZE):
                    pygame.draw.line(screen, grid_color, (0, y), (GRID_W * CELL_SIZE, y))
            
            # Отрисовка клеток
            for y in range(GRID_H):
                for x in range(GRID_W):
                    if grid[y, x]:
                        cell_rect = pygame.Rect(
                            x * CELL_SIZE, y * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE
                        )
                        
                        # Получаем цвет из выбранной палитры
                        age = age_grid[y, x]
                        color = get_palette_color(age, 50, current_palette)
                        
                        pygame.draw.rect(screen, color, cell_rect)
                        
                        # Добавляем границу для лучшей видимости
                        if CELL_SIZE > 4:
                            border_color = tuple(min(255, c + 50) for c in color)
                            pygame.draw.rect(screen, border_color, cell_rect, 1)
            
            # Улучшенный HUD
            hud_x = GRID_W * CELL_SIZE + 10
            font = pygame.font.Font(None, 18)
            title_font = pygame.font.Font(None, 26)
            
            # Фон HUD
            hud_rect = pygame.Rect(GRID_W * CELL_SIZE, 0, HUD_WIDTH, GRID_H * CELL_SIZE)
            pygame.draw.rect(screen, (25, 25, 30), hud_rect)
            pygame.draw.line(screen, (60, 60, 70), (GRID_W * CELL_SIZE, 0), (GRID_W * CELL_SIZE, GRID_H * CELL_SIZE), 2)
            
            # Заголовок
            title = title_font.render("Guitar Life Enhanced", True, (255, 255, 255))
            screen.blit(title, (hud_x, 15))
            
            # Обновляем FPS каждые 30 кадров
            if frame_count % 30 == 0:
                current_time = pygame.time.get_ticks()
                if fps_timer > 0:
                    fps_display = int(30000 / (current_time - fps_timer))
                fps_timer = current_time
            
            # Статистика
            stats_y = 50
            stats = [
                f"Generation: {generation}",
                f"Rule: {current_rule}",
                f"Cells: {np.sum(grid)}",
                f"FPS: {fps_display}",
                f"Palette: {current_palette}",
                f"Spawn: {spawn_method[:12]}...",
                f"Status: {'PAUSED' if paused else 'RUNNING'}",
            ]
            
            for i, text in enumerate(stats):
                if "PAUSED" in text:
                    color = (255, 200, 100)
                elif "RUNNING" in text:
                    color = (100, 255, 100)
                elif "Palette:" in text:
                    color = (255, 150, 255)
                elif "Rule:" in text:
                    color = (150, 255, 150)
                else:
                    color = (200, 200, 255)
                
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (hud_x, stats_y + i * 20))
            
            # Управление
            controls_y = stats_y + len(stats) * 20 + 25
            controls_title = font.render("Controls:", True, (255, 255, 255))
            screen.blit(controls_title, (hud_x, controls_y))
            
            controls = [
                "SPACE - Pause/Resume",
                "C - Clear field", 
                "R - Random spawn",
                "G - Toggle grid",
                "E - Toggle effects",
                "1,2,3,4 - Change rules",
                "TAB - Change spawn method",
                "P - Change palette",
                "LMB - Add cells",
                "RMB - Remove cells",
                "ESC - Exit"
            ]
            
            for i, text in enumerate(controls):
                color = (180, 180, 200)
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (hud_x, controls_y + 20 + i * 16))
            
            # Дополнительная информация
            info_y = controls_y + len(controls) * 16 + 40
            info_title = font.render("Features:", True, (255, 255, 255))
            screen.blit(info_title, (hud_x, info_y))
            
            features = [
                f"Grid: {'ON' if show_grid else 'OFF'}",
                f"Effects: {'ON' if show_effects else 'OFF'}",
                f"Rules: {len(available_rules)}",
                f"Palettes: {len(available_palettes)}",
                f"Effects: {len(AVAILABLE_EFFECTS)}",
            ]
            
            for i, text in enumerate(features):
                if "ON" in text:
                    color = (100, 255, 100)
                elif "OFF" in text:
                    color = (255, 100, 100)
                else:
                    color = (200, 200, 200)
                
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (hud_x, info_y + 20 + i * 16))
            
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
