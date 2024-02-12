from typing import List, Tuple

class cell():
    def __init__(self, coordinates):
        self.x, self.y = coordinates
        self.glyph: str = "."
        return
    
    def __str__(self):
        return(self.glyph)

class nle_map():
    def __init__(self, agent):
        self.agent = agent
        self.grid: List[List[cell]] = [[cell((0, 0))]]
        self.agent_coordinates: Tuple[int, int] = ((self.agent.x, self.agent.y))
        return

    def update_surroundings(self, text_glyphs: List[str]):
        print(text_glyphs)
        print('Update encoded map with the above text glyphs ^')
        return
    
    def __str__(self):
        return_str = ""
        for row in self.grid:
            return_str += '['
            for column in row:
                return_str += str(column)
                if column != row[-1]:
                    return_str += ', '
                return_str += ']\n'
        return(return_str)
