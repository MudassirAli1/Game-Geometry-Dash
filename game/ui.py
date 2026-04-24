import pygame
import random
from .settings import *


class Button:
    """A clickable button with hover effect."""

    def __init__(self, x, y, width, height, text, color=NEON_BLUE, hover_color=NEON_PINK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, FONT_SIZE_MEDIUM)

    def handle_event(self, event):
        """Check if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def draw(self, screen):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color

        # Glow when hovered
        if self.is_hovered:
            glow_rect = pygame.Rect(
                self.rect.x - 3, self.rect.y - 3,
                self.rect.width + 6, self.rect.height + 6
            )
            pygame.draw.rect(screen, (*color, 80), glow_rect)

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
        """Sparks when jumping."""
        for _ in range(15):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-200, -50),
                'life': 1.0,
                'color': color,
                'size': random.uniform(3, 8)
            })

    def emit_death_particles(self, x, y, color):
        """Explosion when dying."""
        for _ in range(40):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 400)
            import math
            self.particles.append({
                'x': x, 'y': y,
                'vx': speed * math.cos(math.radians(angle)),
                'vy': speed * math.sin(math.radians(angle)),
                'life': 1.0,
                'color': color,
                'size': random.uniform(4, 12)
            })

    def emit_trail_particles(self, x, y, color):
        """Sparks behind player."""
        if random.random() < 0.3:
            self.particles.append({
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vx': random.uniform(-30, -10),
                'vy': random.uniform(-20, 20),
                'life': 0.5,
                'color': color,
                'size': random.uniform(2, 5)
            })

    def update(self, dt):
        """Update all particles."""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 2
            particle['size'] *= 0.98

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen, camera_x):
        """Draw all particles."""
        for particle in self.particles:
            screen_x = particle['x'] - camera_x
            alpha = int(255 * particle['life'])
            size = int(particle['size'])

            if size > 0:
                surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(surface, (*particle['color'], alpha),
                                 (size//2, size//2), size//2)
                screen.blit(surface, (screen_x - size//2, particle['y'] - size//2))


class ParallaxBackground:
    """The scrolling background with stars."""

    def __init__(self):
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH * 3),
                'y': random.randint(0, SCREEN_HEIGHT - 150),
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.1, 0.3),
                'twinkle': random.uniform(0, 360)
            })
        self.background_color = DARK_BG

    def update(self, dt, camera_x):
        """Update star twinkling."""
        for star in self.stars:
            star['twinkle'] += dt * 90

    def draw(self, screen, camera_x):
        """Draw the background."""
        screen.fill(self.background_color)

        # Draw stars
        for star in self.stars:
            screen_x = star['x'] - camera_x * star['speed']
            screen_x = screen_x % SCREEN_WIDTH

            size = int(star['size'])
            import math
            brightness = int(128 + 127 * math.cos(math.radians(star['twinkle'])))

            if size > 0:
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 255, 255, brightness),
                                 (size, size), size)
                screen.blit(surface, (screen_x - size, star['y'] - size))


class UIManager:
    """Handles all screens and buttons."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
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
        """Check if any button was clicked."""
        if buttons is None:
            return None
        for button in buttons:
            if button.handle_event(event):
                return button.text
        return None

    def draw_hud(self, screen, progress, score, best_score):
        """Draw score and progress bar."""
        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = 20

        pygame.draw.rect(screen, (50, 50, 80), (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, NEON_GREEN, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        progress_text = f"{int(progress)}%"
        text_surface = self.font_small.render(progress_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
        screen.blit(text_surface, text_rect)

        # Scores
        screen.blit(self.font_small.render(f"Score: {score}", True, NEON_BLUE), (20, 20))
        screen.blit(self.font_small.render(f"Best: {best_score}", True, NEON_YELLOW), (20, 50))

        # Controls hint
        screen.blit(self.font_small.render("SPACE: Jump | ESC: Pause | R: Restart", True, (150, 150, 150)),
                   (self.screen_width - 350, self.screen_height - 30))

    def draw_menu(self, screen):
        """Draw the main menu screen."""
        # Title
        title_surface = self.font_large.render("NEON DASH", True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_surface, title_rect)

        # Subtitle
        subtitle = "A Geometry Dash Clone"
        subtitle_surface = self.font_small.render(subtitle, True, (150, 150, 150))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(subtitle_surface, subtitle_rect)

        for button in self.menu_buttons:
            button.draw(screen)

    def draw_pause_menu(self, screen):
        """Draw pause overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        screen.blit(self.font_large.render("PAUSED", True, NEON_BLUE),
                   (self.screen_width // 2 - 100, 150))

        for button in self.pause_buttons:
            button.draw(screen)

    def draw_game_over(self, screen, score, best_score, won=False):
        """Draw game over screen."""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if won:
            title_text = "LEVEL COMPLETE!"
            title_color = NEON_GREEN
        else:
            title_text = "GAME OVER"
            title_color = NEON_RED

        screen.blit(self.font_large.render(title_text, True, title_color),
                   (self.screen_width // 2 - 200, 150))
        screen.blit(self.font_medium.render(f"Score: {score}", True, WHITE),
                   (self.screen_width // 2 - 50, 230))
        screen.blit(self.font_medium.render(f"Best: {best_score}", True, NEON_YELLOW),
                   (self.screen_width // 2 - 50, 280))

        if score > best_score and score > 0:
            screen.blit(self.font_small.render("NEW BEST!", True, NEON_GREEN),
                       (self.screen_width // 2 - 50, 330))

        for button in self.game_over_buttons:
            button.draw(screen)

    def draw_settings(self, screen, current_skin):
        """Draw settings screen."""
        screen.blit(self.font_large.render("SETTINGS", True, NEON_BLUE),
                   (self.screen_width // 2 - 80, 100))

        screen.blit(self.font_medium.render("Player Skin:", True, WHITE),
                   (self.screen_width // 2 - 60, 180))

        # Skin preview
        skin_color = PLAYER_SKINS[current_skin]
        preview_size = 60
        preview_rect = pygame.Rect(
            self.screen_width // 2 - preview_size // 2,
            210,
            preview_size,
            preview_size
        )
        pygame.draw.rect(screen, skin_color, preview_rect)
        pygame.draw.rect(screen, WHITE, preview_rect, 3)

        skin_names = ["Blue", "Pink", "Green", "Yellow", "Orange"]
        screen.blit(self.font_small.render(skin_names[current_skin], True, skin_color),
                   (self.screen_width // 2 - 30, 290))

        for button in self.settings_buttons:
            button.draw(screen)
