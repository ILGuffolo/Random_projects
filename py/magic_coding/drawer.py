from typing import List, Optional, Tuple
import pygame
import math
import re
import threading

# --- 0 visual converter ---
class VisualNode:
    def __init__(self, glyph_name: str, parent: Optional['VisualNode']=None):
        self.glyph_name = glyph_name
        self.parent = parent
        self.children: List['VisualNode'] = []
        self.center: Tuple[float, float] = (0.0, 0.0)  # x, y in pixels
        self.radius: float = 1.0  # will scale later
        self.depth: int = 0
        self.meta: dict = {}  # for future modifiers, rotation, scale, etc.

        if parent:
            parent.children.append(self)

class VisualScene:
    def __init__(self):
        self.root: Optional[VisualNode] = None

    def build_from_tree(self, glyph_node):
        """
        Recursively build VisualNode tree from encoder GlyphNode.
        """
        def _build(node, parent=None, depth=0):
            v_node = VisualNode(node.name, parent)
            v_node.depth = depth
            for child in node.inputs:
                _build(child, v_node, depth + 1)
            return v_node

        self.root = _build(glyph_node)
        return self.root

    def layout_radial(self, center=(600, 400), radius=200, angle_offset=-90, scale_factor=0.6):
        """
        Recursively layout nodes in a radial fashion.
        """
        def _layout(node, cx, cy, r, angle_offset):
            node.center = (cx, cy)
            node.radius = r

            n_children = len(node.children)
            if n_children == 0:
                return

            child_radius = r * scale_factor
            for i, child in enumerate(node.children):
                angle = angle_offset + (360 / n_children) * i
                import math
                rad = math.radians(angle)
                x = cx + r * math.cos(rad)
                y = cy + r * math.sin(rad)
                _layout(child, x, y, child_radius, angle_offset)

        if self.root:
            _layout(self.root, center[0], center[1], radius, angle_offset)


# --- 1 Instruction Data Structures ---

class DrawInstruction:
    """
    Represents one primitive drawing instruction for a glyph.
    """
    def __init__(self, instr_type: str, params: List[float], color: Tuple[int,int,int]=None):
        self.instr_type = instr_type  # e.g., "circle", "line", "dot", "bezier"
        self.params = params          # list of floats or numbers depending on instr
        self.color = color            # if None, use glyph base color

class GlyphDrawDefinition:
    """
    Holds all drawing instructions for a glyph.
    """
    def __init__(self, name: str):
        self.name = name
        self.instructions: List[DrawInstruction] = []
        self.base_color: Tuple[int,int,int] = (255,255,255)  # default white

# --- 2 Registry ---

class GlyphDrawRegistry:
    """
    Loads glyph definitions from files and stores them.
    """
    def __init__(self, folder="glyphs"):
        self.folder = folder
        self._defs: Dict[str, GlyphDrawDefinition] = {}

    def load_all(self):
        import os
        for fname in os.listdir(self.folder):
            if fname.endswith(".txt"):
                path = os.path.join(self.folder, fname)
                self.load_file(path)

    def load_file(self, path):
        name = None
        current_def = None
        with open(path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # New glyph
                if line.startswith("[") and line.endswith("]"):
                    name = line[1:-1]
                    current_def = GlyphDrawDefinition(name)
                    self._defs[name] = current_def
                    in_shapes_block = False  # reset shapes mode
                    continue
                
                # Start of shapes block
                if line.startswith("shapes=") and current_def:
                    in_shapes_block = True
                    instr_lines = line[len("shapes="):].strip()
                    # Check if color is provided
                    if instr_lines.startswith("(") and instr_lines.endswith(")"):
                        color_str = instr_lines[1:-1]
                        current_def.base_color = tuple(map(int, color_str.split(',')))
                    in_shapes_block = True
                    continue
                        
                # Inside shapes block (multiple lines)
                if in_shapes_block and current_def:
                    #skips empty lines
                    if not line:
                        continue
                    # Check for inline color override
                    color = None
                    if '(' in line and ')' in line:
                        m = re.search(r'\((.*?)\)', line)
                        if m:
                            color_str = m.group(1)
                            color = tuple(map(int, color_str.split(',')))
                            line = line[:m.start()].strip()  # remove color from line
                    parts = line.strip().split(" ")
                    instr_type = parts[0].lower()
                    params = [float(part) for part in parts[1:]]
                    current_def.instructions.append(DrawInstruction(instr_type, params, color))

    def get(self, glyph_name):
        return self._defs.get(glyph_name)

# --- 3 Renderer ---

class GlyphRenderer:
    """
    Draws a VisualNode tree on a pygame surface.
    """
    def __init__(self, registry: GlyphDrawRegistry):
        self.registry = registry

    def draw_node(self, surface, node, parent_pos=None, backColor=(30, 30, 30)):
        """
        Draw a single node according to its glyph definition.
        node.center and node.radius define position and scale.
        """
        glyph_def = self.registry.get(node.glyph_name)
        if not glyph_def:
            print(f"Warning: glyph '{node.glyph_name}' not found")
            return

        cx, cy = node.center
        scale = node.radius
        
        # fill with background color to remove trasparency
        pygame.draw.circle(surface, backColor, node.center, node.radius)
        
        for instr in glyph_def.instructions:
            color = instr.color if instr.color else glyph_def.base_color #choose correct color
            
            if instr.instr_type == "circle":
                x, y, r, thickness = instr.params
                y = -y #adjust for screen render
                
                pygame.draw.circle(
                    surface,
                    color, 
                    (int(cx + x * scale), int(cy + y * scale)),
                    int(r * scale),
                    int(thickness)
                )
            elif instr.instr_type == "dot":
                x, y, r = instr.params
                y = -y #adjust for screen render
                
                pygame.draw.circle(surface, color, (int(cx + x * scale), int(cy + y * scale)), int(r * scale))
            elif instr.instr_type == "line":
                x1, y1, x2, y2 = instr.params
                y1 = -y1 #adjust for screen render
                y2 = -y2
                
                pygame.draw.line(surface, color, (int(cx + x1*scale), int(cy + y1*scale)), (int(cx + x2*scale), int(cy + y2*scale)), 1)
            elif instr.instr_type == "bezier":
                points = [(int(cx + instr.params[i]*scale), int(cy - instr.params[i+1]*scale))
                          for i in range(0, len(instr.params), 2)]
                
                pygame.gfxdraw.bezier(surface, points, 100, color)  # 100 is smoothness

        # recursively draw children
        for child in node.children:
            self.draw_node(surface, child)



def draw_spell(spell, screenDim = (1200, 800), rootData=[(600, 400), 200, -90, 0.6], title="Spell", backColor=(30, 30, 30)):
    # 1 Load glyphs
    registry = GlyphDrawRegistry(folder="glyphs")
    registry.load_all()

    renderer = GlyphRenderer(registry)

    # 2 Converting to visual tree
    scene = VisualScene()
    visRoot = scene.build_from_tree(spell)
    scene.layout_radial(rootData[0], rootData[1], rootData[2], rootData[3])

    # 3 Init Pygame
    pygame.init()
    screen = pygame.display.set_mode(screenDim)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    
    print("drawing succesfull")
    
    # 4 Render
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(backColor)  # background

        # Draw the spell
        if visRoot:
            renderer.draw_node(screen, visRoot, None, backColor)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
    
    


