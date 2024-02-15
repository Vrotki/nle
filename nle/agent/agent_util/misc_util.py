from typing import List

def remove_multiple_substrings(current_string: str, to_replace: List[str]) -> str:
    for current_substring in to_replace:
        current_string = current_string.replace(current_substring, '')
    return(current_string)

def cardinal_directions_to_angle(cardinal_directions: List[str]) -> int:
    cardinal_direction_angles = {'east': 0, 'north': 90, 'west': 180, 'south': 270}
    total_angle = 0
    increment = 90
    for index, current_direction in enumerate(cardinal_directions):
        if index == 0:
            total_angle = cardinal_direction_angles[current_direction]
        else:
            min_index = 0
            candidate_angles = [cardinal_direction_angles[current_direction], cardinal_direction_angles[current_direction] - 360, cardinal_direction_angles[current_direction] + 360]
            for attempted_index, angle in enumerate(candidate_angles):
                if abs(total_angle - candidate_angles[attempted_index]) < abs(total_angle - candidate_angles[min_index]):
                    min_index = attempted_index
            best_angle = candidate_angles[min_index]
            if best_angle > total_angle:
                total_angle += increment
            else:
                total_angle -= increment
        increment /= 2
    total_angle %= 360
    return(round(total_angle))