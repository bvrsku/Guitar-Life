#!/usr/bin/env python3
"""
Демонстрация проекции множественных слоев на один экран в Guitar Life

Этот файл показывает как LayerGenerator создает слои, которые все вместе
проектируются на один экран с правильным наложением и смешиванием.

Ключевые принципы проекции на один экран:
1. Все слои рендерятся в одном canvas (холсте)
2. Каждый слой накладывается с учетом прозрачности (alpha_live, alpha_old)
3. Режимы смешивания (blend_mode) определяют как слои взаимодействуют
4. Solo/mute функциональность позволяет контролировать видимость слоев
5. Финальное изображение - это композит всех активных слоев
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guitar_lifeE import LayerConfig, LayerGenerator

def demonstrate_screen_projection():
    """Демонстрирует как слои проектируются на один экран"""
    print("🖥️ === ПРОЕКЦИЯ СЛОЕВ НА ОДИН ЭКРАН ===")
    print()
    
    print("🎬 Принципы рендеринга Guitar Life:")
    print("   1. ВСЕ слои рендерятся в один общий canvas (холст)")
    print("   2. Каждый слой накладывается поверх предыдущих")
    print("   3. Прозрачность слоев контролируется alpha_live и alpha_old")
    print("   4. Режимы смешивания определяют взаимодействие слоев")
    print("   5. Финальное изображение = композит всех видимых слоев")
    print()

def demonstrate_layer_blending():
    """Показывает различные режимы смешивания слоев"""
    print("🎨 === РЕЖИМЫ СМЕШИВАНИЯ СЛОЕВ ===")
    print()
    
    blending_modes = [
        ("normal", "Обычное наложение - новый слой поверх предыдущего"),
        ("screen", "Осветление - делает изображение ярче"),
        ("overlay", "Перекрытие - контрастное смешивание"),
        ("multiply", "Умножение - затемняет изображение"),
        ("additive", "Сложение - яркое сложение цветов"),
    ]
    
    print("📋 Доступные режимы смешивания:")
    for mode, description in blending_modes:
        print(f"   • {mode:<12}: {description}")
    print()

def create_layered_composition():
    """Создает пример многослойной композиции для одного экрана"""
    print("🏗️ === СОЗДАНИЕ МНОГОСЛОЙНОЙ КОМПОЗИЦИИ ===")
    print()
    
    # Слой 1: Фоновый слой (низкая прозрачность)
    background_layer = LayerConfig(
        rule="Conway",
        age_palette="Ocean",           # Спокойная синяя палитра
        rms_palette="DeepSea",
        color_mode="Age only",
        rms_mode="none",
        blend_mode="normal",
        rms_enabled=False,
        alpha_live=100,               # Приглушенный фон (39% прозрачность)
        alpha_old=60,                 # Еще более тусклый (24% прозрачность)
        mix=0.5,                      # Низкая интенсивность
        solo=False,
        mute=False,
        spawn_method="Стабильные блоки",
        initial_cells=40
    )
    
    # Слой 2: Средний слой (средняя прозрачность)
    middle_layer = LayerConfig(
        rule="HighLife",
        age_palette="Fire",            # Теплая огненная палитра
        rms_palette="Sunset",
        color_mode="RMS+Age blend",
        rms_mode="multiply",
        blend_mode="screen",           # Осветляет композицию
        rms_enabled=True,
        alpha_live=180,               # Заметный слой (71% прозрачность)
        alpha_old=120,                # Средняя видимость (47% прозрачность)
        mix=0.8,
        solo=False,
        mute=False,
        spawn_method="Глайдеры",
        initial_cells=25
    )
    
    # Слой 3: Акцентный слой (высокая прозрачность)
    accent_layer = LayerConfig(
        rule="Lenia",
        age_palette="Neon",           # Яркая неоновая палитра
        rms_palette="Cyberpunk",
        color_mode="RMS only",
        rms_mode="add",
        blend_mode="additive",        # Яркое сложение цветов
        rms_enabled=True,
        alpha_live=220,               # Яркие акценты (86% прозрачность)
        alpha_old=150,                # Видимые переходы (59% прозрачность)
        mix=1.2,                      # Высокая интенсивность
        solo=False,
        mute=False,
        spawn_method="Осцилляторы",
        initial_cells=15
    )
    
    # Слой 4: Детальный слой (переменная прозрачность)
    detail_layer = LayerConfig(
        rule="Seeds",
        age_palette="Galaxy",          # Космическая палитра
        rms_palette="Aurora",
        color_mode="RMS+Age blend",
        rms_mode="multiply",
        blend_mode="overlay",          # Контрастное наложение
        rms_enabled=True,
        alpha_live=160,               # Детали (63% прозрачность)
        alpha_old=80,                 # Быстро исчезающие (31% прозрачность)
        mix=0.9,
        solo=False,
        mute=False,
        spawn_method="Случайные клетки",
        initial_cells=50
    )
    
    layers = [background_layer, middle_layer, accent_layer, detail_layer]
    
    print("🎭 Создана 4-слойная композиция для одного экрана:")
    print("   Слой 1 (Фон):     Conway    | Ocean/DeepSea     | α=100/60   | normal")
    print("   Слой 2 (Средний): HighLife  | Fire/Sunset       | α=180/120  | screen")
    print("   Слой 3 (Акцент):  Lenia     | Neon/Cyberpunk    | α=220/150  | additive")
    print("   Слой 4 (Детали):  Seeds     | Galaxy/Aurora     | α=160/80   | overlay")
    print()
    
    print("🖼️ Результат на экране:")
    print("   • Фоновый слой создает базовую структуру (синие тона)")
    print("   • Средний слой добавляет теплые огненные цвета через screen")
    print("   • Акцентный слой создает яркие неоновые вспышки через additive")
    print("   • Детальный слой добавляет космические акценты через overlay")
    print("   • ВСЕ 4 слоя видны ОДНОВРЕМЕННО на ОДНОМ экране!")
    print()
    
    return layers

def demonstrate_transparency_stacking():
    """Показывает как прозрачность влияет на наложение слоев"""
    print("👻 === НАЛОЖЕНИЕ ПРОЗРАЧНОСТИ ===")
    print()
    
    print("🔢 Математика наложения слоев:")
    print("   Финальный_цвет = Фон + (Слой1 * α1) + (Слой2 * α2) + ... + (СлойN * αN)")
    print()
    
    print("📊 Пример расчета для пикселя:")
    print("   Фон:        RGB(10, 10, 12)    # Темный фон")
    print("   Слой1:      RGB(0, 100, 200) * 0.39  →  RGB(0, 39, 78)")
    print("   Слой2:      RGB(200, 100, 0) * 0.71  →  RGB(142, 71, 0)")
    print("   Слой3:      RGB(0, 255, 100) * 0.86  →  RGB(0, 219, 86)")
    print("   Результат:  RGB(152, 329, 176)  →  RGB(152, 255, 176)  # После clamp")
    print()
    
    transparency_examples = [
        ("Слой-призрак", 50, 20, "Едва заметный, создает атмосферу"),
        ("Фоновый слой", 120, 80, "Видимый фон, не перекрывает детали"),
        ("Основной слой", 200, 150, "Хорошо видимый, основной контент"),
        ("Акцентный слой", 255, 200, "Полностью видимый, привлекает внимание"),
    ]
    
    print("🎨 Типичные уровни прозрачности:")
    for name, alpha_live, alpha_old, description in transparency_examples:
        live_pct = (alpha_live / 255) * 100
        old_pct = (alpha_old / 255) * 100
        print(f"   {name:<15}: α_live={alpha_live:>3} ({live_pct:>3.0f}%), α_old={alpha_old:>3} ({old_pct:>3.0f}%) - {description}")
    print()

def demonstrate_solo_mute_functionality():
    """Показывает как solo/mute влияет на проекцию"""
    print("🎚️ === УПРАВЛЕНИЕ ВИДИМОСТЬЮ СЛОЕВ ===")
    print()
    
    print("🔇 Функциональность Mute:")
    print("   • mute=True: слой НЕ рендерится (исключается из композиции)")
    print("   • mute=False: слой участвует в рендеринге")
    print()
    
    print("🔊 Функциональность Solo:")
    print("   • Если ЕСТЬ слои с solo=True: рендерятся ТОЛЬКО они")
    print("   • Если НЕТ слоев с solo=True: рендерятся все не-muted слои")
    print("   • Solo приоритетнее Mute")
    print()
    
    print("📋 Примеры комбинаций:")
    scenarios = [
        ("Все слои видимы", "solo=False, mute=False для всех", "Полная композиция"),
        ("Скрыт фон", "фон: mute=True, остальные: mute=False", "Композиция без фона"),
        ("Только акценты", "акценты: solo=True, остальные: любое", "Только акцентные слои"),
        ("Изоляция слоя", "один_слой: solo=True, остальные: любое", "Только выбранный слой"),
    ]
    
    for scenario, settings, result in scenarios:
        print(f"   {scenario:<15}: {settings:<35} → {result}")
    print()

def demonstrate_render_pipeline():
    """Объясняет pipeline рендеринга"""
    print("⚙️ === PIPELINE РЕНДЕРИНГА ===")
    print()
    
    print("🔄 Этапы рендеринга каждого кадра:")
    print("   1. Очистка canvas фоновым цветом")
    print("   2. Фильтрация слоев (solo/mute логика)")
    print("   3. Для каждого видимого слоя:")
    print("      a. Генерация цветового изображения клеток")
    print("      b. Применение правил автомата (Conway, Lenia, etc.)")
    print("      c. Применение палитр (age_palette + rms_palette)")
    print("      d. Применение прозрачности (alpha_live/alpha_old)")
    print("      e. Наложение на canvas с учетом blend_mode")
    print("   4. Применение постэффектов (blur, trails, etc.)")
    print("   5. Отображение финального изображения на экране")
    print()
    
    print("🖥️ Результат:")
    print("   ВСЕ активные слои сливаются в ОДНО финальное изображение")
    print("   Экран показывает композит всех слоев одновременно")
    print("   Каждый пиксель - это результат наложения всех слоев")
    print()

def main():
    """Главная демонстрационная функция"""
    print("🎬 ПРОЕКЦИЯ МНОЖЕСТВЕННЫХ СЛОЕВ НА ОДИН ЭКРАН")
    print("=" * 60)
    print("Guitar Life рендерит ВСЕ слои в одно финальное изображение")
    print("Каждый кадр - это композит всех активных слоев")
    print()
    
    # Демонстрируем концепции
    demonstrate_screen_projection()
    demonstrate_layer_blending()
    layers = create_layered_composition()
    demonstrate_transparency_stacking()
    demonstrate_solo_mute_functionality()
    demonstrate_render_pipeline()
    
    print("🎯 === КЛЮЧЕВЫЕ ПРИНЦИПЫ ===")
    print("✅ ОДИН ЭКРАН: Все слои проектируются на один общий экран")
    print("✅ КОМПОЗИЦИЯ: Финальное изображение = сумма всех слоев")
    print("✅ ПРОЗРАЧНОСТЬ: alpha_live/alpha_old контролируют видимость")
    print("✅ СМЕШИВАНИЕ: blend_mode определяет взаимодействие слоев")
    print("✅ УПРАВЛЕНИЕ: solo/mute позволяют контролировать видимость")
    print("✅ РЕАЛЬНОЕ ВРЕМЯ: Все происходит в реальном времени с аудио")
    print()
    
    print("🎮 === ИСПОЛЬЗОВАНИЕ В ИГРЕ ===")
    print("• Создавайте слои с разной прозрачностью для глубины")
    print("• Используйте blend_mode для интересных визуальных эффектов")
    print("• Настраивайте alpha_live/alpha_old для контроля видимости")
    print("• Экспериментируйте с solo/mute для изоляции слоев")
    print("• ВСЕ слои будут видны ОДНОВРЕМЕННО на ОДНОМ экране!")
    print()
    
    print("✨ Теперь вы понимаете как LayerGenerator создает слои,")
    print("   которые все вместе формируют одно красивое изображение!")

if __name__ == "__main__":
    main()