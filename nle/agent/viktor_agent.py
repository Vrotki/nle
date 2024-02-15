import random
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

    def interpret(self, text_glyph: str):
        '''
        Need to separate glyph subject words and glyph location words
        Location words always appear last and include cardinal directions
        '''
        print('Interpreting: ' + text_glyph)
        superfluous_words = [',', '.', 'and ']
        location_distances = {'far': 7, 'very near': 2, 'near': 4, 'adjacent': 1, 'very far': 20}
        cardinal_directions = ['north', 'west', 'south', 'east']
        text_glyph = misc_util.remove_multiple_substrings(text_glyph, superfluous_words).split(' ')

        location_separated = False
        num_words = len(text_glyph)
        index = 0
        while index < num_words and not location_separated:
            current_word = text_glyph[index]
            if current_word in location_distances: # Note - very near not being interpreted correctly, giving same distance as near
                glyph_subject = text_glyph[:index]
                glyph_location = text_glyph[index:]
                estimated_glyph_distance = location_distances[glyph_location.pop(0)]
                print(estimated_glyph_distance)
                # Should have a way to detect a previously found glyph of the same subject in the approximate location
                for location_index, current_copy in enumerate(glyph_location):
                    for cardinal_direction in cardinal_directions:
                        glyph_location[location_index] = glyph_location[location_index].replace(cardinal_direction, cardinal_direction + ' ')
                    glyph_location[location_index] = glyph_location[location_index].split(' ')
                    glyph_location[location_index].pop(-1)
                    glyph_location[location_index] = misc_util.cardinal_directions_to_angle(glyph_location[location_index])
                print(glyph_location)
            index += 1

        return('none')

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