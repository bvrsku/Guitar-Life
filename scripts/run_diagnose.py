import os
import sys

# Добавляем путь если нужно
guitar_life_path = r'c:\REPOS\Guitar-Life'
if guitar_life_path not in sys.path:
    sys.path.append(guitar_life_path)

# Меняем рабочую директорию
os.chdir(guitar_life_path)

# Импортируем и запускаем диагностику
import diagnose_display
diagnose_display.diagnose_display_issue()