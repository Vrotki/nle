import random
import math
from typing import Dict, List, Tuple
from nle.env import NLE
import nle.agent.agent_util.nle_map as nle_map
import nle.agent.agent_util.feature as feature
import nle.agent.agent_util.misc_util as misc_util

int_stats: List[str] = [
    'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'depth', 'gold', 'ac', 'time', 'monster_level', 'dungeon_number','level_number', 'score'
]
scale_stats: List[str] = ['strength', 'hp', 'energy', 'xp']
str_stats = ['position', 'hunger', 'encumbrance', 'alignment', 'condition']

movement_mappings = {
    'w': 'north',
    'a': 'west',
    's': 'south',
    'd': 'east',
    'q': 'northwest',
    'e': 'northeast',
    'z': 'southwest',
    'c': 'southeast'
}

class viktor_agent:
    def __init__(self, env: NLE):
        self.x: int = 0
        self.y: int = 0
        self.env: NLE = env
        self.last_observation: Dict = {}
        self.surroundings: List[str] = []
        self.nle_map: nle_map.nle_map = nle_map.nle_map(self)
        self.stats: Dict = {}
        self.inventory: List[str] = []
        self.character_class: str = None
        self.last_text_message: str = None
        self.current_goal: str = None
        self.current_plan = None
        
    def update_stats(self, blstats: List[str]):
        self.stats['previous_position'] = self.stats.get('position', '')
        for current_value in blstats:
            split_stat = current_value.split(": ")
            current_stat_name = split_stat[0].lower().replace(" ", "_")
            if current_stat_name in int_stats:
                self.stats[current_stat_name] = int(split_stat[-1])
            elif current_stat_name in scale_stats:
                self.stats[current_stat_name], self.stats["max_" + current_stat_name] = [int(x) for x in split_stat[-1].split('/')]
            elif current_stat_name in str_stats:
                self.stats[current_stat_name] = split_stat[-1]

    def can_explore(self, location: Tuple[int, int]) -> bool:
        current_cell = self.nle_map.get_cell(location)
        if current_cell.confirmed_feature and feature.passable.get(current_cell.confirmed_feature, True):
            for relative_x, relative_y in [(-1, -1), (1, 1), (-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1)]:
                neighbor = self.nle_map.get_cell((current_cell.x + relative_x, current_cell.y + relative_y))
                if (not neighbor) or (not neighbor.confirmed_feature):
                    return(True)
        return(False)

    def get_movement_neighbors(self, location) -> List[Tuple[int, int]]:
        current_cell = self.nle_map.get_cell(location)
        neighbor_locations = []
        movement_commands = [(-1, -1), (1, 1), (-1, 0), (1, 0), (-1, 1), (1, -1), (0, 1), (0, -1)]
        random.shuffle(movement_commands)
        for relative_x, relative_y in movement_commands:
            # Random order should help avoid getting stuck in exploring the same 2 cells repeatedly and decrease direction bias
            neighbor = self.nle_map.get_cell((current_cell.x + relative_x, current_cell.y + relative_y))
            if neighbor and neighbor.confirmed_feature and feature.passable.get(neighbor.confirmed_feature, True):
                if (feature.allows_diagonals.get(current_cell.confirmed_feature, True) and feature.allows_diagonals.get(neighbor.confirmed_feature, True)) or abs(relative_x) != abs(relative_y) or (self.current_goal == 'combat' and abs(relative_x) + abs(relative_y) <= 2):
                    # Allow movement if non-diagonal or if both features allow digonal movement
                    neighbor_locations.append((neighbor.x, neighbor.y))
        return(neighbor_locations)

    def iterative_deepening(self, goal_locations: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        solution: List[Tuple[int, int]] = None
        depth_limit = 0
        while (not solution) and depth_limit <= (self.nle_map.grid_height * self.nle_map.grid_width / 2): # Eventually figure out that algorithm is stuck
            solution = self.bounded_DFS(goal_locations, depth_limit) # Could alternatively return whether increasing depth limit would lead to more paths
            depth_limit += 1
        if not solution:
            solution = []
        return(solution)

    def bounded_DFS(self, goal_locations: List[Tuple[int, int]], depth_limit: int) -> List[Tuple[int, int]]:
        frontier: List[List[Tuple[int, int]]] = [[(self.x, self.y)]]
        visited: Dict[str, bool] = {str((self.x, self.y)): True}
        while frontier:
            current_plan = frontier.pop()
            if len(current_plan) == depth_limit:
                if current_plan[-1] in goal_locations:
                    return(current_plan)
            else:
                for neighbor in self.get_movement_neighbors(current_plan[-1]):
                    str_neighbor = str(neighbor)
                    if not visited.get(str_neighbor, False):
                        frontier.append(current_plan + [neighbor])
                        visited[str_neighbor] = True
        return(None)

    def find_goal_locations(self, specified_goal=None):
        if not specified_goal:
            specified_goal = self.current_goal
        goal_locations = []
        if specified_goal == 'explore': # If exploring and no goal locations, may have to go into search procedure
            for x in range(self.nle_map.origin_coordinates[0], self.nle_map.origin_coordinates[0] + self.nle_map.grid_width):
                for y in range(self.nle_map.origin_coordinates[1] - self.nle_map.grid_height + 1, self.nle_map.origin_coordinates[1] + 1):
                    if self.can_explore((x, y)):
                        goal_locations.append((x, y))
        #elif self.current_goal == 'search': After realizing that dungeon has no ways out, start searching for hidden doors
        # Search would involve searching and marking every passable cell in the dungeon, starting with current position
        #   Treat any non-marked cell as a goal location, with search actions between each move
        elif specified_goal == 'open door':
            for x in range(self.nle_map.origin_coordinates[0], self.nle_map.origin_coordinates[0] + self.nle_map.grid_width):
                for y in range(self.nle_map.origin_coordinates[1] - self.nle_map.grid_height + 1, self.nle_map.origin_coordinates[1] + 1):
                    current_cell = self.nle_map.get_cell((x, y))
                    if current_cell.confirmed_feature and current_cell.confirmed_feature in ['horizontal closed door', 'vertical closed door']:
                        goal_locations.append((x, y))
        elif specified_goal == 'combat':
            for x in range(self.nle_map.origin_coordinates[0], self.nle_map.origin_coordinates[0] + self.nle_map.grid_width):
                for y in range(self.nle_map.origin_coordinates[1] - self.nle_map.grid_height + 1, self.nle_map.origin_coordinates[1] + 1):
                    current_cell = self.nle_map.get_cell((x, y))
                    if current_cell.just_observed and feature.mobile.get(current_cell.feature, False) and not current_cell.feature.startswith('tame '):
                        goal_locations.append((x, y))
        elif specified_goal == 'down':
            for x in range(self.nle_map.origin_coordinates[0], self.nle_map.origin_coordinates[0] + self.nle_map.grid_width):
                for y in range(self.nle_map.origin_coordinates[1] - self.nle_map.grid_height + 1, self.nle_map.origin_coordinates[1] + 1):
                    current_cell = self.nle_map.get_cell((x, y))
                    if current_cell.confirmed_feature and current_cell.confirmed_feature == 'stairs down':
                        goal_locations.append((x, y))
        elif specified_goal == 'random':
            for x in range(self.nle_map.origin_coordinates[0], self.nle_map.origin_coordinates[0] + self.nle_map.grid_width):
                for y in range(self.nle_map.origin_coordinates[1] - self.nle_map.grid_height + 1, self.nle_map.origin_coordinates[1] + 1):
                    if x != self.x and y != self.y:
                        goal_locations.append((x, y))
        return(goal_locations)

    def generate_goal(self):
        return_value = 'explore'
        # Generates an overall priority for the agent, based on current circumstances
        if self.is_combat_message(self.last_text_message) or self.find_goal_locations(specified_goal='combat'):
            return_value = 'combat'
        
        elif self.find_goal_locations(specified_goal='down'):
            return_value = 'down'

        elif (feature.features.get('horizontal closed door', []) or feature.features.get('vertical closed door', [])) and self.find_goal_locations(specified_goal='open door'):
            # Check for any door features - if so, check to make sure there is at least 1 confirmed door on the map
            # Only the 2nd check is necessary, but it only needs to be done if the first check is true, and the first check is much less expensive
            return_value = 'open door'

        if return_value == self.current_goal and not self.current_plan: # If procedure resulted in empty plan, try something else
            if return_value != 'explore':
                return_value = 'explore'
            else:
                return_value = 'random'

        if return_value != self.current_goal:
            self.current_plan = None
        return(return_value)

    def think(self): # Note - use more commmand to escape prompts like eat
        determined_action = 'wait'
        # Think about current priorities, like explore, find a specific feature seen earlier, fight, eat, loot
        self.current_goal = self.generate_goal()

        # Identify what type of cell to look for - a cell closer to an previously seen feature, a cell with at least 1 non-confirmed neighbor, monsters, etc.
        # Search for a collection of cells that qualify, and somehow choose between them
        goal_locations = self.find_goal_locations()

        if len(goal_locations) > 0: # Need to leave open door procedure after kicking down door, shouldn't see any more door features
            if self.current_plan:
                self.current_plan.pop(0) # First action was already done last time
                if len(self.current_plan) >= 2 and type(self.current_plan[1]) == str and type(self.current_plan[0]) == tuple:
                    self.current_plan.pop(0) # Don't allow isolated coordinates, they need to be in pairs

            if self.current_plan and (len(self.current_plan) >= 2 or type(self.current_plan[0]) == str) and self.current_plan[-1] in goal_locations:
                # If plan from last time still have another move action and has a desirable final destination, continue following it
                plan = self.current_plan
            else:
                plan = self.iterative_deepening(goal_locations)
            
            # Tune plan beyond just movement to goal location
            if self.current_goal == 'open door': # Insert any relevant non-movement actions after iterative DFS to reach goal location
                if self.last_text_message.startswith('This door is locked') or \
                        self.last_text_message.startswith('WHAMM'):
                    plan.insert(0, 'kick')
            elif self.current_goal == 'combat' and not plan:
                goal_locations = self.find_goal_locations(specified_goal='random')
                plan = self.iterative_deepening(goal_locations)
            elif self.current_goal == 'down' and (self.x, self.y) in goal_locations:
                plan = ['down']

            if (plan and type(plan[0]) == str) or len(plan) > 1: # Plan requires at least 1 manual command or 2+ coordinates
                if type(plan[0]) == str:
                    first_action = plan[0]
                else:
                    first_action = nle_map.reverse_movement_commands[str((plan[1][0] - plan[0][0], plan[1][1] - plan[0][1]))]
                self.current_plan = plan
                determined_action = first_action
            else: # If stuck on an explore, Ai should literally move in a random valid direction
                print('Plan too short: ' + str(self.current_plan))
        else:
            self.current_plan = None
        return(determined_action)

    def act(self, specified_command = None, display = True):
        if specified_command:
            command = movement_mappings.get(specified_command, specified_command)
            self.current_goal = None
            self.current_plan = None
        else:
            command = self.think()
        try:
            obsv, reward, done, info = self.env.step(command)
        except:
            print(specified_command + ' is not a valid command.\n')
            return
        if command == 'down':
            self.nle_map = nle_map.nle_map(self)
            feature.features.clear()
            self.current_goal = None
            self.current_plan = None
        self.surroundings = obsv['text_glyphs'].split("\n") # Description of surroundings
        self.last_text_message: str = obsv['text_message'] # Immediate feedback, like "It's solid stone."
        self.update_stats(obsv['text_blstats'].split('\n')) # Description of stats, statuses, and progress
        self.inventory = obsv['text_inventory'].split('\n') # Description of each inventory item
        self.character_class = obsv['text_cursor'].split(' ')[-1] # Description of character class
        self.nle_map.update_position(command)
        self.nle_map.update_surroundings(self.surroundings, verbose=display)
        if display:
            self.env.render()
            print(self.nle_map)
            if not specified_command:
                print('Current coordinates: ' + str((self.x, self.y)))
                print('Current plan: ' + str(self.current_goal) + ' ' + str(self.current_plan))
                print('Decided action: ' + command)

        # After receiving message "You try to move the boulder, but in vain.", need to log that boulder as a confirmed "stuck boulder" feature that a
        #   boulder observation won't overwrite - treat it as impassable

    def interpret(self, text_glyph: str, verbose: bool = False) -> Dict:
        original_glyph = text_glyph
        if verbose:
            print('Interpreting observation: ' + text_glyph)
        superfluous_words = [',', '.']
        location_distances = {'adjacent': 1, 'verynear': 2, 'near': 3, 'far': 6, 'veryfar': 12}
        location_max_distances = {'adjacent': 1, 'verynear': 2, 'near': 5, 'far': 11, 'veryfar': 30}
        '''
        Observed boundaries:
            Adjacent: 1-1
            Very near: 2-2
            Near: 3-5
            Far: 6-?
            Very far: ?
        '''
        cardinal_directions = ['north', 'west', 'south', 'east']
        text_glyph = text_glyph.replace(' and ', ' ')
        text_glyph = misc_util.remove_multiple_substrings(text_glyph, superfluous_words).replace('very near', 'verynear').replace('very far', 'veryfar').split(' ')
        location_separated = False
        num_words = len(text_glyph)
        index = 0
        while index < num_words and not location_separated:
            current_word = text_glyph[index]
            if current_word in location_distances:
                glyph_subject = text_glyph[:index]
                glyph_location = text_glyph[index:]
                location_word = glyph_location.pop(0)
                min_glyph_distance = location_distances[location_word]
                # Should have a way to detect a previously found glyph of the same subject in the approximate location
                for location_index, current_copy in enumerate(glyph_location):
                    for cardinal_direction in cardinal_directions:
                        glyph_location[location_index] = glyph_location[location_index].replace(cardinal_direction, cardinal_direction + ' ')
                    glyph_location[location_index] = glyph_location[location_index].split(' ')
                    glyph_location[location_index].pop(-1)
                    angle = misc_util.cardinal_directions_to_angle(glyph_location[location_index])
                    if len(glyph_location[location_index]) <= 2: # Angles like north northeast are too imprecise to incorporate accurately
                        glyph_location[location_index] = set([])

                        for estimated_glyph_distance in range(min_glyph_distance, location_max_distances[location_word] + 1):
                            x_change = estimated_glyph_distance * math.cos(math.radians(angle))
                            if round(x_change, 2) < 0:
                                x_change = -1 * int(math.ceil(-1 * x_change))
                            elif round(x_change, 2) > 0:
                                x_change = int(math.ceil(x_change))
                            else:
                                x_change = int(round(x_change))

                            y_change = estimated_glyph_distance * math.sin(math.radians(angle))
                            if round(y_change, 2) < 0:
                                y_change = -1 * int(math.ceil(-1 * y_change))
                            elif round(y_change, 2) > 0:
                                y_change = int(math.ceil(y_change))
                            else:
                                y_change = int(round(y_change))
                            glyph_location[location_index].add((self.x + x_change, self.y + y_change))

                location_separated = True
            index += 1
        if glyph_subject == ['dark', 'area']: # When walking through a tunnel, any adjacent dark areas are always walls, while non-adjacent dark areas are inconsistent
            if min_glyph_distance == 1:
                glyph_subject = ['stone', 'wall']
            else:
                glyph_subject = ['current'] # Don't use far dark observations directly, but they help determine which guaranteed visible cells to modify
        if verbose:
            print('Encoding ' + str(glyph_subject) + ' about ' + str(min_glyph_distance) + ' away at the coordinates ' + str(glyph_location) +'\n')
        return({
            'subject': glyph_subject,
            'locations': glyph_location,
            'glyph': original_glyph
        })

    def is_combat_message(self, text_message: str):
        split_message = text_message.replace('!', '.').replace('. ', '.').replace('. ', '.').split('.')
        for current_message in split_message:
            for combat_start_message in ['You kill ', 'You hit ', 'You miss ', 'You destroy ', 'You cannot escape from ', 'You get zapped']:
                if current_message.startswith(combat_start_message):
                    return(True)
            for combat_end_message in [' is killed', ' hits', ' misses', ' bites', ' misses you']:
                if current_message.endswith(combat_end_message):
                    return(True)
        return(False)
# Account for messages like "The kobold zombie hits! The kitten drops a gold piece." - maybe replace ! and ? with . and split by .