
import pygame

from upgrades import UPGRADES


# --------------------------------------------------
# COLORS
# --------------------------------------------------

BACKGROUND = (24, 20, 30)
PANEL = (38, 32, 48)
PANEL_LIGHT = (50, 42, 62)

TEXT = (235, 225, 205)
TEXT_DIM = (160, 150, 135)

GOLD = (220, 170, 60)
SUCCESS = (100, 200, 120)
FAILURE = (210, 90, 90)


# --------------------------------------------------
# UI
# --------------------------------------------------

class UI:
    def __init__(self, screen):
        self.screen = screen

        self.font = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.font_vlarge =  pygame.font.Font(None, 70)
        self.font_huge = pygame.font.Font(None, 100)

        # Main screen button
        self.roll_button = pygame.Rect(350, 580, 300, 70)

        # Shop button
        self.shop_button = pygame.Rect(760, 590, 160, 50)

        # Shop state
        self.shop_open = False
        self.shop_scroll = 0

        # Shop layout
        self.shop_rect = pygame.Rect(120, 60, 760, 580)
        self.shop_close_button = pygame.Rect(820, 80, 40, 40)

        self.shop_list_rect = pygame.Rect(150, 140, 700, 460)
        
        # Rolling animation
        self.rolling = False
        self.roll_start_time = 0
        self.roll_duration = 300
        self.pending_result = None

    # --------------------------------------------------
    # BASIC DRAWING
    # --------------------------------------------------

    def text(
        self,
        value,
        x,
        y,
        font=None,
        color=TEXT,
        center=False,
    ):
        font = font or self.font
        surface = font.render(str(value), True, color)

        rect = surface.get_rect()

        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)

        self.screen.blit(surface, rect)

    def panel(self, rect, color=PANEL):
        pygame.draw.rect(
            self.screen,
            color,
            rect,
            border_radius=12,
        )

    # --------------------------------------------------
    # MAIN SCREEN
    # --------------------------------------------------

    def draw(self, state, result=None):
        self.screen.fill(BACKGROUND)

        self.draw_header()
        self.draw_challenge(state)
        self.draw_dice(result)
        self.draw_progress(state)
        self.draw_result(result)
        self.draw_bottom_bar(state)
        self.draw_roll_button()
        self.draw_shop_button()

        if self.shop_open:
            self.draw_shop(state)

    # --------------------------------------------------
    # MAIN SCREEN SECTIONS
    # --------------------------------------------------

    def draw_header(self):
        self.text(
            "DICE OF FATE",
            500,
            45,
            self.font_large,
            center=True,
        )

    def draw_challenge(self, state):
        self.text(
            state.challenge_name,
            500,
            100,
            self.font_large,
            GOLD,
            center=True,
        )

        self.text(
            f"Roll a {state.target} "
            f"{state.required_streak} times in a row",
            500,
            140,
            center=True,
        )

    def draw_dice(self, result):
        self.draw_d20((500, 285), 100)
        
        if self.rolling:
            value = pygame.time.get_ticks() // 40 % 20 + 1
        else:
            value = "?" if result is None else result.value

        self.text(
            value,
            500,
            285,
            self.font_vlarge if (value != 20 or self.rolling) else self.font_huge,
            center=True,
            color=(160, 150, 180) if (value != 20 or self.rolling) else (218, 164, 40),
        )
        
    def draw_d20(self, center, size):
        cx, cy = center

        # --------------------------------------------------
        # OUTER HEXAGON
        # --------------------------------------------------

        outer = [
            (cx, cy - size),                       # top
            (cx + size * 0.866, cy - size * 0.50),
            (cx + size * 0.866, cy + size * 0.50),
            (cx, cy + size),
            (cx - size * 0.866, cy + size * 0.50),
            (cx - size * 0.866, cy - size * 0.50),
        ]

        # --------------------------------------------------
        # CENTRAL EQUILATERAL TRIANGLE
        # --------------------------------------------------

        center_tri = [
            (cx, cy + size * 0.6),
            (cx + size * 0.6, cy - size * 0.43),
            (cx - size * 0.6, cy - size * 0.43),
        ]

        # --------------------------------------------------
        # FACET POINTS
        # --------------------------------------------------

        # Three points around the center triangle.
        # These create the three slightly squashed triangles.
        top_point = outer[0]

        right_point = outer[2]

        left_point = outer[4]

        # --------------------------------------------------
        # MAIN TRIANGLES
        # --------------------------------------------------
        
        # Top triangle
        pygame.draw.polygon(
            self.screen,
            (48, 40, 59),
            [
                center_tri[2],
                center_tri[1],
                top_point,
            ]
        )
        
        # Bottom-right triangle
        pygame.draw.polygon(
            self.screen,
            (53, 44, 63),
            [
                center_tri[1],
                center_tri[0],
                right_point,
            ]
        )

        # Bottom-left triangle
        pygame.draw.polygon(
            self.screen,
            (43, 36, 54),
            [
                center_tri[2],
                center_tri[0],
                left_point,
            ]
        )
        
        # --------------------------------------------------
        # OUTER TRIANGLES
        # --------------------------------------------------

        # Top-right
        pygame.draw.polygon(
            self.screen,
            (42, 35, 52),
            [
                center_tri[1],
                top_point,
                outer[1],
            ]
        )
        
        # Right
        pygame.draw.polygon(
            self.screen,
            (47, 39, 57),
            [
                center_tri[1],
                right_point,
                outer[1],
            ]
        )
        
        # Bottom-right
        pygame.draw.polygon(
            self.screen,
            (40, 33, 50),
            [
                center_tri[0],
                right_point,
                outer[3],
            ]
        )
        
        # Bottom-left
        pygame.draw.polygon(
            self.screen,
            (45, 37, 54),
            [
                center_tri[0],
                outer[3],
                left_point,
            ]
        )

        # Left
        pygame.draw.polygon(
            self.screen,
            (50, 41, 60),
            [
                center_tri[2],
                left_point,
                outer[5],
            ]
        )
        
        # Top-left
        pygame.draw.polygon(
            self.screen,
            (44, 36, 53),
            [
                center_tri[2],
                outer[5],
                top_point,
            ]
        )

        # --------------------------------------------------
        # CENTRAL TRIANGLE
        # --------------------------------------------------

        pygame.draw.polygon(
            self.screen,
            (62, 51, 74),
            center_tri
        )


        

    def draw_progress(self, state):
        self.text(
            f"STREAK  {state.streak} / {state.required_streak}",
            500,
            415,
            center=True,
        )

        bar = pygame.Rect(300, 445, 400, 20)

        pygame.draw.rect(
            self.screen,
            PANEL,
            bar,
            border_radius=10,
        )

        progress = min(
            state.streak / state.required_streak,
            1.0,
        )

        if progress > 0:
            fill = bar.copy()
            fill.width = int(bar.width * progress)

            pygame.draw.rect(
                self.screen,
                SUCCESS,
                fill,
                border_radius=10,
            )

    def draw_result(self, result):
        if result is None:
            return

        if result.critical_success:
            message = "NATURAL 20!"
            color = GOLD

        elif result.critical_failure:
            message = "NATURAL 1!"
            color = FAILURE

        elif result.success:
            message = "SUCCESS!"
            color = SUCCESS

        else:
            message = "FAILURE"
            color = FAILURE

        self.text(
            message,
            500,
            495,
            self.font_large,
            color,
            center=True,
        )

        self.text(
            f"+{result.reward} GOLD",
            500,
            535,
            self.font,
            GOLD,
            center=True,
        )

    def draw_bottom_bar(self, state):
        self.text(
            f"GOLD: {state.gold}",
            100,
            675,
            color=GOLD,
        )

        self.text(
            f"BEST: {state.best_streak}",
            400,
            675,
        )

        self.text(
            f"ROLLS: {state.total_rolls}",
            700,
            675,
        )

    def draw_roll_button(self):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.roll_button.collidepoint(mouse_pos)

        color = PANEL_LIGHT if hovered else PANEL

        pygame.draw.rect(
            self.screen,
            color,
            self.roll_button,
            border_radius=12,
        )

        self.text(
            "ROLL D20",
            self.roll_button.centerx,
            self.roll_button.centery,
            self.font_large,
            center=True,
        )

    def draw_shop_button(self):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.shop_button.collidepoint(mouse_pos)

        color = PANEL_LIGHT if hovered else PANEL

        pygame.draw.rect(
            self.screen,
            color,
            self.shop_button,
            border_radius=10,
        )

        self.text(
            "UPGRADES",
            self.shop_button.centerx,
            self.shop_button.centery,
            self.font,
            center=True,
        )
        
        
    # --------------------------------------------------
    # ROLL ANIMATION
    # --------------------------------------------------
    def start_roll_animation(self, result, roll_speed):
        self.rolling = True
        self.roll_start_time = pygame.time.get_ticks()
        self.roll_duration = int(300 / roll_speed)
        self.pending_result = result
        
    def update_roll_animation(self):
        if not self.rolling:
            return None

        elapsed = pygame.time.get_ticks() - self.roll_start_time

        if elapsed >= self.roll_duration:
            self.rolling = False
            result = self.pending_result
            self.pending_result = None
            return result

        return False

    # --------------------------------------------------
    # SHOP
    # --------------------------------------------------

    def draw_shop(self, state):
        # Dark overlay over the game
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        # Main shop panel
        self.panel(self.shop_rect, PANEL_LIGHT)

        self.text(
            "UPGRADES",
            165,
            95,
            self.font_large,
        )

        self.text(
            f"GOLD: {state.gold}",
            650,
            102,
            self.font,
            GOLD,
        )

        # Close button
        pygame.draw.rect(
            self.screen,
            PANEL,
            self.shop_close_button,
            border_radius=8,
        )

        self.text(
            "X",
            self.shop_close_button.centerx,
            self.shop_close_button.centery,
            self.font,
            center=True,
        )

        # Clip drawing to the scrollable area
        self.screen.set_clip(self.shop_list_rect)

        item_height = 100
        gap = 12

        y = (
            self.shop_list_rect.top
            - self.shop_scroll
        )

        for i, upgrade in enumerate(UPGRADES):
            rect = pygame.Rect(
                self.shop_list_rect.left + 10,
                y,
                self.shop_list_rect.width - 20,
                item_height,
            )

            self.draw_upgrade(
                state,
                upgrade,
                i,
                rect,
            )

            y += item_height + gap

        self.screen.set_clip(None)

        # Simple scrollbar
        self.draw_shop_scrollbar()

    def draw_upgrade(self, state, upgrade, index, rect):
        self.panel(rect, PANEL)

        # Upgrade name
        self.text(
            upgrade.name,
            rect.x + 20,
            rect.y + 15,
            self.font_large,
            color=TEXT_DIM if upgrade.purchased else TEXT,
        )

        # Description
        self.text(
            upgrade.description,
            rect.x + 20,
            rect.y + 53,
            self.font,
            color=TEXT_DIM,
        )

        # Buy button
        buy_rect = pygame.Rect(
            rect.right - 180,
            rect.y + 25,
            150,
            50,
        )

        if upgrade.purchased:
            button_color = PANEL_LIGHT
            button_text = "MAXED"
            text_color = TEXT_DIM

        elif state.gold >= upgrade.cost:
            button_color = GOLD
            button_text = f"BUY {upgrade.cost}G"
            text_color = BACKGROUND

        else:
            button_color = PANEL_LIGHT
            button_text = f"{upgrade.cost}G"
            text_color = TEXT_DIM

        pygame.draw.rect(
            self.screen,
            button_color,
            buy_rect,
            border_radius=8,
        )

        self.text(
            button_text,
            buy_rect.centerx,
            buy_rect.centery,
            self.font,
            text_color,
            center=True,
        )

    def draw_shop_scrollbar(self):
        total_height = len(UPGRADES) * 112

        if total_height <= self.shop_list_rect.height:
            return

        # Track
        track = pygame.Rect(
            self.shop_list_rect.right + 5,
            self.shop_list_rect.top,
            8,
            self.shop_list_rect.height,
        )

        pygame.draw.rect(
            self.screen,
            PANEL,
            track,
            border_radius=4,
        )

        # Thumb
        visible_ratio = (
            self.shop_list_rect.height
            / total_height
        )

        thumb_height = max(
            30,
            int(
                self.shop_list_rect.height
                * visible_ratio
            ),
        )

        max_scroll = self.get_max_scroll()

        if max_scroll > 0:
            thumb_y = (
                track.top
                + (
                    self.shop_scroll / max_scroll
                ) * (
                    track.height - thumb_height
                )
            )
        else:
            thumb_y = track.top

        thumb = pygame.Rect(
            track.x,
            int(thumb_y),
            track.width,
            thumb_height,
        )

        pygame.draw.rect(
            self.screen,
            TEXT_DIM,
            thumb,
            border_radius=4,
        )

    # --------------------------------------------------
    # INPUT
    # --------------------------------------------------

    def roll_clicked(self, position):
        return (
            not self.shop_open
            and self.roll_button.collidepoint(position)
        )

    def shop_clicked(self, position):
        return self.shop_button.collidepoint(position)

    def shop_close_clicked(self, position):
        return (
            self.shop_open
            and self.shop_close_button.collidepoint(position)
        )

    def upgrade_clicked(self, position):
        if not self.shop_open:
            return None

        # Only check clicks inside the scroll area
        if not self.shop_list_rect.collidepoint(position):
            return None

        item_height = 100
        gap = 12

        y = self.shop_list_rect.top - self.shop_scroll

        for i, upgrade in enumerate(UPGRADES):
            rect = pygame.Rect(
                self.shop_list_rect.left + 10,
                y,
                self.shop_list_rect.width - 20,
                item_height,
            )

            buy_rect = pygame.Rect(
                rect.right - 180,
                rect.y + 25,
                150,
                50,
            )

            if buy_rect.collidepoint(position):
                return i

            y += item_height + gap

        return None

    def scroll_shop(self, amount):
        if not self.shop_open:
            return

        self.shop_scroll -= amount * 40

        self.shop_scroll = max(
            0,
            min(
                self.shop_scroll,
                self.get_max_scroll(),
            ),
        )

    def get_max_scroll(self):
        total_height = len(UPGRADES) * 112

        return max(
            0,
            total_height - self.shop_list_rect.height,
        )
