from typing import List, Set

equivalence = {
    'northeast room corner': 'horizontal wall',
    'northwest room corner': 'horizontal wall',
    'southwest room corner': 'horizontal wall',
    'southeast room corner': 'horizontal wall',
    'northeast corner': 'horizontal wall',
    'northwest corner': 'horizontal wall',
    'southwest corner': 'horizontal wall',
    'southeast corner': 'horizontal wall',
    'doorway': 'blank'
}

icons = {
    'horizontal wall': '-',
    'vertical wall': '|',
    'stone wall': '/',
    'horizontal closed door': '+',
    'vertical closed door': '+',
    'horizontal open door': '|',
    'vertical open door': '-',
    'blank': '.',
    'empty': ' ',
    'dark area': ' ',
    'agent': '@',
    'tame little dog': 'd',
    #'jackal': 'd',
    'gold piece': '$',
    'tame kitten': 'f',
    'tame pony': 'u',
    #'kobold': 'k',
    'fountain': '{',
    'grave': '|',
    'bars': '#',
    'bronze ring': '=',
    'lichen': 'F',
    'stairs up': '<',
    #'newt': ':',
    'invisible creature': 'I',
    'leather armor': '[',
    'hole': '^',
    #'kobold zombie': 'Z',
    #'sewer rat': 'r',
    'boulder': "'",
    'anti magic trap': '^',
    #'fox': 'd',
    'chest': ')',
    'stuck': 'X',
    #'grid bug': 'x',
    'stairs down': '>',
    #'goblin': 'o',
    #'hobbit': 'h'
}

passable = { #Assumed any object without an entry is passable - may update and log in runtime if discovered that move command failed due to impassable object
    'horizontal wall': False,
    'vertical wall': False,
    'horizontal closed door': True,
    'vertical closed door': True,
    'stone wall': False,
    'bars': False,
    'stuck': False
}

allows_diagonals = {
    'horizontal open door': False,
    'vertical open door': False
}

mobile = {
    'fox': True,
    'newt': True,
    'lichen': True,
    'tame little dog': True,
    'tame kitten': True,
    'tame pony': True,
    'jackal': True,
    'kobold': True,
    'kobold zombie': True,
    'sewer rat': True,
    'grid bug': True,
    'goblin': True,
    'invisible creature': True,
    'hobbit': True
}

#features = {}

class feature():
    def __init__(self, nle_map, subject_list: List, location_set: Set):
        self.nle_map = nle_map
        self.subject_list = subject_list
        self.location_set: Set
        self.predicted_location = None
        str_subject = ' '.join(self.subject_list)
        if str_subject in self.nle_map.features:
            self.nle_map.features[str_subject].append(self)
        else:
            self.nle_map.features[str_subject] = [self]
        self.set_location_set(location_set)

    def set_location_set(self, new_location_set: Set):
        self.location_set = new_location_set
        max_distance = -1
        max_location = None
        for location in new_location_set: # Always assume objects are as far away as possible until confirmed, encourages investigating over dead end
            distance = abs(location[0] - self.nle_map.agent_coordinates[0]) + abs(location[1] - self.nle_map.agent_coordinates[1])
            if max_distance < 0 or distance > max_distance:
                max_distance = distance
                max_location = location
        if self.predicted_location:
            self.nle_map.get_cell(self.predicted_location).incorporate(['empty'], confirmed=False)
        self.predicted_location = max_location
        self.nle_map.get_cell(self.predicted_location).incorporate(self.subject_list, confirmed=(len(new_location_set) == 1))
    
    def remove(self):
        if self.predicted_location:
            self.nle_map.get_cell(self.predicted_location).incorporate(['empty'], confirmed=False)
        self.nle_map.features[' '.join(self.subject_list)].remove(self)

def update_mobile_features(nle_map) -> None: # Accounts for any mobile feature to move by 1 each turn, expand possible locations
    for mobile_subject in mobile:
        for feature in nle_map.features.get(mobile_subject, []):
            new_locations = set()
            for location in feature.location_set:
                new_locations.add((location[0] + 1, location[1]))
                new_locations.add((location[0] - 1, location[1]))
                new_locations.add((location[0], location[1] + 1))
                new_locations.add((location[0], location[1] - 1))
                new_locations.add((location[0] + 1, location[1] + 1))
                new_locations.add((location[0] - 1, location[1] - 1))
                new_locations.add((location[0] - 1, location[1] + 1))
                new_locations.add((location[0] + 1, location[1] - 1))
            for new_location in new_locations:
                nle_map.create_cell(new_location)
            feature.location_set = new_locations.union(feature.location_set)

        preserved_features = []
        for feature in nle_map.features.get(mobile_subject, []):
            for other_feature in nle_map.features.get(mobile_subject, []): # If there have been 2 sightings 
                if feature != other_feature:
                    union = feature.location_set.union(other_feature.location_set)
                    if len(union) > 0:
                        feature.set_location_set(union)
                        other_feature.remove()
            length = len(feature.location_set)
            if length > 0 and length <= 100: # Forget any mobile features that haven't been seen in too long
                preserved_features.append(feature)
        nle_map.features[mobile_subject] = preserved_features

def find_overlap(nle_map, subject_list: List, location_set: Set) -> List:
    return_list = []
    subject = ' '.join(subject_list)
    for feature in nle_map.features.get(subject, []):
        intersection = location_set.intersection(feature.location_set)
        if bool(intersection):
            return_list.append((feature, intersection))
    return(return_list)

def print_features(nle_map) -> None:
    print('Printing amorphous features: ')
    for subject in nle_map.features:
        first = True
        for feature in nle_map.features[subject]:
            if len(feature.location_set) != 1: # Only bother printing if there is some level of unpredictability
                if first:
                    print(subject)
                    first = False
                print('    ' + str(feature.predicted_location) + '(' + str(feature.location_set) + ')')
