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
        self.agent_coordinates: Tuple[int, int] = ((self.agent.x, self.agent.y))
        self.origin_coordinates = self.agent_coordinates
        return
    
    def create_cell(self, coordinates: Tuple[int, int]) -> None:
        '''
        Grid is initialized with an initial origin cell, like [[.]]
        Given grid [[.]], to add cell at coordinate (-1, 1) based on an observation:

            Identify that the grid is empty and create a and create <0, 0> cell, leading to grid []
        '''
        return

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
        try:
            return(self.grid[self.origin_coordinates[1] - coordinates[1]][coordinates[0] - self.origin_coordinates[0]])
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
