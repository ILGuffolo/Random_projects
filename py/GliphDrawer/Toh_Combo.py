import pygame, pygame.gfxdraw
import math
import random

### Helper functions ###

# Circle class
class Circle:
    def __init__(self, center, radius, parent = None, color=(0,0,0), Thickness = 5 ):
        self.center = center  # (x, y)
        self.radius = radius
        self.Thickness = Thickness
        self.id = len(GStack)
        self.filled = False
        self.parent = parent
        if color != (0,0,0) :
            self.color = color
        else:
            self.color = random_rgb()
        self.Children = []
        self.BaseColor = self.color
        self.shape = None
        
        if parent: parent.Children.append(self)
        GStack.append(self)


    def point_at_angle(self, angle_deg): #get pos on circle at angle
        cx, cy = self.center
        angle_rad = math.radians(angle_deg)
        x = cx + self.radius * math.cos(angle_rad)
        y = cy - self.radius * math.sin(angle_rad)  # minus so 90° = up
        return (x, y)
        
        
    def addChild(self, scale = 1, Bias = -90): # adds a circle child to this circle (used at runtime)
        number = len(self.Children) + 1
        if number <= 1: nu = 2
        else: nu = number
        
        Circle(self.point_at_angle(Bias), self.radius * scale / nu, self, self.color)
        
        for i in range(number):
            c = self.Children[i]
            c.center = self.point_at_angle(360 / number * i + Bias)
            c.radius = self.radius * scale / nu
            c.updatePos()
            if c.filled: # move dependent gliphs
                c.shape.center = c.center
                c.shape.radius = (c.radius - c.Thickness) * 0.9
        
        if self.filled: # move dependent gliphs
                self.shape.center = self.center
                self.shape.radius = (self.radius - self.Thickness) * 0.9
    
    def updatePos(self, scale = 1, Bias = -90):
        if len(self.Children) > 0:
            number = len(self.Children)
            if number <= 1: nu = 2
            else: nu = number
            
            for i in range(number):
                c = self.Children[i]
                c.center = self.point_at_angle(360 / number * i + Bias)
                c.radius = self.radius * scale / nu
                c.updatePos()
                if c.filled: # move dependent gliphs
                    c.shape.center = c.center
                    c.shape.radius = (c.radius - c.Thickness) * 0.9
            
            if self.filled: # move dependent gliphs
                self.shape.center = self.center
                self.shape.radius = (self.radius - self.Thickness) * 0.9
    
    
    def DrawSubCircles(self, number, scale = 1, Bias = -90): #draws n subcircles on the cirlce circunference (used at start)
        if number <= 1: nu = 2
        else: nu = number
        for i in range(number):
            c = Circle(self.point_at_angle(360 / number * i + Bias), self.radius * scale / nu, self)
            DStack.append(c)



