#!/usr/bin/env python3
"""
Простой стартер для Guitar Life с проверкой HUD
"""

try:
    print("Запуск Guitar Life...")
    
    # Импортируем main функцию
    from guitar_life import main
    
    print("✓ Импорт успешен")
    
    # Запускаем приложение
    main()
    
except KeyboardInterrupt:
    print("Приложение остановлено пользователем")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()