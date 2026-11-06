'''
all functions for visual display
(with pygame)
'''
import pygame
from game_runner import grid, p1, p2, EMPTY
from agents import MinimaxAgent
    
HUMAN = 0
MINIMAX = 1
    
def manual_play():
    pygame.init()

    WIDTH, HEIGHT = 300, 300
    CELL_SIZE = WIDTH // 3

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tic Tac Toe")

    game = grid()

    def draw_grid():
        for i in range(1, 3):
            pygame.draw.line(screen, (255,255,255), (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), 2)
            pygame.draw.line(screen, (255,255,255), (i*CELL_SIZE, 0), (i*CELL_SIZE, HEIGHT), 2)

    def draw_marks():
        for i, val in enumerate(game.state):
            x = (i % 3) * CELL_SIZE
            y = (i // 3) * CELL_SIZE

            if val == p1:
                pygame.draw.line(screen, (255,0,0), (x+20, y+20), (x+80, y+80), 3)
                pygame.draw.line(screen, (255,0,0), (x+80, y+20), (x+20, y+80), 3)
            elif val == p2:
                pygame.draw.circle(screen, (0,0,255), (x+50, y+50), 30, 3)
    
    def select_mode(screen):
        font = pygame.font.Font(None, 40)

        while True:
            screen.fill((30, 30, 30))

            text1 = font.render("Press 1: Human vs Human", True, (255, 255, 255))
            text2 = font.render("Press 2: Human vs AI", True, (255, 255, 255))

            screen.blit(text1, (30, 100))
            screen.blit(text2, (30, 160))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return (HUMAN, HUMAN)
                    if event.key == pygame.K_2:
                        return (HUMAN, MINIMAX)

    running = True
    
    ai = MinimaxAgent()

    player_X, player_O = select_mode(screen)

    while running:
        screen.fill((30,30,30))
        draw_grid()
        draw_marks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                col = mx // CELL_SIZE
                row = my // CELL_SIZE
                index = row * 3 + col

                game.move(index)

        pygame.display.flip()
        
        winner = game.check_winner()
        if winner is not None:
            print("Winner:", winner)
            pygame.time.delay(10)
            game.reset()

    pygame.quit()
