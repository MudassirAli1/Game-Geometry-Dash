import pygame
import random
from .settings import *


class Button:
    """Interactive button with hover effects"""
    
    def __init__(self, x, y, width, height, text, color=NEON_BLUE, hover_color=NEON_PINK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, screen):
        """Draw button with effects"""
        color = self.hover_color if self.is_hovered else self.color
        
        # Glow effect
        if self.is_hovered:
            glow_rect = pygame.Rect(
                self.rect.x - 3, self.rect.y - 3,
                self.rect.width + 6, self.rect.height + 6
            )
            pygame.draw.rect(screen, (*color, 80), glow_rect)
        
        # Main button
        pygame.draw.rect(screen, DARK_BG, self.rect)
        pygame.draw.rect(screen, color, self.rect, 3)
        
        # Text
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ParticleSystem:
    """Particle effect system for visual effects"""
    
    def __init__(self):
        self.particles = []
        
    def emit_jump_particles(self, x, y, color):
        """Emit particles on jump"""
        for _ in range(15):
            particle = {
                'x': x,
                'y': y,
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-200, -50),
                'life': 1.0,
                'color': color,
                'size': random.uniform(3, 8)
            }
            self.particles.append(particle)
    
    def emit_death_particles(self, x, y, color):
        """Emit explosion particles on death"""
        for _ in range(40):
            angle = random.uniform(0, 360)
            speed = random.uniform(100, 400)
            particle = {
                'x': x,
                'y': y,
                'vx': speed * pygame.math.Vector2(1, 0).rotate(angle).x,
                'vy': speed * pygame.math.Vector2(1, 0).rotate(angle).y,
                'life': 1.0,
                'color': color,
                'size': random.uniform(4, 12)
            }
            self.particles.append(particle)
    
    def emit_trail_particles(self, x, y, color):
        """Emit trail particles behind player"""
        if random.random() < 0.3:
            particle = {
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vx': random.uniform(-30, -10),
                'vy': random.uniform(-20, 20),
                'life': 0.5,
                'color': color,
                'size': random.uniform(2, 5)
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 2
            particle['size'] *= 0.98
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen, camera_x):
        """Draw all particles"""
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
    """Parallax scrolling background layers"""
    
    def __init__(self):
        self.stars = self._generate_stars(100)
        self.clouds = self._generate_clouds(15)
        self.background_color = DARK_BG
        
    def _generate_stars(self, count):
        """Generate random stars"""
        stars = []
        for _ in range(count):
            stars.append({
                'x': random.randint(0, SCREEN_WIDTH * 3),
                'y': random.randint(0, SCREEN_HEIGHT - 150),
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.1, 0.3),
                'twinkle': random.uniform(0, 360)
            })
        return stars
    
    def _generate_clouds(self, count):
        """Generate cloud shapes"""
        clouds = []
        for _ in range(count):
            clouds.append({
                'x': random.randint(0, SCREEN_WIDTH * 2),
                'y': random.randint(50, SCREEN_HEIGHT - 250),
                'width': random.randint(100, 250),
                'height': random.randint(30, 60),
                'speed': random.uniform(0.05, 0.15)
            })
        return clouds
    
    def update(self, dt, camera_x):
        """Update parallax layers"""
        for star in self.stars:
            star['twinkle'] += dt * 90
            
        # Update background color based on progress
        progress = min(1.0, camera_x / LEVEL_LENGTH)
        r = int(10 + progress * 20)
        g = int(10 + progress * 5)
        b = int(30 + progress * 30)
        self.background_color = (r, g, b)
    
    def draw(self, screen, camera_x):
        """Draw parallax background"""
        # Background fill
        screen.fill(self.background_color)
        
        # Draw clouds (far layer)
        for cloud in self.clouds:
            screen_x = cloud['x'] - camera_x * cloud['speed']
            # Wrap around
            screen_x = screen_x % (SCREEN_WIDTH + cloud['width']) - cloud['width'] // 2
            
            cloud_surface = pygame.Surface((cloud['width'], cloud['height']), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, (40, 40, 80, 40), 
                              (0, 0, cloud['width'], cloud['height']))
            screen.blit(cloud_surface, (screen_x, cloud['y']))
        
        # Draw stars (mid layer)
        for star in self.stars:
            screen_x = star['x'] - camera_x * star['speed']
            # Wrap around
            screen_x = screen_x % SCREEN_WIDTH
            
            # Twinkle effect
            alpha = int(128 + 127 * pygame.math.Vector2(1, 0).rotate(star['twinkle']).x)
            size = int(star['size'])
            
            if size > 0:
                surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 255, 255, alpha), 
                                 (size, size), size)
                screen.blit(surface, (screen_x - size, star['y'] - size))
        
        # Draw grid overlay
        self._draw_grid(screen, camera_x)
    
    def _draw_grid(self, screen, camera_x):
        """Draw subtle grid overlay"""
        grid_size = 60
        start_x = int(camera_x * 0.05 // grid_size) * grid_size
        
        for x in range(start_x, start_x + SCREEN_WIDTH + grid_size, grid_size):
            screen_x = x - camera_x * 0.05
            pygame.draw.line(screen, (25, 25, 50, 20), 
                           (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, (25, 25, 50, 20), 
                           (0, y), (SCREEN_WIDTH, y))


class UIManager:
    """Manages all UI elements"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.particles = ParticleSystem()
        self.background = ParallaxBackground()
        
        # Menu buttons
        menu_center_x = screen_width // 2
        menu_start_y = 300
        button_spacing = 80
        
        self.menu_buttons = [
            Button(menu_center_x - BUTTON_WIDTH//2, menu_start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "START GAME"),
            Button(menu_center_x - BUTTON_WIDTH//2, menu_start_y + button_spacing, BUTTON_WIDTH, BUTTON_HEIGHT, "SETTINGS"),
            Button(menu_center_x - BUTTON_WIDTH//2, menu_start_y + button_spacing * 2, BUTTON_WIDTH, BUTTON_HEIGHT, "LEVEL EDITOR"),
            Button(menu_center_x - BUTTON_WIDTH//2, menu_start_y + button_spacing * 3, BUTTON_WIDTH, BUTTON_HEIGHT, "EXIT"),
        ]
        
        # Pause buttons
        self.pause_buttons = [
            Button(menu_center_x - BUTTON_WIDTH//2, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "RESUME"),
            Button(menu_center_x - BUTTON_WIDTH//2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "RESTART"),
            Button(menu_center_x - BUTTON_WIDTH//2, 450, BUTTON_WIDTH, BUTTON_HEIGHT, "MAIN MENU"),
        ]
        
        # Game over buttons
        self.game_over_buttons = [
            Button(menu_center_x - BUTTON_WIDTH//2, 400, BUTTON_WIDTH, BUTTON_HEIGHT, "RETRY"),
            Button(menu_center_x - BUTTON_WIDTH//2, 480, BUTTON_WIDTH, BUTTON_HEIGHT, "MAIN MENU"),
        ]
        
        # Settings buttons
        self.settings_buttons = [
            Button(menu_center_x - BUTTON_WIDTH//2, 250, BUTTON_WIDTH, BUTTON_HEIGHT, "CHANGE SKIN"),
            Button(menu_center_x - BUTTON_WIDTH//2, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "BACK"),
        ]
        
        # Level editor buttons
        self.editor_buttons = [
            Button(10, 10, 100, 40, "SPIKE"),
            Button(120, 10, 100, 40, "BLOCK"),
            Button(230, 10, 100, 40, "JUMP PAD"),
            Button(SCREEN_WIDTH - 110, 10, 100, 40, "BACK"),
        ]
        
    def handle_event(self, event, buttons=None):
        """Handle events for button list"""
        if buttons is None:
            return None
            
        for button in buttons:
            if button.handle_event(event):
                return button.text
        return None
    
    def draw_hud(self, screen, progress, score, best_score):
        """Draw in-game HUD"""
        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = 20
        
        # Bar background
        pygame.draw.rect(screen, (50, 50, 80), (bar_x, bar_y, bar_width, bar_height))
        
        # Bar fill
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, NEON_GREEN, (bar_x, bar_y, fill_width, bar_height))
        
        # Bar border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Progress text
        progress_text = f"{int(progress)}%"
        text_surface = self.font_small.render(progress_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
        screen.blit(text_surface, text_rect)
        
        # Score
        score_text = f"Score: {score}"
        text_surface = self.font_small.render(score_text, True, NEON_BLUE)
        screen.blit(text_surface, (20, 20))
        
        # Best score
        best_text = f"Best: {best_score}"
        text_surface = self.font_small.render(best_text, True, NEON_YELLOW)
        screen.blit(text_surface, (20, 50))
        
        # Controls hint
        controls_text = "SPACE: Jump | ESC: Pause | R: Restart"
        text_surface = self.font_small.render(controls_text, True, (150, 150, 150))
        screen.blit(text_surface, (self.screen_width - 350, self.screen_height - 30))
    
    def draw_menu(self, screen):
        """Draw main menu"""
        # Animated title
        title_text = "NEON DASH"
        
        # Title glow effect
        glow_offset = int(10 * pygame.time.get_ticks() / 1000) % 20
        title_color = (
            min(255, NEON_BLUE[0] + glow_offset),
            min(255, NEON_BLUE[1] + glow_offset),
            min(255, NEON_BLUE[2] + glow_offset)
        )
        
        title_surface = self.font_large.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        
        # Title shadow
        shadow_surface = self.font_large.render(title_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle = "A Geometry Dash Clone"
        subtitle_surface = self.font_small.render(subtitle, True, (150, 150, 150))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(screen)
    
    def draw_pause_menu(self, screen):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_surface = self.font_large.render("PAUSED", True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_surface, title_rect)
        
        # Buttons
        for button in self.pause_buttons:
            button.draw(screen)
    
    def draw_game_over(self, screen, score, best_score, won=False):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if won:
            title_text = "LEVEL COMPLETE!"
            title_color = NEON_GREEN
        else:
            title_text = "GAME OVER"
            title_color = NEON_RED
        
        # Title
        title_surface = self.font_large.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_surface, title_rect)
        
        # Score
        score_text = f"Score: {score}"
        text_surface = self.font_medium.render(score_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 230))
        screen.blit(text_surface, text_rect)
        
        # Best score
        best_text = f"Best: {best_score}"
        text_surface = self.font_medium.render(best_text, True, NEON_YELLOW)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 280))
        screen.blit(text_surface, text_rect)
        
        # New best indicator
        if score > best_score and score > 0:
            new_best_text = "NEW BEST!"
            text_surface = self.font_small.render(new_best_text, True, NEON_GREEN)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 330))
            screen.blit(text_surface, text_rect)
        
        # Buttons
        for button in self.game_over_buttons:
            button.draw(screen)
    
    def draw_settings(self, screen, current_skin):
        """Draw settings screen"""
        # Title
        title_surface = self.font_large.render("SETTINGS", True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Current skin preview
        preview_text = "Player Skin:"
        text_surface = self.font_medium.render(preview_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(text_surface, text_rect)
        
        # Skin preview box
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
        
        # Skin name
        skin_names = ["Blue", "Pink", "Green", "Yellow", "Orange"]
        skin_text = skin_names[current_skin]
        text_surface = self.font_small.render(skin_text, True, skin_color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 290))
        screen.blit(text_surface, text_rect)
        
        # Buttons
        for button in self.settings_buttons:
            button.draw(screen)
    
    def draw_level_editor(self, screen):
        """Draw level editor"""
        # Title
        title_surface = self.font_medium.render("LEVEL EDITOR (Coming Soon)", True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title_surface, title_rect)
        
        # Buttons
        for button in self.editor_buttons:
            button.draw(screen)
        
        # Instructions
        instructions = "Click to place obstacles. Select type from top buttons."
        text_surface = self.font_small.render(instructions, True, (150, 150, 150))
        screen.blit(text_surface, (20, SCREEN_HEIGHT - 40))
