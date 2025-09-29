#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест GUI для Guitar Life
"""
import subprocess
import sys
import os

def main():
    # Переходим в директорию с guitar_life.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🎮 Запускаем Guitar Life...")
    print("📁 Директория:", os.getcwd())
    print("📋 Инструкция:")
    print("   - Проверьте отображение комбобоксов в верхней части GUI")
    print("   - Убедитесь, что палитры отображаются полностью")
    print("   - Проверьте, что все элементы правильно расположены")
    print("   - Нажмите ESC для выхода из игры")
    print()
    
    try:
        # Запускаем guitar_life.py
        result = subprocess.run([sys.executable, "guitar_life.py"], 
                               capture_output=False, 
                               text=True)
        
        if result.returncode == 0:
            print("✅ Игра успешно завершена")
        else:
            print(f"⚠️ Игра завершена с кодом: {result.returncode}")
    
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")

if __name__ == "__main__":
    main()