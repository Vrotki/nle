from typing import List, Tuple
from . import feature

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

class cell():
    def __init__(self, coordinates: Tuple[int, int], glyph: str = " ") -> None:
        self.x: int = coordinates[0]
        self.y: int = coordinates[1]
        self.glyph: str = glyph
        self.feature: str = 'empty'
        self.confirmed_glyph: str = None
        self.passable: bool = True
        self.just_observed: bool = False
    
    def __str__(self) -> str:
        if not self.confirmed_glyph:
            return(self.glyph)
        elif self.just_observed or self.glyph == '@':
            return(self.glyph)
        else:
            return(self.confirmed_glyph)

    def incorporate(self, glyph_subject: List[str], confirmed: bool = False) -> None:
        if glyph_subject != ['current']:
            str_subject = ' '.join(glyph_subject)
            if str_subject in feature.equivalence: # Converts something like northeast room corner to horizontal wall due to identical appearance and functionality
                str_subject = feature.equivalence[str_subject]

            self.glyph = feature.icons.get(str_subject, '?')
            self.feature = str_subject # A non-confirmed feature may be the best prediction of a mobile feature or one seen from afar

            if confirmed and not feature.mobile.get(str_subject): # A feature is only logged as confirmed if unambiguously observed and immobile
                self.confirmed_glyph = feature.icons.get(str_subject, '?') # A confirmed feature can only ever be replaced by another confirmed feature
                self.confirmed_feature = str_subject

            self.passable = feature.passable.get(str_subject, True)

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

    def update_position(self, command: str, text_message: str) -> None:
        if command in movement_commands and self.agent.allows_move(text_message):
                # Need to use It's solid stone to determine whether certain dark areas are passable
            coordinate_changes = movement_commands[command]
            self.get_cell(self.agent_coordinates).glyph = '.'
            self.agent.x += coordinate_changes[0]
            self.agent.y += coordinate_changes[1]
            self.agent_coordinates = (self.agent.x, self.agent.y)
            self.get_cell(self.agent_coordinates).glyph = '@'
        print('Current location: ' + str(self.agent_coordinates))

    def update_surroundings(self, text_glyphs: List[str]) -> None:
        feature.update_mobile_features(self) # Updates possible locations of any features that can move

        for x in range(self.origin_coordinates[0], self.origin_coordinates[0] + self.grid_width):
            for y in range(self.origin_coordinates[1], self.origin_coordinates[1] + self.grid_height):
                self.get_cell((x, y)).just_observed = False

        for text_glyph in text_glyphs:
            interpretation = self.agent.interpret(text_glyph, verbose=False)
            if interpretation['subject'] == ['current']: # If an observation is labelled as current, it only exists for purposes of verifying that a cell has just been directly observed
                for location_set in interpretation['locations']:
                    if type(location_set) == set: # Observations deemed to not be useful part-way through will not be fully converted to location sets
                        if len(location_set) == 1:
                            current_location = next(iter(location_set))
                            self.create_cell(current_location)
                            self.get_cell(current_location).just_observed = True
            else:
                for location_set in interpretation['locations']:
                    if type(location_set) == set: # Observations deemed to not be useful part-way through will not be fully converted to location sets
                        for location in location_set:
                            self.create_cell(location)
                        overlapping_features = feature.find_overlap(interpretation['subject'], location_set)
                        current_feature = None
                        if len(overlapping_features) == 1:
                            current_feature, intersection = overlapping_features[0]
                            current_feature.set_location_set(intersection)
                        elif len(overlapping_features) == 0:
                            current_feature = feature.feature(self, interpretation['subject'], location_set)
                        if current_feature and len(current_feature.location_set) == 1:
                            self.get_cell(current_feature.predicted_location).just_observed = True

        feature.print_features()

        guaranteed_visible_cells = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        while guaranteed_visible_cells:
            relative_coordinates = guaranteed_visible_cells.pop(0)
            current_cell = self.get_cell((relative_coordinates[0] + self.agent_coordinates[0], relative_coordinates[1] + self.agent_coordinates[1]))
            if current_cell:
                if not current_cell.just_observed:
                    current_cell.incorporate(['blank'], confirmed=True)
                    current_cell.just_observed = True
                if feature.passable.get(current_cell.feature, True) and current_cell.feature != 'dark area':
                    if abs(relative_coordinates[0]) == 1 or abs(relative_coordinates[1]) == 1:
                        new_coordinates = (relative_coordinates[0] * 2, relative_coordinates[1] * 2)
                        if not new_coordinates in guaranteed_visible_cells:
                            guaranteed_visible_cells.append(new_coordinates)

    def __str__(self) -> str:
        return_str = ""
        for row in self.grid:
            for column in row:
                return_str += str(column)
            return_str += '\n'
        return(return_str)
