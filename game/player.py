import pygame
from .settings import *


class Player:
    """Player cube with physics and rotation animation"""

    def __init__(self, x, y, skin_index=0):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_y = 0
        self.on_ground = False
        self.alive = True
        self.rotation = 0
        self.skin_index = skin_index
        self.color = PLAYER_SKINS[skin_index]
        self.trail_positions = []
        self.max_trail = 5
        self.jumps_remaining = 2  # Double jump
        self.max_jumps = 2
        self.is_holding_jump = False  # Track if space is being held
        
    def reset(self):
        """Reset player to starting position"""
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
        """Make player jump (supports double jump)"""
        if self.jumps_remaining > 0:
            self.velocity_y = JUMP_FORCE
            if self.on_ground:
                self.on_ground = False
            self.jumps_remaining -= 1
            return True
        return False
    
    def release_jump(self):
        """Called when space key is released"""
        self.is_holding_jump = False
    
    def update(self, dt, ground_y):
        """Update player physics and position"""
        if not self.alive:
            return

        # Move forward automatically (Geometry Dash style)
        self.rect.x += MOVE_SPEED * dt

        # Apply gravity
        self.velocity_y += GRAVITY * dt
        
        # If holding jump and moving upward, reduce upward velocity for controlled ascent
        if self.is_holding_jump and self.velocity_y < 0:
            self.velocity_y *= 0.95  # Slow down ascent

        # Update vertical position
        self.rect.y += self.velocity_y * dt
        
        # Ground collision
        if self.rect.y >= ground_y - PLAYER_SIZE:
            self.rect.y = ground_y - PLAYER_SIZE
            self.velocity_y = 0
            self.on_ground = True
            self.jumps_remaining = self.max_jumps  # Reset jumps when touching ground
            # Snap rotation to nearest 90 degrees when on ground
            target_rotation = round(self.rotation / 90) * 90
            self.rotation = target_rotation
        else:
            self.on_ground = False
            # Rotate while in air (Geometry Dash style)
            self.rotation += 350 * dt  # degrees per second
        
        # Update trail
        self.trail_positions.append((self.rect.centerx, self.rect.centery))
        if len(self.trail_positions) > self.max_trail:
            self.trail_positions.pop(0)
    
    def get_distance_to_obstacle(self, obstacles, direction=1):
        """Get distance to nearest obstacle in front of player"""
        player_right = self.rect.right
        min_distance = float('inf')

        for obstacle in obstacles:
            if direction > 0 and obstacle.rect.left > player_right:
                distance = obstacle.rect.left - player_right
                min_distance = min(min_distance, distance)
            elif direction < 0 and obstacle.rect.right < self.rect.left:
                distance = self.rect.left - obstacle.rect.right
                min_distance = min(min_distance, distance)

        return min_distance if min_distance != float('inf') else 9999
    
    def get_collision_rects(self):
        """Get slightly smaller collision boxes for fairer collision"""
        margin = 4
        return pygame.Rect(
            self.rect.x + margin,
            self.rect.y + margin,
            self.rect.width - margin * 2,
            self.rect.height - margin * 2
        )
    
    def draw(self, screen, camera_x):
        """Draw player with rotation and trail effect"""
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail_positions):
            alpha = int(255 * (i / len(self.trail_positions)) * 0.5)
            trail_size = PLAYER_SIZE * (i / len(self.trail_positions)) * 0.6
            trail_rect = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.rect(trail_rect, color_with_alpha, (0, 0, trail_size, trail_size))
            screen_x = tx - camera_x
            screen.blit(trail_rect, (screen_x - trail_size/2, ty - trail_size/2))
        
        # Draw rotated player cube
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        
        # Create rotated surface
        rotated_surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(rotated_surface, self.color, (0, 0, PLAYER_SIZE, PLAYER_SIZE))
        pygame.draw.rect(rotated_surface, WHITE, (0, 0, PLAYER_SIZE, PLAYER_SIZE), 2)
        
        # Inner glow effect
        inner_size = PLAYER_SIZE - 8
        inner_rect = pygame.Rect(4, 4, inner_size, inner_size)
        pygame.draw.rect(rotated_surface, (*self.color, 150), inner_rect)
        
        rotated = pygame.transform.rotate(rotated_surface, -self.rotation)
        new_rect = rotated.get_rect(center=(screen_x + PLAYER_SIZE/2, screen_y + PLAYER_SIZE/2))
        screen.blit(rotated, new_rect.topleft)
    
    def change_skin(self, skin_index):
        """Change player skin color"""
        self.skin_index = skin_index
        self.color = PLAYER_SKINS[skin_index]
