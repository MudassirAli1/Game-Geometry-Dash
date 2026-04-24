import pygame
from .settings import *


class Player:
    """The player's cube that jumps and rotates."""

    def __init__(self, x, y, skin_index=0):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_y = 0
        self.on_ground = False
        self.alive = True
        self.rotation = 0

        # Skin/color
        self.skin_index = skin_index
        self.color = PLAYER_SKINS[skin_index]

        # Trail effect (ghost images behind player)
        self.trail_positions = []
        self.max_trail = 5

        # Double jump (can jump twice in the air)
        self.jumps_remaining = 2
        self.max_jumps = 2
        self.is_holding_jump = False

    def reset(self):
        """Put player back at the start."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.velocity_y = 0
        self.on_ground = False
        self.alive = True
        self.rotation = 0
        self.trail_positions = []
        self.jumps_remaining = 2
        self.is_holding_jump = False

    def jump(self):
        """Make the player jump. Returns True if successful."""
        if self.jumps_remaining > 0:
            self.velocity_y = JUMP_FORCE
            if self.on_ground:
                self.on_ground = False
            self.jumps_remaining -= 1
            return True
        return False

    def update(self, dt, ground_y):
        """Update physics and position."""
        if not self.alive:
            return

        # Move right automatically (like Geometry Dash)
        self.rect.x += MOVE_SPEED * dt

        # Gravity pulls down
        self.velocity_y += GRAVITY * dt

        # Holding jump while going up = slower ascent (easier to control)
        if self.is_holding_jump and self.velocity_y < 0:
            self.velocity_y *= 0.95

        # Move up or down
        self.rect.y += self.velocity_y * dt

        # Hit the ground?
        if self.rect.y >= ground_y - PLAYER_SIZE:
            self.rect.y = ground_y - PLAYER_SIZE
            self.velocity_y = 0
            self.on_ground = True
            self.jumps_remaining = self.max_jumps  # Get jumps back
            # Snap rotation to 0, 90, 180, etc.
            self.rotation = round(self.rotation / 90) * 90
        else:
            self.on_ground = False
            # Spin while in the air
            self.rotation += 350 * dt

        # Save position for trail effect
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        if len(self.trail_positions) > self.max_trail:
            self.trail_positions.pop(0)

    def get_collision_rects(self):
        """Get a slightly smaller box for fairer collisions."""
        margin = 4
        return pygame.Rect(
            self.rect.x + margin,
            self.rect.y + margin,
            self.rect.width - margin * 2,
            self.rect.height - margin * 2
        )

    def draw(self, screen, camera_x):
        """Draw the player cube with trail and rotation."""
        # Draw trail (fading ghosts behind)
        for i, (tx, ty) in enumerate(self.trail_positions):
            alpha = int(255 * (i / len(self.trail_positions)) * 0.5)
            trail_size = PLAYER_SIZE * (i / len(self.trail_positions)) * 0.6
            trail_rect = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
            pygame.draw.rect(trail_rect, (*self.color, alpha), (0, 0, trail_size, trail_size))
            screen_x = tx - camera_x
            screen.blit(trail_rect, (screen_x - trail_size/2, ty - trail_size/2))

        # Draw rotated cube
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        rotated_surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(rotated_surface, self.color, (0, 0, PLAYER_SIZE, PLAYER_SIZE))
        pygame.draw.rect(rotated_surface, WHITE, (0, 0, PLAYER_SIZE, PLAYER_SIZE), 2)

        rotated = pygame.transform.rotate(rotated_surface, -self.rotation)
        new_rect = rotated.get_rect(center=(screen_x + PLAYER_SIZE/2, screen_y + PLAYER_SIZE/2))
        screen.blit(rotated, new_rect.topleft)

    def change_skin(self, skin_index):
        """Change the cube's color."""
        self.skin_index = skin_index
        self.color = PLAYER_SKINS[skin_index]
