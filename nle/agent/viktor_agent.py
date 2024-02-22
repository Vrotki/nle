import random
import math
from typing import Dict, List
from nle.env import NLE
from nle.agent.agent_util.nle_map import nle_map
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
        self.nle_map: nle_map = nle_map(self)
        self.stats: Dict = {}
        self.inventory: List[str] = []
        self.character_class: str = None
        self.last_text_message: str = None
        
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

    def think(self):
        return('wait')

    def act(self, specified_command = None):
        if specified_command:
            command = movement_mappings.get(specified_command, specified_command)
        else:
            command = self.think() #"wait"
        try:
            obsv, reward, done, info = self.env.step(command)
        except:
            print(specified_command + ' is not a valid command.\n')
            return
        self.surroundings = obsv['text_glyphs'].split("\n") # Description of surroundings
        self.last_text_message: str = obsv['text_message'] # Immediate feedback, like "It's solid stone."
        self.update_stats(obsv['text_blstats'].split('\n')) # Description of stats, statuses, and progress
        self.inventory = obsv['text_inventory'].split('\n') # Description of each inventory item
        self.character_class = obsv['text_cursor'].split(' ')[-1] # Description of character class
        self.nle_map.update_position(command)
        self.nle_map.update_surroundings(self.surroundings)

    def interpret(self, text_glyph: str, verbose: bool = False) -> Dict:
        original_glyph = text_glyph
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
        if verbose:
            print(text_glyph)
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
                    if verbose:
                        print(angle)
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

        print('Encoding ' + str(glyph_subject) + ' about ' + str(min_glyph_distance) + ' away at the coordinates ' + str(glyph_location) +'\n')
        return({
            'subject': glyph_subject,
            'locations': glyph_location,
            'glyph': original_glyph
        })
