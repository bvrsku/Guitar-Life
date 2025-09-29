#!/usr/bin/env python3
"""
Тест CyberHUD с реальными значениями параметров
"""

import pygame
import sys
import os

# Добавляем путь к основному модулю
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import CyberHUD

class MockApp:
    """Имитация приложения с реальными параметрами"""
    def __init__(self):
        # AUDIO параметры
        self.gain = 150  # 150%
        self.rms_strength = 85  # 85%
        self.pitch_sensitivity = 75.5
        
        # VISUAL параметры  
        self.aging_speed = 2.3
        self.max_age = 180
        self.fade_start = 90
        self.global_v_mul = 1.8
        self.fade_sat_drop = 45
        self.fade_val_drop = 30
        
        # PERF параметры
        self.fps_limit = 60
        self.cell_size = 4
        self.update_rate = 30

def main():
    pygame.init()
    
    # Создаем окно
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("CyberHUD Real Values Test")
    
    # Создаем шрифт
    font = pygame.font.SysFont("courier new", 12, bold=True)
    
    # Создаем CyberHUD
    hud = CyberHUD(font, 800, 3)
    
    # Создаем mock приложение с реальными значениями
    mock_app = MockApp()
    hud.update_from_app(mock_app)
    
    # Расширенная информация
    test_info = {
        'fps': 60,
        'cells': 15000,
        'rms': 0.0275,
        'layers': 3,
        # Добавляем реальные значения для тестирования
        'pitch_sensitivity': 75.5,
        'frequency_range': 'Mid',
    }
    
    print("🎯 Тестируем CyberHUD с реальными значениями...")
    print(f"📊 Gain: {mock_app.gain}%")
    print(f"📊 RMS Strength: {mock_app.rms_strength}%") 
    print(f"📊 Aging Speed: {mock_app.aging_speed}")
    print(f"📊 Max Age: {mock_app.max_age}")
    
    # Тестируем каждую категорию с реальными значениями
    for i, category in enumerate(hud.categories):
        print(f"\n📋 Тестируем категорию: {category}")
        
        # Переключаемся на категорию
        hud.active_category = category
        hud.scroll_offset = 0
        
        # Рисуем HUD
        screen.fill((0, 0, 0))
        
        # Киберпанк фон
        for x in range(0, 960, 30):
            for y in range(0, 800, 30):
                intensity = ((x // 30 + y // 30) % 3) * 20
                color = (0, intensity, intensity // 2)
                pygame.draw.rect(screen, color, (x, y, 30, 30))
        
        try:
            hud.draw(screen, test_info)
            
            # Статус информация
            status_font = pygame.font.Font(None, 20)
            status_lines = [
                f"🎛️ CYBERPUNK HUD - {category}",
                f"📊 Real Values Test",
                f"⚙️ Gain: {mock_app.gain}% | RMS: {mock_app.rms_strength}%",
                f"🎨 Age Speed: {mock_app.aging_speed} | Max Age: {mock_app.max_age}",
                f"🔧 Category {i+1}/{len(hud.categories)}"
            ]
            
            for j, line in enumerate(status_lines):
                if j == 0:
                    color = (0, 255, 200)  # Accent цвет
                elif j == 1:
                    color = (0, 255, 100)  # Border цвет
                else:
                    color = (0, 220, 120)  # Text цвет
                    
                text_surface = status_font.render(line, True, color)
                screen.blit(text_surface, (10, 10 + j * 22))
            
            pygame.display.flip()
            
            # Сохраняем скриншот
            filename = f"cyberhud_real_{category.lower()}_screenshot.png"
            pygame.image.save(screen, filename)
            print(f"📸 Скриншот с реальными значениями: {filename}")
            
        except Exception as e:
            print(f"❌ Ошибка при отрисовке '{category}': {e}")
            import traceback
            traceback.print_exc()
        
        pygame.time.wait(300)
    
    print("\n🎉 Тест с реальными значениями завершен!")
    print("📁 Созданы скриншоты с реальными значениями:")
    for category in hud.categories:
        print(f"   • cyberhud_real_{category.lower()}_screenshot.png")
    
    pygame.quit()

if __name__ == "__main__":
    main()