# any shape has this class
class Shape: 
    def __init__(self, center, radius, Type, color=(0,0,0), Thickness=1):
        self.center = center  
        self.radius = radius
        self.color = color
        self.Thickness = Thickness
        self.type = Type
        
        
    def Draw_shape(self):
        #Drawing the shape by type
        if self.type == "f":
            self.draw_fire()
            
        elif self.type == "l":
            self.draw_Light()
        
        elif self.type == "i":
            self.draw_Ice()
        
        elif self.type == "p":
            self.draw_Plant()
        
        else:
            print("error wrong type entered")
        return
        
        
    #Fire Gliph
    def draw_fire(self):
        cx, cy = self.center
        R = self.radius
        self.color = (255, 0, 0)

        #Drawing
        r1 = R / 2
        r2 = R * 3/10
        pygame.draw.circle(screen, self.color, (cx, cy), R, width=3)               # Outer circle
        pygame.draw.circle(screen, self.color, (cx, cy + r1), r1, width=1)         # Big circle
        pygame.draw.circle(screen, self.color, (cx, cy - r2), r2, width=1)         # Small circle
        pygame.draw.circle(screen, self.color, (cx, cy + r1), R / 30)              # Dot
        
        pygame.gfxdraw.bezier(screen,[(cx +r1, cy +r1), (cx +r1, cy -r2), (cx, cy - 2*r2)] , 100, self.color)  #LR1
        pygame.gfxdraw.bezier(screen,[(cx +r2, cy -r2), (cx +r2, cy -2*r2), (cx, cy - R)] , 100, self.color)   #LR2
        pygame.gfxdraw.bezier(screen,[(cx -r1, cy +r1), (cx -r1, cy -r2), (cx, cy - 2*r2)] , 100, self.color)  #LL1
        pygame.gfxdraw.bezier(screen,[(cx -r2, cy -r2), (cx -r2, cy -2*r2), (cx, cy - R)] , 100, self.color)   #LL2
        
    
    #Light Gliph
    def draw_Light(self):
        cx, cy = self.center
        R = self.radius
        self.color = (255, 255, 0)
        
        #Drawing
        D = R / 6
        r1 = R / 6
        d2 = 0.94 * R
        dd = 0.1 * R
        pygame.draw.circle(screen, self.color, (cx, cy), R, width=3)                        # Outer circle
        pygame.draw.circle(screen, self.color, (cx, cy -R/2), r1, width=1)                  # Small Circle
        
        pygame.draw.line(screen, self.color, (cx, cy +R), (cx, cy -D*2), 1)                 # L1 (vertical)
        pygame.draw.line(screen, self.color, (cx -d2, cy +D*2), (cx +d2, cy +D*2), 1)       # L2 (orizontal)
        pygame.draw.line(screen, self.color, (cx +d2, cy +D*2), (cx, cy -D*2), 1)           # L3 (R big side)
        pygame.draw.line(screen, self.color, (cx -d2, cy +D*2), (cx, cy -D*2), 1)           # L4 (L big side)
        pygame.draw.line(screen, self.color, (cx +r1, cy -R/2-dd/3), (cx, cy -R), 1)        # L5 (R small side)
        pygame.draw.line(screen, self.color, (cx -r1, cy -R/2-dd/3), (cx, cy -R), 1)        # L6 (L small side)
        
        pygame.draw.line(screen, self.color, (cx -dd, cy +dd/2), (cx +dd, cy -dd/2), 1)     # D1
        pygame.draw.line(screen, self.color, (cx -dd, cy +dd*1.5), (cx +dd, cy +dd/2), 1)   # D2
        
    
    #Ice Gliph
    def draw_Ice(self):
        cx, cy = self.center
        R = self.radius
        self.color = (100, 200, 255)
        
        #Drawing
        dq = 0.15 * R
        d1 = 0.94 * R
        db = 0.99 * R
        dp = 0.05 * R
        pygame.draw.circle(screen, self.color, (cx, cy), R, width=3)                        # Outer circle
        
        pygame.draw.line(screen, self.color, (cx -d1, cy +R/3), (cx +d1, cy +R/3), 1)       # L1
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx, cy -R), 1)                 # L2
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx +R/4, cy -R*2/3), 1)        # L3
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx -R/4, cy -R*2/3), 1)        # L4
        pygame.draw.line(screen, self.color, (cx +R/4, cy -R*2/3), (cx, cy -R), 1)          # L5
        pygame.draw.line(screen, self.color, (cx -R/4, cy -R*2/3), (cx, cy -R), 1)          # L6
        
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx +dq, cy +R/3+dq), 1)        # Q1
        pygame.draw.line(screen, self.color, (cx +dq, cy +R/3+dq), (cx, cy +R/3+2*dq), 1)   # Q2
        pygame.draw.line(screen, self.color, (cx, cy +R/3+2*dq), (cx -dq, cy +R/3+dq), 1)   # Q3
        pygame.draw.line(screen, self.color, (cx -dq, cy +R/3+dq), (cx, cy +R/3), 1)        # Q4
        
        pygame.gfxdraw.bezier(screen,[(cx -db, cy +R/12), (cx -dp, cy -dp), (cx +dp, cy -dp), (cx +db, cy +R/12)] , 100, self.color) # Curva
        
        
    #Plant Gliph
    def draw_Plant(self):
        cx, cy = self.center
        R = self.radius
        self.color = (0, 255, 0)
        
        #Drawing
        dr = 0.2 * R
        r1 = R / 3 - dr/2
        da = 0.2 * R
        A  = 2 * R / 9 - da / 3
        da7 = 0.69
        pygame.draw.circle(screen, self.color, (cx, cy), R, width=3)                             # Outer circle
        pygame.draw.circle(screen, self.color, (cx, cy +R/3+r1), r1, width=1)                    # Root circle
        pygame.draw.circle(screen, self.color, (cx, cy +R/3+r1), R/30)                           # Dot
        
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx, cy -R/3), 1)                    # L1
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx +R/3, cy), 1)                    # L2
        pygame.draw.line(screen, self.color, (cx, cy +R/3), (cx -R/3, cy), 1)                    # L3
        pygame.draw.line(screen, self.color, (cx, cy -R/3), (cx -2*A, cy -R+da), 1)              # L4
        pygame.draw.line(screen, self.color, (cx, cy -R/3), (cx +2*A, cy -R+da), 1)              # L5
        pygame.draw.line(screen, self.color, (cx -2*A, cy -R+da), (cx +2*A, cy -R+da), 1)        # L6
        pygame.draw.line(screen, self.color, (cx -A*da7, cy -R/3-A), (cx +A*da7, cy -R/3-A), 1)  # L7
        
