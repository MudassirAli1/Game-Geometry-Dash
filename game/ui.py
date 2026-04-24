import pygame
import random
from .settings import *


class Button:
    """A clickable button with high-reliability hitboxes for PC and Mobile."""

    def __init__(self, x, y, width, height, text, color=NEON_BLUE, hover_color=NEON_PINK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont("Arial", FONT_SIZE_MEDIUM, bold=True)

    def handle_event(self, event):
        """Check if button was clicked using global mouse state for PC reliability."""
        # Update hover state for PC using logical coordinates (works perfectly with SCALED)
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        
        elif event.type == pygame.FINGERDOWN:
            # Native Touch registration for mobile (bypass mouse emulation)
            touch_pos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
            if self.rect.collidepoint(touch_pos):
                return True
        return False

    def draw(self, screen):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, DARK_BG, self.rect)
        pygame.draw.rect(screen, color, self.rect, 3)

        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ParticleSystem:
    """Creates spark effects for jumps, deaths, and trails."""

    def __init__(self):
        self.particles = []

    def emit_jump_particles(self, x, y, color):
        for _ in range(8):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-200, -50),
                'life': 1.0,
                'color': color,
                'size': random.uniform(2, 5)
            })

    def emit_death_particles(self, x, y, color):
        for _ in range(25):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 400)
            import math
            self.particles.append({
                'x': x, 'y': y,
                'vx': speed * math.cos(math.radians(angle)),
                'vy': speed * math.sin(math.radians(angle)),
                'life': 1.0,
                'color': color,
                'size': random.uniform(3, 8)
            })

    def emit_trail_particles(self, x, y, color):
        if random.random() < 0.2:
            self.particles.append({
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vx': random.uniform(-30, -10),
                'vy': random.uniform(-20, 20),
                'life': 0.5,
                'color': color,
                'size': random.uniform(2, 4)
            })

    def update(self, dt):
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 2
            particle['size'] *= 0.98
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen, camera_x):
        for particle in self.particles:
            screen_x = int(particle['x'] - camera_x)
            size = int(particle['size'])
            if size > 0:
                pygame.draw.circle(screen, particle['color'], (screen_x, int(particle['y'])), size)


class ParallaxBackground:
    """The scrolling background with stars."""

    def __init__(self):
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT - 150),
                'size': random.randint(1, 2),
                'speed': random.uniform(0.05, 0.15),
            })
        self.background_color = DARK_BG

    def update(self, dt, camera_x):
        pass

    def draw(self, screen, camera_x):
        screen.fill(self.background_color)
        for star in self.stars:
            screen_x = int((star['x'] - camera_x * star['speed']) % SCREEN_WIDTH)
            pygame.draw.circle(screen, (150, 150, 200), (screen_x, star['y']), star['size'])


class UIManager:
    """Handles all screens and buttons."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont("Arial", FONT_SIZE_LARGE, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", FONT_SIZE_MEDIUM, bold=True)
        self.font_small = pygame.font.SysFont("Arial", FONT_SIZE_SMALL)
        self.particles = ParticleSystem()
        self.background = ParallaxBackground()

        center_x = screen_width // 2

        # Main menu buttons
        self.menu_buttons = [
            Button(center_x - BUTTON_WIDTH//2, 300, BUTTON_WIDTH, BUTTON_HEIGHT, "START GAME"),
            Button(center_x - BUTTON_WIDTH//2, 380, BUTTON_WIDTH, BUTTON_HEIGHT, "SETTINGS"),
            Button(center_x - BUTTON_WIDTH//2, 460, BUTTON_WIDTH, BUTTON_HEIGHT, "EXIT"),
        ]

        # Pause buttons
        self.pause_buttons = [
            Button(center_x - BUTTON_WIDTH//2, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "RESUME"),
            Button(center_x - BUTTON_WIDTH//2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "RESTART"),
            Button(center_x - BUTTON_WIDTH//2, 450, BUTTON_WIDTH, BUTTON_HEIGHT, "MAIN MENU"),
        ]

        # Game over buttons
        self.game_over_buttons = [
            Button(center_x - BUTTON_WIDTH//2, 400, BUTTON_WIDTH, BUTTON_HEIGHT, "RETRY"),
            Button(center_x - BUTTON_WIDTH//2, 480, BUTTON_WIDTH, BUTTON_HEIGHT, "MAIN MENU"),
        ]

        # Settings buttons
        self.settings_buttons = [
            Button(center_x - BUTTON_WIDTH//2, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "CHANGE SKIN"),
            Button(center_x - BUTTON_WIDTH//2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "BACK"),
        ]

    def handle_event(self, event, buttons=None):
        if buttons is None: return None
        for button in buttons:
            if button.handle_event(event):
                return button.text
        return None

    def draw_hud(self, screen, progress, score, best_score):
        bar_width, bar_height = 400, 20
        bar_x, bar_y = (self.screen_width - bar_width) // 2, 20
        pygame.draw.rect(screen, (50, 50, 80), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, NEON_GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        screen.blit(self.font_small.render(f"Score: {score}", True, NEON_BLUE), (20, 20))
        screen.blit(self.font_small.render(f"Best: {best_score}", True, NEON_YELLOW), (20, 50))

    def draw_menu(self, screen):
        title_surf = self.font_large.render("NEON DASH", True, NEON_BLUE)
        screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width()//2, 150))
        for button in self.menu_buttons:
            button.draw(screen)

    def draw_pause_menu(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        for button in self.pause_buttons:
            button.draw(screen)

    def draw_game_over(self, screen, score, best_score, won=False):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        title_text = "LEVEL COMPLETE!" if won else "GAME OVER"
        title_color = NEON_GREEN if won else NEON_RED
        title_surf = self.font_large.render(title_text, True, title_color)
        screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width()//2, 150))
        for button in self.game_over_buttons:
            button.draw(screen)

    def draw_settings(self, screen, current_skin):
        title_surf = self.font_large.render("SETTINGS", True, NEON_BLUE)
        screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width()//2, 100))
        
        # Skin preview
        skin_color = PLAYER_SKINS[current_skin]
        preview_rect = pygame.Rect(self.screen_width // 2 - 30, 180, 60, 60)
        pygame.draw.rect(screen, skin_color, preview_rect)
        pygame.draw.rect(screen, WHITE, preview_rect, 3)

        for button in self.settings_buttons:
            button.draw(screen)
