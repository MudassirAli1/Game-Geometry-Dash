import pygame
import random
from .settings import *


class Obstacle:
    """An obstacle in the game - spikes, blocks, or jump pads."""

    def __init__(self, x, y, width, height, obstacle_type="spike"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obstacle_type
        self.color = NEON_RED if obstacle_type == "spike" else NEON_ORANGE

        # For moving obstacles (rare)
        self.moving = False
        self.move_range = 0
        self.move_speed = 0
        self.move_direction = 1
        self.start_y = y

    def update(self, dt):
        """Update position for moving obstacles."""
        if self.moving:
            self.rect.y += self.move_speed * self.move_direction * dt
            if abs(self.rect.y - self.start_y) > self.move_range:
                self.move_direction *= -1

    def draw(self, screen, camera_x):
        """Draw the obstacle on screen."""
        screen_x = self.rect.x - camera_x

        if self.type == "spike":
            self._draw_spike(screen, screen_x)
        elif self.type == "block":
            self._draw_block(screen, screen_x)
        elif self.type == "jump_pad":
            self._draw_jump_pad(screen, screen_x)

    def _draw_spike(self, screen, screen_x):
        """Draw a triangle spike."""
        points = [
            (screen_x, self.rect.bottom),
            (screen_x + self.rect.width / 2, self.rect.top),
            (screen_x + self.rect.width, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

    def _draw_block(self, screen, screen_x):
        """Draw a rectangular block."""
        pygame.draw.rect(screen, self.color, (screen_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, WHITE, (screen_x, self.rect.y, self.rect.width, self.rect.height), 2)

    def _draw_jump_pad(self, screen, screen_x):
        """Draw a green jump pad."""
        pygame.draw.rect(screen, NEON_GREEN, (screen_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, WHITE, (screen_x, self.rect.y, self.rect.width, self.rect.height), 2)

    def get_collision_rect(self):
        """Get the rectangle used for collision checking."""
        if self.type == "spike":
            # Make spike hitbox smaller (more fair for player)
            margin = 8
            return pygame.Rect(
                self.rect.x + margin,
                self.rect.y + margin,
                self.rect.width - margin * 2,
                self.rect.height - margin // 2
            )
        return self.rect


class Level:
    """Creates and manages all obstacles in the level."""

    def __init__(self):
        self.obstacles = []
        self.length = LEVEL_LENGTH
        self.next_obstacle_x = 600  # Where to place next obstacle

    def reset(self):
        """Clear all obstacles and start over."""
        self.obstacles = []
        self.next_obstacle_x = 600

    def generate_ahead(self, player_x, screen_width):
        """Generate obstacles ahead of the player."""
        # Keep generating until we're past the screen
        while self.next_obstacle_x < player_x + screen_width + 500:
            self._add_next_obstacle()

    def _add_next_obstacle(self):
        """Add one obstacle (or a pair) at next_obstacle_x."""
        # Pick random distance to next obstacle
        spacing = random.randint(250, 450)
        self.next_obstacle_x += spacing

        # Pick random type (80% spikes, 15% blocks, 5% jump pads)
        roll = random.random()

        if roll < 0.80:
            # SPIKE - most common
            width = random.choice([30, 40])
            height = random.choice([30, 40, 50])
            obstacle = Obstacle(self.next_obstacle_x, GROUND_Y - height, width, height, "spike")
            self.obstacles.append(obstacle)

        elif roll < 0.95:
            # BLOCK - less common
            width = random.choice([40, 60, 80])
            height = random.choice([40, 60, 80])
            obstacle = Obstacle(self.next_obstacle_x, GROUND_Y - height, width, height, "block")
            self.obstacles.append(obstacle)

        else:
            # JUMP PAD - rare, launches you high
            width = 50
            height = 20
            obstacle = Obstacle(self.next_obstacle_x, GROUND_Y - height, width, height, "jump_pad")
            self.obstacles.append(obstacle)

    def check_collisions(self, player_rect):
        """Check if player hits any obstacle.
        Returns: (type, obstacle) or (None, None)"""
        for obstacle in self.obstacles:
            obs_rect = obstacle.get_collision_rect()
            if player_rect.colliderect(obs_rect):
                if obstacle.type == "jump_pad":
                    return "jump_pad", obstacle
                else:
                    return "collision", obstacle
        return None, None

    def get_progress(self, player_x):
        """Get how far through the level player is (0-100%)."""
        progress = (player_x / self.length) * 100
        return min(100, max(0, progress))

    def is_complete(self, player_x):
        """Check if player reached the end."""
        return player_x >= self.length

    def draw_ground(self, screen, camera_x, screen_width):
        """Draw the ground line."""
        pygame.draw.line(screen, NEON_BLUE, (0, GROUND_Y), (screen_width, GROUND_Y), 3)
