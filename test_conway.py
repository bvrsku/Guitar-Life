import numpy as np

def step_life_test(grid: np.ndarray, rule: str) -> np.ndarray:
    """Test version of step_life with debug output"""
    h, w = grid.shape
    neighbors = np.zeros_like(grid, dtype=int)
    
    # Подсчет соседей для каждой клетки
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            ri, rj = np.ogrid[0:h, 0:w]
            ni, nj = (ri + i) % h, (rj + j) % w
            neighbors += grid[ni, nj]
    
    new = np.zeros_like(grid, dtype=bool)
    
    if rule == "Conway":
        # Живая клетка выживает при 2-3 соседях
        # Мертвая клетка рождается при 3 соседях
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & (neighbors==3))] = True
    elif rule == "HighLife":
        new[(grid & ((neighbors==2)|(neighbors==3))) | (~grid & ((neighbors==3)|(neighbors==6)))] = True
    elif rule == "Day&Night":
        new[(grid & ((neighbors==3)|(neighbors==4)|(neighbors==6)|(neighbors==7)|(neighbors==8))) | 
            (~grid & ((neighbors==3)|(neighbors==6)|(neighbors==7)|(neighbors==8)))] = True
    
    return new

# Test 2x2 block - should be stable in Conway
test_grid = np.zeros((20, 20), dtype=bool)
test_grid[9:11, 9:11] = True  # 2x2 block in center

print("Initial 2x2 block:")
print(test_grid[7:13, 7:13].astype(int))
print(f"Alive cells: {np.sum(test_grid)}")

# Test one step
new_grid = step_life_test(test_grid, "Conway")
print("\nAfter one Conway step:")
print(new_grid[7:13, 7:13].astype(int))
print(f"Alive cells: {np.sum(new_grid)}")

# Check neighbors for center 2x2 area
h, w = test_grid.shape
neighbors = np.zeros_like(test_grid, dtype=int)
for i in range(-1, 2):
    for j in range(-1, 2):
        if i == 0 and j == 0:
            continue
        ri, rj = np.ogrid[0:h, 0:w]
        ni, nj = (ri + i) % h, (rj + j) % w
        neighbors += test_grid[ni, nj]

print("\nNeighbor counts for 2x2 area:")
print(neighbors[7:13, 7:13])
print("\n2x2 block cells with their neighbor counts:")
for y in range(9, 11):
    for x in range(9, 11):
        print(f"Cell ({y},{x}): alive={test_grid[y,x]}, neighbors={neighbors[y,x]}")