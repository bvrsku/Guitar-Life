import numpy as np

def step_life_debug(grid: np.ndarray, rule: str) -> np.ndarray:
    """Debug version of step_life to see exactly what's happening"""
    h, w = grid.shape
    neighbors = np.zeros_like(grid, dtype=int)
    
    print(f"DEBUG step_life: grid shape={h}x{w}, rule={rule}")
    print(f"DEBUG step_life: input grid has {np.sum(grid)} alive cells")
    
    # Найдем живые клетки и покажем их позиции
    alive_positions = np.where(grid)
    if len(alive_positions[0]) > 0:
        print(f"DEBUG step_life: alive cells at positions:")
        for i in range(min(8, len(alive_positions[0]))):  # показываем первые 8
            r, c = alive_positions[0][i], alive_positions[1][i]
            print(f"  Cell ({r},{c})")
    
    # Подсчет соседей для каждой клетки
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            ri, rj = np.ogrid[0:h, 0:w]
            ni, nj = (ri + i) % h, (rj + j) % w
            neighbors += grid[ni, nj]
    
    # Покажем соседей для живых клеток
    if len(alive_positions[0]) > 0:
        print(f"DEBUG step_life: neighbor counts for alive cells:")
        for i in range(min(8, len(alive_positions[0]))):
            r, c = alive_positions[0][i], alive_positions[1][i]
            print(f"  Cell ({r},{c}): {neighbors[r,c]} neighbors")
    
    new = np.zeros_like(grid, dtype=bool)
    
    if rule == "Conway":
        # Живая клетка выживает при 2-3 соседях
        # Мертвая клетка рождается при 3 соседях
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & (neighbors==3)
        new[survive_mask | birth_mask] = True
        
        print(f"DEBUG step_life Conway: survive_mask has {np.sum(survive_mask)} cells")
        print(f"DEBUG step_life Conway: birth_mask has {np.sum(birth_mask)} cells")
        
    elif rule == "HighLife":
        survive_mask = grid & ((neighbors==2)|(neighbors==3))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6))
        new[survive_mask | birth_mask] = True
        
        print(f"DEBUG step_life HighLife: survive_mask has {np.sum(survive_mask)} cells")
        print(f"DEBUG step_life HighLife: birth_mask has {np.sum(birth_mask)} cells")
        
    elif rule == "Day&Night":
        survive_mask = grid & ((neighbors==3)|(neighbors==4)|(neighbors==6)|(neighbors==7)|(neighbors==8))
        birth_mask = (~grid) & ((neighbors==3)|(neighbors==6)|(neighbors==7)|(neighbors==8))
        new[survive_mask | birth_mask] = True
        
        print(f"DEBUG step_life Day&Night: survive_mask has {np.sum(survive_mask)} cells")
        print(f"DEBUG step_life Day&Night: birth_mask has {np.sum(birth_mask)} cells")
    
    print(f"DEBUG step_life: output grid has {np.sum(new)} alive cells")
    return new

# Test with a simple 2x2 block
grid = np.zeros((70, 120), dtype=bool)
grid[35:37, 60:62] = True  # 2x2 block

print("=== TESTING 2x2 BLOCK ===")
print(f"Initial: {np.sum(grid)} cells")
result = step_life_debug(grid, "Conway")
print(f"After Conway step: {np.sum(result)} cells")
print()

# Test with the exact same pattern the real code creates
grid2 = np.zeros((70, 120), dtype=bool) 
grid2[32:34, 69:71] = True  # Same position as in log

print("=== TESTING EXACT POSITION FROM LOG ===")
print(f"Initial: {np.sum(grid2)} cells")
result2 = step_life_debug(grid2, "Conway")
print(f"After Conway step: {np.sum(result2)} cells")