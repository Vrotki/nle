from typing import List, Tuple

class cell():
    def __init__(self, coordinates: Tuple[int, int], glyph: str = ".") -> None:
        self.x: int = coordinates[0]
        self.y: int = coordinates[1]
        self.glyph: str = glyph
    
    def __str__(self) -> str:
        return(self.glyph)

class nle_map():
    def __init__(self, agent) -> None:
        self.agent = agent
        self.grid: List[List[cell]] = [[cell((0, 0))]]
        self.grid_width: int = 1
        self.grid_height: int = 1
        self.agent_coordinates: Tuple[int, int] = ((self.agent.x, self.agent.y))
        self.origin_coordinates = self.agent_coordinates
    
    def create_cell(self, coordinates: Tuple[int, int]) -> None:
        while coordinates[1] > self.origin_coordinates[1]: # If new cell would be above current origin, need to move origin up and add new rows
            self.grid_height += 1
            self.origin_coordinates = (self.origin_coordinates[0], self.origin_coordinates[1] + 1)
            self.grid.insert(0, [cell(self.to_coordinates((0, col_index))) for col_index in range(self.grid_width)])
            # Add rows to top of map until new cell is accomodated, moving origin 1 up each time

        while coordinates[0] < self.origin_coordinates[0]: # If new cell would be to left of current origin, need to move origin left and add new columns
            self.grid_width += 1
            self.origin_coordinates = (self.origin_coordinates[0] - 1, self.origin_coordinates[1])
            col_index = 0
            for row_index, row in enumerate(self.grid):
                row.insert(0, cell(self.to_coordinates((row_index, col_index))))
            # Add columns to left of map until new cell is accomodated, moving origin 1 left each time

        while self.origin_coordinates[1] - coordinates[1] >= self.grid_height: # While distance from origin to bottom of grid shows that new cell doesn't have a row yet
            self.grid_height += 1
            self.grid.append([cell(self.to_coordinates((self.grid_height - 1, col_index))) for col_index in range(self.grid_width)])
        
        while self.origin_coordinates[0] + self.grid_width <= coordinates[0]: # While distance from origin to right of grid shows that new cell doesn't have a column yet
            self.grid_width += 1
            col_index = self.grid_width - 1
            for row_index, row in enumerate(self.grid):
                row.append(cell(self.to_coordinates((row_index, col_index))))

    def to_row_col(self, coordinates: Tuple[int, int]) -> Tuple[int, int]:
        return((self.origin_coordinates[1] - coordinates[1], coordinates[0] - self.origin_coordinates[0]))

    def to_coordinates(self, row_col: Tuple[int, int]) -> Tuple[int, int]:
        return((row_col[1] + self.origin_coordinates[0], self.origin_coordinates[1] - row_col[0]))

    def get_cell(self, coordinates: Tuple[int, int]) -> cell:
        row, col = self.to_row_col(coordinates)
        try:
            return(self.grid[row][col])
        except:
            return(None)

    def update_surroundings(self, text_glyphs: List[str]) -> None:
        for text_glyph in text_glyphs:
            return
    
    def __str__(self) -> str:
        return_str = ""
        for row in self.grid:
            return_str += '['
            for column in row:
                return_str += str(column)
                if column != row[-1]:
                    return_str += ' '
            return_str += ']'
            if row != self.grid[-1]:
                return_str += ', '
            return_str += '\n'
        return(return_str)
