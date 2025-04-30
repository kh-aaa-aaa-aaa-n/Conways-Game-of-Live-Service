
import random

class ConwayGame:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = self.create_empty_grid()


    def create_empty_grid(self):
        """Creates a grid filled with dead cells (0)."""
        return [[0 for _ in range(self.width)] for _ in range(self.height)]

    def randomize_grid(self, probability=0.2):
        """Fills the grid randomly based on probability."""
        self.grid = [[1 if random.random() < probability else 0 for _ in range(self.width)] for _ in range(self.height)]

    def set_cell(self, row, col, state):
        """Sets the state of a specific cell."""
        if 0 <= row < self.height and 0 <= col < self.width:
            self.grid[row][col] = 1 if state else 0
        else:
            print(f"Warning: Attempted to set cell outside bounds ({row}, {col})")

    def count_live_neighbors(self, row, col):
        """Counts the live neighbors for a given cell."""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue # Skip the cell itself
                neighbor_row = (row + i + self.height) % self.height
                neighbor_col = (col + j + self.width) % self.width
                if self.grid[neighbor_row][neighbor_col] == 1:
                    count += 1
        return count

    def update_grid(self):
        """Updates the grid based on Conway's rules."""
        new_grid = self.create_empty_grid()
        for r in range(self.height):
            for c in range(self.width):
                live_neighbors = self.count_live_neighbors(r, c)
                cell_state = self.grid[r][c]

                if cell_state == 1: # If cell is alive
                    if live_neighbors < 2 or live_neighbors > 3:
                        new_grid[r][c] = 0 # Dies by underpopulation or overpopulation
                    else:
                        new_grid[r][c] = 1 # Survives
                else: # If cell is dead
                    if live_neighbors == 3:
                        new_grid[r][c] = 1 # Becomes alive by reproduction
                    else:
                        new_grid[r][c] = 0 # Stays dead
        self.grid = new_grid

    def clear_grid(self):
        """Resets the grid to all dead cells."""
        self.grid = self.create_empty_grid()

    def get_grid_for_json(self):
        return self.grid 

    def set_grid_from_data(self, grid_data):
        """
        Sets the game's grid based on incoming data 
        """
        try:
            if (isinstance(grid_data, list) and
                    len(grid_data) == self.height and
                    all(isinstance(row, list) for row in grid_data) and
                    all(len(row) == self.width for row in grid_data)):

                self.grid = [[int(cell) for cell in row] for row in grid_data]
                print("Grid successfully set from data.")
            # Example: Check if grid_data is a list of live coordinates [[r1, c1], [r2, c2]]
            elif isinstance(grid_data, list) and all(isinstance(item, list) and len(item) == 2 for item in grid_data):
                print("Setting grid from list of live coordinates.")
                self.clear_grid() # Start with an empty grid
                for r, c in grid_data:
                    if 0 <= r < self.height and 0 <= c < self.width:
                        self.grid[r][c] = 1
                    else:
                        print(f"Warning: Coordinate ({r}, {c}) out of bounds during load.")
            else:
                 print(f"Error: Cannot set grid from provided data. Invalid format or dimensions.")
                 print(f"Expected dimensions: {self.height}x{self.width}, Data type: {type(grid_data)}")
                 if isinstance(grid_data, list) and len(grid_data) > 0:
                     print(f"Received dimensions: {len(grid_data)}x{len(grid_data[0]) if isinstance(grid_data[0], list) else '?'}")
                 # Optionally raise an error or just log and keep the old grid

        except Exception as e:
            print(f"Error setting grid from data: {e}")
            # Keep the old grid in case of error