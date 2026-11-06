import encoder
import drawer
import pygame
import pygame.gfxdraw


# 2 Build spell matrix
reg = encoder.GlyphRegistry()
loded = encoder.spell_builder(reg)

# center=(600, 400), radius=200, angle_offset=-90, scale_factor=0.6
# WIDTH, HEIGHT = 1200, 800
drawer.draw_spell(loded, (1500, 1000), [(750, 500), 250, -90, 0.6])
