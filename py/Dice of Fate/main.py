import pygame

from game import GameState, RollHandler
from ui import UI


WIDTH = 1000
HEIGHT = 700
FPS = 60


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dice of Fate")

    clock = pygame.time.Clock()

    state = GameState()
    handler = RollHandler(state)
    ui = UI(screen)

    result = None
    running = True

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                position = event.pos

                # Shop is open
                if ui.shop_open:

                    if ui.shop_close_clicked(position):
                        ui.shop_open = False

                    else:
                        upgrade_index = ui.upgrade_clicked(position)

                        if upgrade_index is not None:
                            handler.buy_upgrade(upgrade_index)

                # Main game
                else:
                    if ui.roll_clicked(position) and not ui.rolling:
                        roll_result = handler.roll()
                        ui.start_roll_animation(
                            roll_result,
                            state.roll_speed
                        )

                    elif ui.shop_clicked(position):
                        ui.shop_open = True

            elif event.type == pygame.MOUSEWHEEL:
                ui.scroll_shop(event.y)

        # Every frame
        animation_result = ui.update_roll_animation()

        if animation_result is not None and animation_result is not False:
            result = animation_result
        
        
        #draw screen
        ui.draw(state, result)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()