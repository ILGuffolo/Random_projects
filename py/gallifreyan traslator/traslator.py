import math

class LayoutUnit:
    def __init__(self, unit):
        self.unit = unit

        self.angle = 0
        self.pos = (0, 0)

        self.attached = False
        
    def __repr__(self):
        return "layout_unit: " + str(self.unit)


class LayoutWord:
    def __init__(self, word, center = (0, 0)):
        self.word = word

        self.center = (0, 0)
        self.radius = 0

        self.units = []  # LayoutUnit
        
        ### Build structure
        self.center = center
        self.radius = compute_word_radius(word)

        main_units = get_main_units(word)
        self.main_units = main_units
        angles = compute_angles(len(main_units))

        unit_map = {}

        # Place main units
        for unit, angle in zip(main_units, angles):
            lu = LayoutUnit(unit)
            lu.angle = angle
            lu.pos = polar_to_cartesian(center, self.radius, angle)

            self.units.append(lu)
            unit_map[unit] = lu

        # Place attached units (vowels)
        for unit in word.units:
            if unit.attached_to:
                parent_layout = unit_map[unit.attached_to]

                lu = LayoutUnit(unit)
                lu.angle = parent_layout.angle
                lu.pos = polar_to_cartesian(center, self.radius, parent_layout.angle)
                lu.attached = True

                self.units.append(lu)
        
    def __repr__(self):
        return "layout_" + str(self.word)
        
def compute_word_radius(word, base = 100, scale = 25):
    return base + len(word.units) * scale

def get_main_units(word):
    return [u for u in word.units if u.attached_to is None]

def compute_angles(n):
    step = (2 * math.pi) / n
    start = math.pi / 2

    return [start - i * step for i in range(n)]

def polar_to_cartesian(center, radius, angle):
    cx, cy = center
    x = cx + radius * math.cos(angle)
    y = cy + radius * math.sin(angle)
    return (x, y)


