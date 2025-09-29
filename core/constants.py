#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guitar Life - Константы и настройки
==================================

Все основные константы и настройки приложения.
"""

# Audio settings
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CHANNELS = 1
FPS = 60

# Grid and display settings
GRID_W, GRID_H = 120, 70
CELL_SIZE = 8
BG_COLOR = (10, 10, 12)
HUD_WIDTH = 520
FIELD_OFFSET_X = 0

# Cellular automaton rules
CA_RULES = [
    "Conway", "HighLife", "Day&Night", "Replicator", 
    "Seeds", "Maze", "Coral", "LifeWithoutDeath", "Gnarl"
]

# Available color palettes grouped by category
HSV_DESIGN_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight",
    # Монохромные и контрастные
    "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", 
    "Monochrome", "Sepia", "HighContrast", "LowContrast",
    # Материалы и текстуры
    "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
    "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
    # Специальные и тематические
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    # Природные цвета
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"
]

HSV_COLOR_PALETTES = [
    # Основные HSV переходы
    "Blue->Red", "Blue->Green->Yellow->Red", "Rainbow", "RainbowSmooth", 
    # Природные дизайны
    "Sunset", "Aurora", "Ocean", "Fire", "Galaxy", "Tropical", "Volcano", "DeepSea",
    # Сезонные
    "Spring", "Summer", "Autumn", "Winter", "Ice", "Forest", "Desert",
    # Научные палитры
    "Viridis", "Inferno", "Magma", "Plasma", "Cividis", "Twilight",
    # Монохромные и контрастные
    "White->LightGray->Gray->DarkGray", "BrightRed->DarkRed->DarkGray->Black", 
    "Monochrome", "Sepia", "HighContrast", "LowContrast",
    # Материалы и текстуры
    "Gold", "Silver", "Copper", "Emerald", "Sapphire", "Ruby", "Amethyst",
    "Steel", "Bronze", "Pearl", "Coral", "Jade", "Topaz",
    # Специальные и тематические
    "Ukraine", "Neon", "Cyberpunk", "Retro", "Vintage", "Pastel", "Candy",
    # Природные цвета
    "Lime", "Mint", "Peach", "Lavender", "Rose", "Sky", "Sand", "Charcoal", "Clouds", "Flame"
]

# Combined list for backward compatibility
PALETTE_OPTIONS = HSV_DESIGN_PALETTES + HSV_COLOR_PALETTES

# Audio processing settings
SPAWN_BASE, SPAWN_SCALE = 10, 10
FREQ_MIN, FREQ_MAX = 72.0, 1500.0
MIN_NOTE_FREQ = 70.0
VOLUME_SCALE = 8.0

# Default timing and threshold values
DEFAULT_CLEAR_RMS = 0.004
DEFAULT_COLOR_RMS_MIN = 0.005
DEFAULT_COLOR_RMS_MAX = 0.2
DEFAULT_TICK_MS = 20
DEFAULT_PTICK_MIN_MS = 60
DEFAULT_PTICK_MAX_MS = 120

# Clear types for different clearing methods
CLEAR_TYPES = [
    "Полная очистка",        # Complete clear - all cells
    "Частичная очистка",     # Partial clear - percentage
    "Очистка по возрасту",   # Age-based clear - old cells
    "Случайная очистка"      # Random clear - random cells
]

# Audio globals (will be updated by audio module)
audio_rms = 0.0
audio_pitch = 0.0
audio_gain = 0.0
