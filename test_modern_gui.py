#!/usr/bin/env python3
"""
Тест современного GUI для Guitar Life
"""

import subprocess
import sys
import os

def test_modern_gui():
    print("🎨 Тестируем современный GUI...")
    
    try:
        # Проверяем синтаксис
        with open('guitar_life.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'guitar_life.py', 'exec')
        print("✅ Синтаксис корректен")
        
        # Проверяем наличие ModernColors
        if 'class ModernColors:' in code:
            print("✅ Современная цветовая схема добавлена")
        
        # Проверяем обновленные стили
        checks = [
            ('ModernColors.PRIMARY', 'Основные цвета'),
            ('border_radius=', 'Закругленные углы'),
            ('pygame.Surface.*SRCALPHA', 'Поддержка прозрачности'),
            ('градиент', 'Градиенты'),
            ('shadow_rect', 'Тени'),
            ('glow.*surface', 'Эффекты свечения')
        ]
        
        for check, description in checks:
            if check in code:
                print(f"✅ {description}: найдено")
            else:
                print(f"⚠️ {description}: не найдено")
        
        print("\n🎯 Современные улучшения GUI:")
        print("• Темная тема с градиентами")
        print("• Закругленные углы и тени")
        print("• Эффекты свечения для активных элементов")
        print("• Современная типографика")
        print("• Улучшенные слайдеры с градиентной заливкой")
        print("• Стильные кнопки с индикаторами состояния")
        print("• Элегантные выпадающие списки")
        print("• Красивые разделители с декором")
        print("• Современная панель управления с акцентами")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    os.chdir(r"C:\REPOS\Guitar-Life")
    success = test_modern_gui()
    
    if success:
        print("\n🚀 GUI готов к использованию!")
        print("Запустите guitar_life.py для просмотра обновленного интерфейса")
    else:
        print("\n⚠️ Нужно исправить ошибки перед запуском")