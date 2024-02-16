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
        
    def update_stats(self, blstats: List[str]):
        for current_value in blstats:
            split_stat = current_value.split(": ")
            current_stat_name = split_stat[0].lower().replace(" ", "_")
            if current_stat_name in int_stats:
                self.stats[current_stat_name] = int(split_stat[-1])
            elif current_stat_name in scale_stats:
                self.stats[current_stat_name], self.stats["max_" + current_stat_name] = [int(x) for x in split_stat[-1].split('/')]
            elif current_stat_name in str_stats:
                self.stats[current_stat_name] = split_stat[-1]

    def act(self):
        obsv, reward, done, info = self.env.step("wait")
        self.surroundings = obsv["text_glyphs"].split("\n") # Description of surroundings
        self.nle_map.update_surroundings(self.surroundings)
        text_message: str = obsv["text_message"] # Seems to be empty
        self.update_stats(obsv["text_blstats"].split("\n")) # Description of stats, statuses, and progress
        self.inventory = obsv["text_inventory"].split("\n") # Description of each inventory item
        self.character_class = obsv["text_cursor"].split(" ")[-1] # Description of character class
        print(self.nle_map)

    def interpret(self, text_glyph: str, verbose: bool = False) -> Dict:
        original_glyph = text_glyph
        #if verbose:
        print('Interpreting observation: ' + text_glyph)
        superfluous_words = [',', '.', 'and ']
        location_distances = {'far': 6, 'verynear': 2, 'near': 4, 'adjacent': 1, 'veryfar': 12}
        '''
        Observed boundaries:
            Adjacent: 1-1
            Very near: 2-2
            Near: 3-5
            Far: 6-?
            Very far: ?
        '''
        cardinal_directions = ['north', 'west', 'south', 'east']
        text_glyph = misc_util.remove_multiple_substrings(text_glyph, superfluous_words).replace('very near', 'verynear').replace('very far', 'veryfar').split(' ')

        location_separated = False
        num_words = len(text_glyph)
        index = 0
        while index < num_words and not location_separated:
            current_word = text_glyph[index]
            if current_word in location_distances:
                glyph_subject = text_glyph[:index]
                glyph_location = text_glyph[index:]
                estimated_glyph_distance = location_distances[glyph_location.pop(0)]
                # Should have a way to detect a previously found glyph of the same subject in the approximate location
                for location_index, current_copy in enumerate(glyph_location):
                    for cardinal_direction in cardinal_directions:
                        glyph_location[location_index] = glyph_location[location_index].replace(cardinal_direction, cardinal_direction + ' ')
                    glyph_location[location_index] = glyph_location[location_index].split(' ')
                    glyph_location[location_index].pop(-1)
                    glyph_location[location_index] = misc_util.cardinal_directions_to_angle(glyph_location[location_index])

                    if verbose:
                        print(glyph_location[location_index]) # Prints vector angle

                    x_change = estimated_glyph_distance * math.cos(math.radians(glyph_location[location_index]))
                    if round(x_change, 2) < 0:
                        x_change = -1 * int(math.ceil(-1 * x_change))
                    elif round(x_change, 2) > 0:
                        x_change = int(math.ceil(x_change))
                    else:
                        x_change = int(round(x_change))

                    y_change = estimated_glyph_distance * math.sin(math.radians(glyph_location[location_index]))
                    if round(y_change, 2) < 0:
                        y_change = -1 * int(math.ceil(-1 * y_change))
                    elif round(y_change, 2) > 0:
                        y_change = int(math.ceil(y_change))
                    else:
                        y_change = int(round(y_change))

                    glyph_location[location_index] = (self.x + x_change, self.y + y_change)

                location_separated = True
            index += 1
        if verbose:
            print('Encoding ' + str(glyph_subject) + ' about ' + str(estimated_glyph_distance) + ' away at the coordinates ' + str(glyph_location) +'\n')
        return({
            'subject': glyph_subject,
            'locations': glyph_location,
            'glyph': original_glyph
        })

'''
observation_keys=(
    "glyphs",
    "chars",
    "colors",
    "specials",
    "blstats",
    "message",
    "inv_glyphs",
    "inv_strs",
    "inv_letters",
    "inv_oclasses",
    "screen_descriptions",
    "tty_chars",
    "tty_colors",
    "tty_cursor",
)

Commands:
    0 MiscAction.MORE
    1 CompassDirection.N
    2 CompassDirection.E
    3 CompassDirection.S
    4 CompassDirection.W
    5 CompassDirection.NE
    6 CompassDirection.SE
    7 CompassDirection.SW
    8 CompassDirection.NW
    9 CompassDirectionLonger.N
    10 CompassDirectionLonger.E
    11 CompassDirectionLonger.S
    12 CompassDirectionLonger.W
    13 CompassDirectionLonger.NE
    14 CompassDirectionLonger.SE
    15 CompassDirectionLonger.SW
    16 CompassDirectionLonger.NW
    17 MiscDirection.UP
    18 MiscDirection.DOWN
    19 MiscDirection.WAIT
    20 Command.KICK
    21 Command.EAT
    22 Command.SEARCH
'''