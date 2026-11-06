import pygame
import sys

from parser import parse_text
from traslator import LayoutWord
from drawer import Renderer


# --- CONFIG ---
WIDTH, HEIGHT = 800, 600
TEXT = "hello"
BACK_COLOR = (30, 30, 30)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gallifreyan Test")

    clock = pygame.time.Clock()

    renderer = Renderer()

    # --- INITIAL PARSE ---
    sentence = parse_text(TEXT)
    word_layouts = []

    # layout words horizontally for now
    spacing = WIDTH // (len(sentence.words) + 1)

    for i, word in enumerate(sentence.words):
        center = ((i + 1) * spacing, HEIGHT // 2)
        lw = LayoutWord(word, center)
        word_layouts.append(lw)

    # --- LOOP ---
    running = True
    while running:
        screen.fill(BACK_COLOR)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # draw all words
        for lw in word_layouts:
            renderer.draw_word(screen, lw)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()