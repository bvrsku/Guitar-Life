#!/usr/bin/env python3
"""
Простой тест для проверки ползунков без запуска полного приложения
"""
import os
import sys
import subprocess

def test_guitar_life():
    try:
        print("Запуск Guitar Life для тестирования ползунков...")
        print("ИНСТРУКЦИИ ДЛЯ ТЕСТИРОВАНИЯ:")
        print("1. Приложение должно запуститься без ошибок")
        print("2. Попробуйте перетащить различные ползунки")
        print("3. Проверьте скроллинг GUI")
        print("4. Нажмите Ctrl+C в терминале для остановки")
        print("="*50)
        
        # Запускаем приложение
        result = subprocess.run([sys.executable, "guitar_life.py"], 
                              cwd=r"C:\REPOS\Guitar-Life",
                              timeout=None)
        
        if result.returncode == 0:
            print("Приложение завершилось корректно")
        else:
            print(f"Приложение завершилось с кодом: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\nТестирование прервано пользователем")
    except subprocess.TimeoutExpired:
        print("Тестирование прервано по таймауту")
    except Exception as e:
        print(f"Ошибка при запуске: {e}")

if __name__ == "__main__":
    test_guitar_life()