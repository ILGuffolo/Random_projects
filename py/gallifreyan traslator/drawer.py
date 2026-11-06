import pygame
import math

BACK_COLOR = (30, 30, 30)

class shape:
    def __init__(self, shape_type, radiusFactor = 1, offset = 0):
        
        self.shape_type = shape_type
        self.radiusFactor = radiusFactor
        self.offset = offset
        
    def draw(self, surface, layout_unit, radius, layout_word, width = 2, color = (255, 255, 255)):
        
        position = layout_unit.pos
        angle = layout_unit.angle
        
        if self.shape_type == "inner":
            newPos = (position[0] + self.offset, position[1] + self.offset)
            pygame.draw.circle(surface, color, newPos, radius * self.radiusFactor, width)
            
        elif self.shape_type == "full":
            pygame.draw.circle(surface, color, position, radius * self.radiusFactor, width)
        
        elif self.shape_type == "ark":
            pygame.draw.circle(surface, BACK_COLOR, position, radius * self.radiusFactor) # erase
            
            rect_box = pygame.Rect(position[0] - radius, position[1] - radius, 2*radius, 2*radius)
            theta = math.acos(self.offset / layout_word.radius)
            angle_start = angle + theta
            angle_end = angle - theta
            
            pygame.draw.arc(surface, color, rect_box, angle_start, angle_end)
        
        elif self.shape_type == "omega":
            newPos = (position[0], position[1])
            pygame.draw.circle(surface, BACK_COLOR, newPos, radius * self.radiusFactor) # erase
            
            rect_box = pygame.Rect(position[0] - radius, position[1] - radius, 2*radius, 2*radius)
            theta = math.acos(self.offset / layout_word.radius)
            angle_start = angle - theta
            angle_end = angle + theta
            
            pygame.draw.arc(surface, color, rect_box, angle_start, angle_end)
        
        else: print(f"unable to draw shape: {self}")
    
    
    def __repr__(self):
        return f"shape({self.shape_type})"


SHAPE_INNER = shape("inner", radiusFactor=0.8, offset=1)
SHAPE_FULL = shape("full")
SHAPE_ARC = shape("ark")
SHAPE_OMEGA = shape("omega", offset=0.5)
    

SHAPE_MAP = { # Mapping of token-shape (type, dots, lines)
    "B": (SHAPE_OMEGA, 0, 0),
    " ": (SHAPE_OMEGA, 1, 0),
    "CH": (SHAPE_OMEGA, 2, 0),
    "D": (SHAPE_OMEGA, 3, 0),
    "ND": (SHAPE_OMEGA, 4, 0),
    "G": (SHAPE_OMEGA, 0, 1),
    "H": (SHAPE_OMEGA, 0, 2),
    "F": (SHAPE_OMEGA, 0, 3),
    
    "J": (SHAPE_INNER, 0, 0),
    "PH": (SHAPE_INNER, 1, 0),
    "BK": (SHAPE_INNER, 2, 0),
    "L": (SHAPE_INNER, 3, 0),
    "C": (SHAPE_INNER, 4, 0),
    "N": (SHAPE_INNER, 0, 1),
    "P": (SHAPE_INNER, 0, 2),
    "M": (SHAPE_INNER, 0, 3),
    
    "T": (SHAPE_ARC, 0, 0),
    "WH": (SHAPE_ARC, 1, 0),
    "SH": (SHAPE_ARC, 2, 0),
    "R": (SHAPE_ARC, 3, 0),
    "NT": (SHAPE_ARC, 4, 0),
    "V": (SHAPE_ARC, 0, 1),
    "W": (SHAPE_ARC, 0, 2),
    "S": (SHAPE_ARC, 0, 3),
    
    "TH": (SHAPE_FULL, 0, 0),
    "GH": (SHAPE_FULL, 1, 0),
    "Y": (SHAPE_FULL, 2, 0),
    "Z": (SHAPE_FULL, 3, 0),
    "Q": (SHAPE_FULL, 4, 0),
    "QU": (SHAPE_FULL, 0, 1),
    "X": (SHAPE_FULL, 0, 2),
    "NG": (SHAPE_FULL, 0, 3),
}

class Renderer:
    def __init__(self):
        self.consonant_drawers = {}
        self.vowel_drawers = {}

    def draw_word(self, surface, layout_word, color = (255, 255, 255)):
        # draw word circle
        pygame.draw.circle(
            surface,
            color,
            (int(layout_word.center[0]), int(layout_word.center[1])),
            int(layout_word.radius),
            2
        )

        for lu in layout_word.units:
            if lu.unit.unit_type == "consonant":
                self.draw_consonant(surface, lu, layout_word)
            elif lu.unit.unit_type == "vowel":
                self.draw_vowel(surface, lu, layout_word)
                


    def draw_consonant(self, surface, lu, layout_word, color = (255, 255, 255)):
        letter = lu.unit.text

        shape, dots, lines = SHAPE_MAP.get(letter.upper(), (SHAPE_FULL, 0, 0))

        r = 2 * layout_word.radius / len(layout_word.main_units)
        shape.draw(surface, lu, r, layout_word, color= color)
        #TO DO modifiers

    def draw_vowel(self, surface, lu, layout_word, color = (255, 255, 255)):
        x, y = lu.pos

        r = 0.1 * layout_word.radius

        pygame.draw.circle(
            surface,
            color,
            (int(x), int(y)),
            r,
            2
        )
