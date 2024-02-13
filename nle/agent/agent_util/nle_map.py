from typing import List, Tuple

class cell():
    def __init__(self, coordinates: Tuple[int, int]) -> None:
        self.x: int = coordinates[0]
        self.y: int = coordinates[1]
        self.glyph: str = "."
    
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
        '''
        Grid is initialized with an initial origin cell, like [[.]]
        Given grid [[.]], to add cell at coordinate (-1, 1) based on an observation:
        
        '''
        row, col = self.to_row_col(coordinates)
        while coordinates[1] > self.origin_coordinates[1]: # If new cell would be above current origin, need to move origin up and add new rows
            # Increase grid height by 1
            return # Add rows to top of map until new cell is accomodated, moving origin 1 up each time
        while coordinates[0] < self.origin_coordinates[0]: # If new cell would be to left of current origin, need to move origin left and add new columns
            # Increase grid width by 1
            return # Add columns to left of map until new cell is accomodated, moving origin 1 left each time

        # Need to add rows to bottom if difference between coordinates[1] and origin[1] is greater than length of grid?
        # While origin_y + grid_height <= new_y_coordinate, add rows to bottom
        #   To add y coordinate -2 when origin is (0, 0) and grid height is 1,
        #       origin_y + grid_height = 1, which is <= 2, so add a row to bototm
        #       Origin is still (0, 0), but grid height is 2
        #       origin_y + grid_height = 2, which is <= 2, so add a row to bottom
        #       Origin is still (0, 0, but grid height is 3
        #       origin_y + grid_height = 3, which is not <= 2, so done adding rows
        while self.origin_coordinates[1] + self.grid_height <= coordinates[1]: # While distance from origin to bottom of grid shows that new cell doesn't have a row yet
            # Increase grid height by 1
            return # Add rows to bottom of map until new cell is accomodated
        
        # Continue process for adding new columns

        return

    def to_row_col(self, coordinates: Tuple[int, int]) -> Tuple[int, int]:
        return((self.origin_coordinates[1] - coordinates[1], coordinates[0] - self.origin_coordinates[0]))

    def get_cell(self, coordinates: Tuple[int, int]) -> cell:
        '''
        Room example:
            !--
            -.-
            ---
            Center has coordinates (0, 0), top left has coordinates (-1, 1), and bottom right has coordinates (1, -1)
            These should be stored as cells with glyphs:
                [
                    [!, -, -],
                    [-, ., -],
                    [-, -, -]
                ]
            This means that, with (0, 0) being in the center, the map would remember the origin row, column with <0, 0> corresponding to coordinates (-1, 1):
                Get cell at coordinates (0, 0): return grid[1][1]
                    Y coordinate 0 is equal to row 1, since it is 1 less than the origin row's Y coordinate
                    X coordinate 0 is equal to column 1, since it is 1 more than the origin column's X coordinates
                Get cell at coordinates (-1, 1): return grid[0][0]
                    Y coordinate 1 is equal to row 0, since it is equal to the origin row's Y coordinate
                    X coordinate -1 is equal to column 0, since it is equal to the origin row's X coordinate
                Get cell at coordinate (1, 0): return grid [1][2]
                    Y coordinate 0 is equal to row 1, since it is 1 less than the origin row's Y coordinate
                    X coordinate 1 is equal to column 2, since it is 2 more than the origin column's X coordinate
            To gain this behavior, get_cell((x, y)) should return self.grid[self.origin_y - y][x - self.origin_x]
                get_cell((1, 0)) with self.origin = (-1, 1) returns self.grid[1 - 0][1 - (-1)] = self.grid[1][2] - intended behavior
        '''
        row, col = self.to_row_col(coordinates)
        try:
            return(self.grid[row][col])
            #return(self.grid[self.origin_coordinates[1] - coordinates[1]][coordinates[0] - self.origin_coordinates[0]])
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
                    return_str += ', '
                return_str += ']\n'
        return(return_str)
