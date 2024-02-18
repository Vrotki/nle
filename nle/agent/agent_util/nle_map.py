from typing import List, Tuple

movement_commands = {
    'east': (1, 0),
    'northeast': (1, 1),
    'north': (0, 1),
    'northwest': (-1, 1),
    'west': (-1, 0),
    'southwest': (-1, -1),
    'south': (0, -1),
    'southeast': (1, -1)
}

equivalence = {
    'northeast room corner': 'horizontal wall',
    'northwest room corner': 'horizontal wall',
    'southwest room corner': 'horizontal wall',
    'southeast room corner': 'horizontal wall',
    'northeast corner': 'horizontal wall',
    'northwest corner': 'horizontal wall',
    'southwest corner': 'horizontal wall',
    'southeast corner': 'horizontal wall',
    'doorway': 'blank',
    'dark area': 'blank'
}

icons = {
    'horizontal wall': '-',
    'vertical wall': '|',
    'horizontal closed door': '+',
    'vertical closed door': '+',
    'horizontal open door': '|',
    'vertical open door': '-',
    'blank': '.',
    'agent': '@',
    'tame little dog': 'd',
    'gold piece': '$',
    'tame kitten': 'f',
    'tame pony': 'u',
    'kobold': 'k',
    'fountain': '{',
    'grave': '|',
    'bars': '#',
    'bronze ring': '=',
    'lichen': 'F',
    'stairs up': '<'
}

passable = { #Assumed any object without an entry is passable - may update and log in runtime if discovered that move command failed due to impassable object
    'horizontal wall': False,
    'vertical wall': False,
    'horizontal closed door': False,
    'vertical closed door': False,
    'bars': False
}

class cell():
    def __init__(self, coordinates: Tuple[int, int], glyph: str = " ") -> None:
        self.x: int = coordinates[0]
        self.y: int = coordinates[1]
        self.glyph: str = glyph
        self.passable: bool = True
        self.just_observed: bool = False
    
    def __str__(self) -> str:
        return(self.glyph)

    def incorporate(self, glyph_subject: List[str]) -> None:
        str_subject = ' '.join(glyph_subject)
        if str_subject in equivalence: # Converts something like northeast room corner to horizontal wall due to identical appearance and functionality
            str_subject = equivalence[str_subject]
        self.feature = str_subject
        self.glyph = icons.get(str_subject, '?')
        self.passable = passable.get(str_subject, True)

class nle_map():
    def __init__(self, agent) -> None:
        self.agent = agent
        self.grid: List[List[cell]] = [[cell((0, 0))]]
        self.grid_width: int = 1
        self.grid_height: int = 1
        self.agent_coordinates: Tuple[int, int] = ((self.agent.x, self.agent.y))
        self.origin_coordinates = self.agent_coordinates
        self.get_cell((self.agent.x, self.agent.y)).glyph = '@' # Automate this process when setting location
    
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

    def update_position(self, command: str) -> None:
        if command in movement_commands:
            coordinate_changes = movement_commands[command]
            self.get_cell(self.agent_coordinates).glyph = '.'
            self.agent.x += coordinate_changes[0]
            self.agent.y += coordinate_changes[1]
            self.agent_coordinates = (self.agent.x, self.agent.y)
            self.get_cell(self.agent_coordinates).glyph = '@'
        print('Current location: ' + str(self.agent_coordinates))

    def update_surroundings(self, text_glyphs: List[str]) -> None:
        for x in range(self.origin_coordinates[0], self.origin_coordinates[0] + self.grid_width):
            for y in range(self.origin_coordinates[1], self.origin_coordinates[1] + self.grid_height):
                self.get_cell((x, y)).just_observed = False

        for text_glyph in text_glyphs:
            interpretation = self.agent.interpret(text_glyph)
            print(interpretation)
            for location in interpretation['locations']: 
                # Need to add feature tracking: if a feature's position has previously been seen in an area, don't add copies of it when it is seen again from
                #   somewhere else
                # Maybe store a feature's position uncertainty when it is incorporated - then, combine new observations and previous uncertain features in the area
                #   into a new, refined position with lower uncertainty (the new position's possible range is the overlap of the areas of previous observations)
                # Either store a partially resolved feature as a class object or series of cell attributes
                #   Probably a class object to allow things like merging 2 observed features with a single function
                #   Need an easy way to access the locations of all features of a type and see if they overlap with the uncertainty range of a new observation
                self.create_cell(location)
                current_cell = self.get_cell(location)
                current_cell.incorporate(interpretation['subject'])
                current_cell.just_observed = True
                self.get_cell(location).incorporate(interpretation['subject'])
        
        guaranteed_visible_cells = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        while guaranteed_visible_cells:
            relative_coordinates = guaranteed_visible_cells.pop(0)
            current_cell = self.get_cell((relative_coordinates[0] + self.agent_coordinates[0], relative_coordinates[1] + self.agent_coordinates[1]))
            if current_cell:
                if not current_cell.just_observed:
                    current_cell.incorporate(['blank'])
                    current_cell.just_observed = True
                if passable.get(current_cell.feature, True):
                    if abs(relative_coordinates[0]) == 1 or abs(relative_coordinates[1]) == 1:
                        new_coordinates = (relative_coordinates[0] * 2, relative_coordinates[1] * 2)
                        if not new_coordinates in guaranteed_visible_cells:
                            guaranteed_visible_cells.append(new_coordinates)
    
    def __str__(self) -> str:
        return_str = ""
        for row in self.grid:
            #return_str += '['
            for column in row:
                return_str += str(column)
                #if column != row[-1]:
                #    return_str += ' '
            #return_str += ']'
            #if row != self.grid[-1]:
            #    return_str += ', '
            return_str += '\n'
        return(return_str)
