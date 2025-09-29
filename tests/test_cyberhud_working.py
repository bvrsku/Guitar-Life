#!/usr/bin/env python3
"""
Быстрый тест - делаем скриншот нового CyberHUD в действии
"""
import pygame
import sys
import time
sys.path.append('c:\\REPOS\\Guitar-Life')

from guitar_lifeE import App

# Инициализируем pygame
pygame.init()

print("🎮 Создаем приложение...")

# Создаем минимальный sel словарь для App
sel = {
    'device': 'Mock Audio Device',
    'device_index': 0,
    'layer_count': 3,
    'volume_scale': 8.0,
    'spawn_base': 1,
    'spawn_scale': 400
}

app = App(sel)

print("📊 Информация о CyberHUD:")
print(f"  - Видимость: {app.hud.visible}")
print(f"  - Слайдеры: {len(app.hud.sliders)}")
print(f"  - Кнопки: {len(app.hud.buttons)}")
print(f"  - Комбо-боксы: {len(app.hud.comboboxes)}")
print(f"  - Активная категория: {app.hud.active_category}")

# Делаем один кадр для проверки отрисовки
app.screen.fill((5, 5, 10))

# Рисуем HUD
info = {
    'fps': 60,
    'cells_alive': 5000,
    'rms': 0.025,
    'pitch': 440.0,
    'births': 35
}

app.hud.draw(app.screen, info)

# Сохраняем скриншот
screenshot_path = f"cyberhud_working_test_{int(time.time())}.png"
pygame.image.save(app.screen, screenshot_path)
print(f"📸 Скриншот сохранен: {screenshot_path}")

pygame.quit()
print("✅ Тест завершен - CyberHUD работает!")