# draws the circle
def DrawCircle (C):
    pygame.draw.circle(screen, C.color, C.center, C.radius, C.Thickness)
    pygame.draw.circle(screen, BackColor, C.center, C.radius - C.Thickness)
    return

# draws sets of circles by using his building code
def DrawSet (SetCode, Root = 0) :
    # code dechypher
    if ":" in SetCode:
        parts = SetCode.split(":")            # split code
        RootID = int(parts[0])                # convert first part to number
        Code = list(parts[1])                 # converts string to list of characters
    else :
        RootID = Root
        Code = list(SetCode)
        
    # circle drawer
    DStack.clear()                  # clear stack for safety
    DStack.append(GStack[RootID])   # starts with
    for n in Code:                  # cycle for evey digit
        if len(DStack) == 0:        # check for invalid temporary root
            print("error, Code invalid")
            break
        
        r = DStack.pop(0)            # FIFO stack
        if n.isdigit():
            r.DrawSubCircles(int(n)) # Draw subcircle
            
        elif n.isalpha():
            s = Shape(r.center, (r.radius - r.Thickness) * 0.9 , n)
            r.filled = True
            r.shape = s
            SStack.append(s)
            
    DStack.clear()                  # Clear for safety
    
    return

def GlobalDrawer():
    for i in GStack:
        DrawCircle(i)
    for j in SStack:
        j.Draw_shape()
    for k in RStack:
        k.Draw_shape()
    
    return

def random_rgb():
    channels = [
        random.randint(200, 255),  # high
        random.randint(50, 150),   # medium
        random.randint(0, 50)      # low
        ]
    random.shuffle(channels)  # randomize channel order
    return channels

# nearest object (Must have .center propiety)
def nearest_object(cursor, objects, max_range = math.inf):
    closest = min(objects, key=lambda obj: math.dist(cursor, obj.center), default=None)
    if closest and math.dist(cursor, closest.center) <= max_range:
        return closest
    return None

### Global Parameters ###

GStack = [] #Global stack
DStack = [] #Drawing Stack
SStack = [] #Shape Stack
RStack = [] #Reference stack (flip)

# Main circle properties
circle_pos = (600, 400)  # (x, y)
circle_radius = 250
circle_color = (0, 200, 255)  # RGB
Thikness = 5 #percentage

C0 = Circle(circle_pos, circle_radius, None, circle_color, Thikness)

# References

RStack.append(Shape((100, 100), 50, "f"))
RStack.append(Shape((100, 300), 50, "l"))
RStack.append(Shape((100, 500), 50, "i"))
RStack.append(Shape((100, 700), 50, "p"))

### Window setup ###

# Initialize pygame
pygame.init()

# Window size
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Circle")
clock = pygame.time.Clock()

#Parameters
BackColor = (30, 30, 30)
GlowColor = (255, 255, 255)

MouseShape = None
SelectRadious = 100
MPressed = False
nearCircle = GStack[0]

#setup
#  DrawSet(input("inster your Code here: "))


### Main ###


# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # get mouse pos
    mx, my = pygame.mouse.get_pos()
    curPos = (mx, my)
    
    # check mouse button press
    # left mouse button pressed
    if not MPressed and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
        MPressed = True 
        if MouseShape != None: # if has shape, place it
            c =  nearest_object(curPos, GStack, 200)
            if c and not c.filled and len(c.Children) == 0:
                s = Shape(c.center, (c.radius - c.Thickness) * 0.9, MouseShape.type)
                c.filled = True
                c.shape = s
                SStack.append(s)
                MouseShape = None
            
        else: # if not, get it
            temps =  nearest_object(curPos, RStack)
            if temps:
                MouseShape = Shape(curPos, 50, temps.type)
    
    #wait untill release to check again
    if event.type == pygame.MOUSEBUTTONUP and (event.button == 1 or event.button == 3):
        MPressed = False
        
        
    # Right mouse button pressed
    if not MPressed and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: 
        MPressed = True
        c = nearest_object(curPos, GStack)
        if c and not c.filled:
            c.color = c.BaseColor
            c.addChild()
            
    # Glow nearest circle
    Cnew = nearest_object(curPos, GStack)
    if Cnew.id != nearCircle.id:
        nearCircle.color = nearCircle.BaseColor
        Cnew.color = GlowColor
    nearCircle = Cnew
    
        
        
    # clearscreen
    screen.fill(BackColor)  # dark gray background

    # Draw Phase
    GlobalDrawer()
    
    # drawing Dragged shape
    if MouseShape != None:
        MouseShape.center = (mx, my)
        MouseShape.Draw_shape()
    

    # Update screen
    pygame.display.flip()
    clock.tick(60)

# Quit pygame
pygame.quit()
