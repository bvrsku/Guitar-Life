#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест галочки "Приоритет старым клеткам на удаление" в Soft Clean режиме
"""

import pygame
import sys
import os
import random
import time

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_li4fe import App

class OldCellsPriorityTest:
    def __init__(self):
        """Инициализация тестового класса"""
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Test: Old Cells Priority")
        self.clock = pygame.time.Clock()
        
        # Создаём приложение
        self.app = App(self.screen)
        
        # Настраиваем тестовую среду
        self.setup_test_environment()
        
    def setup_test_environment(self):
        """Настройка тестовой среды"""
        print("=== Настройка тестовой среды ===")
        
        # Активируем Soft Clean
        self.app.set_parameter('soft_clean_enabled', True)
        print("✓ Soft Clean включён")
        
        # Устанавливаем режим "Затухание + удаление"
        self.app.set_parameter('soft_mode', 'Затухание + удаление')
        print("✓ Режим: Затухание + удаление")
        
        # Настраиваем параметры для активного удаления
        self.app.set_parameter('soft_clear_threshold', 30)  # Низкий порог
        self.app.set_parameter('max_cells_percent', 40)    # Небольшой лимит
        self.app.set_parameter('soft_kill_rate', 0.3)      # Умеренная скорость удаления
        self.app.set_parameter('age_bias', 0.7)            # Сильный bias к старым клеткам
        
        print("✓ Параметры настроены для активного удаления")
        
        # Создаём тестовые клетки разного возраста
        self.create_test_cells()
        
    def create_test_cells(self):
        """Создание тестовых клеток с разным возрастом"""
        print("\n=== Создание тестовых клеток ===")
        
        # Очищаем поле
        self.app.current_layer.clear_cells()
        
        # Создаём клетки с разными возрастами
        center_x, center_y = 600, 400
        
        # Старые клетки (возраст 100+)
        for i in range(15):
            x = center_x - 100 + random.randint(-50, 50)
            y = center_y - 100 + random.randint(-50, 50)
            if 0 <= x < 1200 and 0 <= y < 800:
                self.app.current_layer.set_cell(x, y, True)
                self.app.current_layer.ages[y, x] = 100 + random.randint(0, 50)
        
        # Средние клетки (возраст 50-99)
        for i in range(20):
            x = center_x + random.randint(-50, 50)
            y = center_y + random.randint(-50, 50)
            if 0 <= x < 1200 and 0 <= y < 800:
                self.app.current_layer.set_cell(x, y, True)
                self.app.current_layer.ages[y, x] = 50 + random.randint(0, 49)
        
        # Молодые клетки (возраст 1-49)
        for i in range(25):
            x = center_x + 100 + random.randint(-50, 50)
            y = center_y + 100 + random.randint(-50, 50)
            if 0 <= x < 1200 and 0 <= y < 800:
                self.app.current_layer.set_cell(x, y, True)
                self.app.current_layer.ages[y, x] = 1 + random.randint(0, 48)
        
        total_cells = self.app.current_layer.count_alive_cells()
        print(f"✓ Создано {total_cells} клеток:")
        print("  - Старые (100+): ~15 клеток")
        print("  - Средние (50-99): ~20 клеток") 
        print("  - Молодые (1-49): ~25 клеток")
        
    def analyze_cells_by_age(self):
        """Анализ клеток по возрасту"""
        ages = []
        for y in range(self.app.current_layer.height):
            for x in range(self.app.current_layer.width):
                if self.app.current_layer.cells[y, x]:
                    ages.append(self.app.current_layer.ages[y, x])
        
        if not ages:
            return {"total": 0, "old": 0, "middle": 0, "young": 0, "avg_age": 0}
        
        old_cells = len([age for age in ages if age >= 100])
        middle_cells = len([age for age in ages if 50 <= age < 100])
        young_cells = len([age for age in ages if age < 50])
        avg_age = sum(ages) / len(ages)
        
        return {
            "total": len(ages),
            "old": old_cells,
            "middle": middle_cells,
            "young": young_cells,
            "avg_age": avg_age
        }
    
    def test_priority_enabled(self):
        """Тест с включённым приоритетом старых клеток"""
        print("\n=== ТЕСТ 1: Приоритет старых клеток ВКЛЮЧЁН ===")
        
        # Включаем приоритет
        self.app.set_parameter('old_cells_priority', True)
        print("✓ old_cells_priority = True")
        
        # Анализ до удаления
        before = self.analyze_cells_by_age()
        print(f"До удаления: {before['total']} клеток")
        print(f"  - Старые: {before['old']}")
        print(f"  - Средние: {before['middle']}")
        print(f"  - Молодые: {before['young']}")
        print(f"  - Средний возраст: {before['avg_age']:.1f}")
        
        # Принудительно вызываем удаление
        for _ in range(5):  # Несколько итераций для явного эффекта
            self.app.soft_population_control()
            self.app.soft_clear()
        
        # Анализ после удаления
        after = self.analyze_cells_by_age()
        print(f"\nПосле удаления: {after['total']} клеток")
        print(f"  - Старые: {after['old']}")
        print(f"  - Средние: {after['middle']}")
        print(f"  - Молодые: {after['young']}")
        print(f"  - Средний возраст: {after['avg_age']:.1f}")
        
        # Анализ результата
        old_reduction = (before['old'] - after['old']) / max(before['old'], 1) * 100
        young_reduction = (before['young'] - after['young']) / max(before['young'], 1) * 100
        
        print(f"\nАнализ удаления:")
        print(f"  - Старые клетки сократились на {old_reduction:.1f}%")
        print(f"  - Молодые клетки сократились на {young_reduction:.1f}%")
        
        if old_reduction > young_reduction + 10:
            print("✓ УСПЕХ: Старые клетки удаляются приоритетно!")
        else:
            print("✗ ПРОБЛЕМА: Приоритет старых клеток не работает")
        
        return after
    
    def test_priority_disabled(self):
        """Тест с выключенным приоритетом старых клеток"""
        print("\n=== ТЕСТ 2: Приоритет старых клеток ВЫКЛЮЧЕН ===")
        
        # Пересоздаём клетки
        self.create_test_cells()
        
        # Выключаем приоритет
        self.app.set_parameter('old_cells_priority', False)
        print("✓ old_cells_priority = False")
        
        # Анализ до удаления
        before = self.analyze_cells_by_age()
        print(f"До удаления: {before['total']} клеток")
        print(f"  - Старые: {before['old']}")
        print(f"  - Средние: {before['middle']}")
        print(f"  - Молодые: {before['young']}")
        print(f"  - Средний возраст: {before['avg_age']:.1f}")
        
        # Принудительно вызываем удаление
        for _ in range(5):  # Несколько итераций для явного эффекта
            self.app.soft_population_control()
            self.app.soft_clear()
        
        # Анализ после удаления
        after = self.analyze_cells_by_age()
        print(f"\nПосле удаления: {after['total']} клеток")
        print(f"  - Старые: {after['old']}")
        print(f"  - Средние: {after['middle']}")
        print(f"  - Молодые: {after['young']}")
        print(f"  - Средний возраст: {after['avg_age']:.1f}")
        
        # Анализ результата
        old_reduction = (before['old'] - after['old']) / max(before['old'], 1) * 100
        young_reduction = (before['young'] - after['young']) / max(before['young'], 1) * 100
        
        print(f"\nАнализ удаления:")
        print(f"  - Старые клетки сократились на {old_reduction:.1f}%")
        print(f"  - Молодые клетки сократились на {young_reduction:.1f}%")
        
        if abs(old_reduction - young_reduction) < 15:
            print("✓ УСПЕХ: Удаление происходит равномерно!")
        else:
            print("✗ ПРОБЛЕМА: Всё ещё есть приоритет при выключенной настройке")
        
        return after
    
    def test_hud_checkbox(self):
        """Тест работы checkbox в HUD"""
        print("\n=== ТЕСТ 3: Проверка HUD checkbox ===")
        
        # Проверяем наличие checkbox
        if 'old_cells_priority' in self.app.hud.buttons:
            checkbox = self.app.hud.buttons['old_cells_priority']
            print("✓ Checkbox 'old_cells_priority' найден в HUD")
            print(f"  - Состояние: {checkbox.checked}")
            
            # Тестируем переключение
            initial_state = self.app.old_cells_priority
            checkbox.toggle()
            self.app.hud.handle_checkbox_click('old_cells_priority')
            
            if self.app.old_cells_priority != initial_state:
                print("✓ Checkbox корректно переключает параметр приложения")
            else:
                print("✗ Checkbox не влияет на параметр приложения")
            
            # Проверяем синхронизацию
            self.app.hud.update_from_app()
            if checkbox.checked == self.app.old_cells_priority:
                print("✓ HUD корректно синхронизируется с приложением")
            else:
                print("✗ Проблема синхронизации HUD с приложением")
        else:
            print("✗ Checkbox 'old_cells_priority' НЕ найден в HUD!")
    
    def run_tests(self):
        """Запуск всех тестов"""
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ ПРИОРИТЕТА СТАРЫХ КЛЕТОК")
        print("=" * 60)
        
        try:
            # Тест HUD
            self.test_hud_checkbox()
            
            # Тест с включённым приоритетом
            self.test_priority_enabled()
            
            # Тест с выключенным приоритетом
            self.test_priority_disabled()
            
            print("\n" + "=" * 60)
            print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ ОШИБКА В ТЕСТАХ: {e}")
            import traceback
            traceback.print_exc()
    
    def run_interactive(self):
        """Интерактивный режим для визуального тестирования"""
        print("\n=== ИНТЕРАКТИВНЫЙ РЕЖИМ ===")
        print("Управление:")
        print("  SPACE - Переключить приоритет старых клеток")
        print("  R - Пересоздать клетки")
        print("  C - Принудительно запустить очистку")
        print("  ESC - Выход")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Переключаем приоритет
                        new_priority = not self.app.old_cells_priority
                        self.app.set_parameter('old_cells_priority', new_priority)
                        print(f"Приоритет старых клеток: {new_priority}")
                    elif event.key == pygame.K_r:
                        # Пересоздаём клетки
                        self.create_test_cells()
                        print("Клетки пересозданы")
                    elif event.key == pygame.K_c:
                        # Принудительная очистка
                        self.app.soft_population_control()
                        self.app.soft_clear()
                        stats = self.analyze_cells_by_age()
                        print(f"Очистка: {stats['total']} клеток, средний возраст {stats['avg_age']:.1f}")
                
                # Передаём события в HUD
                self.app.hud.handle_event(event)
            
            # Обновляем приложение
            self.app.update()
            self.app.draw()
            
            # Отображаем HUD
            self.app.hud.draw()
            
            # Показываем информацию о клетках
            stats = self.analyze_cells_by_age()
            info_text = f"Клетки: {stats['total']}, Старые: {stats['old']}, Молодые: {stats['young']}, Приоритет: {self.app.old_cells_priority}"
            font = pygame.font.Font(None, 36)
            text_surface = font.render(info_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(60)

def main():
    """Главная функция"""
    print("Запуск тестирования приоритета старых клеток...")
    
    test = OldCellsPriorityTest()
    
    # Запускаем автоматические тесты
    test.run_tests()
    
    # Предлагаем интерактивный режим
    response = input("\nЗапустить интерактивный режим? (y/n): ")
    if response.lower() in ['y', 'yes', 'да', 'д']:
        test.run_interactive()
    
    pygame.quit()
    print("Тестирование завершено.")

if __name__ == "__main__":
    main()