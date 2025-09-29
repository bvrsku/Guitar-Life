#!/usr/bin/env python3
"""
Тестовый файл для демонстрации новой функциональности LayerGenerator
Показывает как использовать новые возможности генерации нескольких слоев изображения
с индивидуальными параметрами для каждого слоя.

Новая функциональность включает:
- Генерацию нескольких слоев из конфигураций
- Различные правила автомата для каждого слоя
- Индивидуальные методы спавна клеток
- Персональные палитры для каждого слоя
- Настройки прозрачности (alpha_live, alpha_old) для каждого слоя
- Пресеты для быстрой настройки
- Дублирование слоев с модификацией параметров
"""

# Импортируем необходимые классы из основного файла
import sys
import os

# Добавляем путь к основному файлу
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import LayerConfig, LayerGenerator
import numpy as np

def demonstrate_layer_configs():
    """Демонстрирует создание различных конфигураций слоев"""
    print("🎨 === ДЕМОНСТРАЦИЯ LayerConfig ===")
    
    # Пример 1: Классический слой Conway's Game of Life
    classic_config = LayerConfig(
        rule="Conway",
        age_palette="Радуга HSV",
        rms_palette="Огонь",
        color_mode="RMS+Age blend",
        rms_mode="multiply",
        blend_mode="normal",
        rms_enabled=True,
        alpha_live=255,  # Полная непрозрачность живых клеток
        alpha_old=180,   # Частичная прозрачность старых клеток
        mix=1.0,
        solo=False,
        mute=False,
        spawn_method="Случайные клетки",
        initial_cells=50
    )
    
    # Пример 2: Экспериментальный слой с высокой рождаемостью
    experimental_config = LayerConfig(
        rule="Высокая рождаемость",
        age_palette="Синий спектр",
        rms_palette="Холодная вода",
        color_mode="Age only",
        rms_mode="add",
        blend_mode="screen",
        rms_enabled=False,
        alpha_live=200,  # Немного прозрачные живые клетки
        alpha_old=120,   # Очень прозрачные старые клетки
        mix=0.8,
        solo=False,
        mute=False,
        spawn_method="Стабильные блоки",
        initial_cells=30
    )
    
    # Пример 3: Слой с музыкальной реактивностью
    audio_reactive_config = LayerConfig(
        rule="Lenia",
        age_palette="Пурпурный туман",
        rms_palette="Электро пульс",
        color_mode="RMS only",
        rms_mode="multiply",
        blend_mode="overlay",
        rms_enabled=True,
        alpha_live=180,  # Средняя прозрачность
        alpha_old=80,    # Низкая прозрачность для fade эффекта
        mix=1.2,         # Усиленный микс для яркости
        solo=False,
        mute=False,
        spawn_method="Глайдеры",
        initial_cells=25
    )
    
    configs = [classic_config, experimental_config, audio_reactive_config]
    
    for i, config in enumerate(configs, 1):
        print(f"\n📋 Конфигурация слоя {i}:")
        print(f"   Правило: {config.rule}")
        print(f"   Age палитра: {config.age_palette}")
        print(f"   RMS палитра: {config.rms_palette}")
        print(f"   Цветовой режим: {config.color_mode}")
        print(f"   Альфа живые/старые: {config.alpha_live}/{config.alpha_old}")
        print(f"   Метод спавна: {config.spawn_method}")
        print(f"   Начальные клетки: {config.initial_cells}")
    
    return configs

def demonstrate_layer_generator():
    """Демонстрирует использование LayerGenerator"""
    print("\n🏭 === ДЕМОНСТРАЦИЯ LayerGenerator ===")
    
    # Создаем генератор слоев
    generator = LayerGenerator()
    
    print(f"📊 Доступно правил автомата: {len(generator.available_rules)}")
    print(f"   Правила: {', '.join(generator.available_rules[:5])}...")
    
    print(f"🎨 Доступно age палитр: {len(generator.available_age_palettes)}")
    print(f"   Палитры: {', '.join(generator.available_age_palettes[:3])}...")
    
    print(f"🔊 Доступно RMS палитр: {len(generator.available_rms_palettes)}")
    print(f"   Палитры: {', '.join(generator.available_rms_palettes[:3])}...")
    
    print(f"🌱 Доступно методов спавна: {len(generator.available_spawn_methods)}")
    print(f"   Методы: {', '.join(generator.available_spawn_methods)}")
    
    # Создаем случайную конфигурацию
    print("\n🎲 Генерация случайной конфигурации:")
    random_config = generator.create_random_layer_config()
    print(f"   Случайный слой: {random_config.rule} | {random_config.spawn_method}")
    print(f"   Палитры: {random_config.age_palette} + {random_config.rms_palette}")
    print(f"   Прозрачность: α_live={random_config.alpha_live}, α_old={random_config.alpha_old}")
    
    # Создаем пресетные конфигурации
    print("\n🎯 Генерация пресетных конфигураций:")
    for preset_type in ["classic", "experimental", "balanced"]:
        preset_configs = generator.create_preset_configs(2, preset_type)
        print(f"   Пресет '{preset_type}': {len(preset_configs)} слоев")
        for i, config in enumerate(preset_configs):
            print(f"     Слой {i+1}: {config.rule} | α={config.alpha_live}")

