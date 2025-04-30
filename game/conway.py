def get_neighbors(x, y, grid):
    neighbors = [
        (x-1, y-1), (x-1, y), (x-1, y+1),
        (x, y-1),             (x, y+1),
        (x+1, y-1), (x+1, y), (x+1, y+1)
    ]
    return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(grid) and 0 <= ny < len(grid[0])]

def next_generation(grid):
    new_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            alive_neighbors = sum(grid[x][y] for x, y in get_neighbors(i, j, grid))
            
            if grid[i][j] == 1:
                if alive_neighbors < 2 or alive_neighbors > 3:
                    new_grid[i][j] = 0  # Cell dies
                else:
                    new_grid[i][j] = 1  # Cell stays alive
            else:
                if alive_neighbors == 3:
                    new_grid[i][j] = 1  # Cell becomes alive
    return new_grid