def demonstrate_manual_layer_creation():
    """Показывает как создавать слои вручную с полным контролем параметров"""
    print("\n🔧 === РУЧНОЕ СОЗДАНИЕ СЛОЕВ ===")
    
    # Создаем несколько специализированных конфигураций
    background_layer = LayerConfig(
        rule="Conway",
        age_palette="Темная материя",
        rms_palette="Базовый синий",
        color_mode="Age only",
        rms_mode="none",
        blend_mode="normal",
        rms_enabled=False,
        alpha_live=120,   # Приглушенный фон
        alpha_old=60,     # Очень тусклые старые клетки
        mix=0.6,
        solo=False,
        mute=False,
        spawn_method="Стабильные блоки",
        initial_cells=40
    )
    
    accent_layer = LayerConfig(
        rule="Lenia", 
        age_palette="Огненный закат",
        rms_palette="Золотые искры",
        color_mode="RMS+Age blend",
        rms_mode="multiply",
        blend_mode="screen",
        rms_enabled=True,
        alpha_live=255,   # Яркие акценты
        alpha_old=200,    # Заметные переходы
        mix=1.5,          # Усиленная яркость
        solo=False,
        mute=False,
        spawn_method="Глайдеры",
        initial_cells=15  # Меньше клеток для акцентов
    )
    
    detail_layer = LayerConfig(
        rule="Высокая рождаемость",
        age_palette="Кристальная вода",
        rms_palette="Электро пульс",
        color_mode="RMS only",
        rms_mode="add",
        blend_mode="overlay",
        rms_enabled=True,
        alpha_live=180,   # Детали средней яркости
        alpha_old=90,     # Быстро исчезающие детали
        mix=0.8,
        solo=False,
        mute=False,
        spawn_method="Случайные клетки",
        initial_cells=60  # Много мелких деталей
    )
    
    multi_layer_setup = [background_layer, accent_layer, detail_layer]
    
    print("🎬 Создана конфигурация из трех слоев:")
    print("   1. Фоновый слой (Conway, приглушенный)")
    print("   2. Акцентный слой (Lenia, яркий с аудио-реактивностью)")
    print("   3. Детальный слой (Высокая рождаемость, быстрые переходы)")
    
    return multi_layer_setup

def demonstrate_transparency_control():
    """Демонстрирует управление прозрачностью слоев"""
    print("\n👻 === УПРАВЛЕНИЕ ПРОЗРАЧНОСТЬЮ ===")
    
    # Примеры различных настроек прозрачности
    transparency_examples = [
        ("Полностью непрозрачный", 255, 255),
        ("Живые яркие, старые тусклые", 255, 128),
        ("Полупрозрачный", 180, 120),
        ("Призрачный эффект", 120, 60),
        ("Едва заметный", 80, 30),
    ]
    
    print("🔧 Примеры настроек прозрачности:")
    for name, alpha_live, alpha_old in transparency_examples:
        percentage_live = (alpha_live / 255) * 100
        percentage_old = (alpha_old / 255) * 100
        print(f"   {name}:")
        print(f"     α_live: {alpha_live} ({percentage_live:.0f}%)")
        print(f"     α_old:  {alpha_old} ({percentage_old:.0f}%)")

def main():
    """Главная демонстрационная функция"""
    print("🚀 ДЕМОНСТРАЦИЯ НОВОЙ ФУНКЦИОНАЛЬНОСТИ GUITAR LIFE")
    print("=" * 60)
    print("Эта программа показывает возможности LayerGenerator для создания")
    print("нескольких слоев изображения с индивидуальными параметрами.")
    print()
    
    # Выполняем все демонстрации
    layer_configs = demonstrate_layer_configs()
    demonstrate_layer_generator()
    manual_configs = demonstrate_manual_layer_creation()
    demonstrate_transparency_control()
    
    print("\n🎮 === ГОРЯЧИЕ КЛАВИШИ В ИГРЕ ===")
    print("Для использования новой функциональности в Guitar Life:")
    print("   1-5     : Генерация 1-5 случайных слоев")
    print("   F4      : Пресет 'классические' слои")
    print("   F5      : Пресет 'экспериментальные' слои") 
    print("   F6      : Пресет 'сбалансированные' слои")
    print("   Ctrl+D  : Дублировать выбранный слой")
    print("   +/=     : Добавить случайный слой к существующим")
    
    print("\n📚 === ПРОГРАММНОЕ ИСПОЛЬЗОВАНИЕ ===")
    print("В коде можно использовать методы:")
    print("   app.generate_multiple_layers_from_configs(configs)")
    print("   app.generate_preset_layers(count, 'preset_type')")
    print("   app.generate_random_layers(count)")
    print("   app.add_layer_from_config(config)")
    print("   app.update_layer_transparency(index, alpha_live, alpha_old)")
    print("   app.duplicate_layer(index, modify_params=True)")
    
    print("\n✅ Демонстрация завершена! Теперь вы можете:")
    print("   - Создавать слои с индивидуальными правилами автомата")
    print("   - Настраивать методы спавна клеток для каждого слоя")
    print("   - Выбирать палитры возраста и RMS отдельно")
    print("   - Управлять прозрачностью alpha_live и alpha_old")
    print("   - Использовать пресеты для быстрой настройки")
    print("   - Дублировать и модифицировать существующие слои")

if __name__ == "__main__":
    main()