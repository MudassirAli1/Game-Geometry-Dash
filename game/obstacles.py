import pygame
import random
from .settings import *


class Obstacle:
    """Base obstacle class"""
    
    def __init__(self, x, y, width, height, obstacle_type="spike"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obstacle_type
        self.moving = False
        self.move_range = 0
        self.move_speed = 0
        self.move_direction = 1
        self.start_y = y
        self.color = NEON_RED if obstacle_type == "spike" else NEON_ORANGE
        
    def update(self, dt):
        """Update moving obstacles"""
        if self.moving:
            self.rect.y += self.move_speed * self.move_direction * dt
            if abs(self.rect.y - self.start_y) > self.move_range:
                self.move_direction *= -1
    
    def draw(self, screen, camera_x):
        """Draw obstacle"""
        screen_x = self.rect.x - camera_x
        
        if self.type == "spike":
            self._draw_spike(screen, screen_x)
        elif self.type == "block":
            self._draw_block(screen, screen_x)
        elif self.type == "gap":
            self._draw_gap(screen, screen_x)
        elif self.type == "jump_pad":
            self._draw_jump_pad(screen, screen_x)
    
    def _draw_spike(self, screen, screen_x):
        """Draw triangle spike"""
        points = [
            (screen_x, self.rect.bottom),
            (screen_x + self.rect.width / 2, self.rect.top),
            (screen_x + self.rect.width, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Inner glow
        inner_points = [
            (screen_x + 4, self.rect.bottom - 2),
            (screen_x + self.rect.width / 2, self.rect.top + 6),
            (screen_x + self.rect.width - 4, self.rect.bottom - 2)
        ]
        pygame.draw.polygon(screen, (*self.color, 100), inner_points)
    
    def _draw_block(self, screen, screen_x):
        """Draw block obstacle"""
        pygame.draw.rect(screen, self.color, (screen_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, WHITE, (screen_x, self.rect.y, self.rect.width, self.rect.height), 2)
        
        # Grid pattern on block
        grid_size = 10
        for i in range(0, self.rect.width, grid_size):
            pygame.draw.line(screen, (*self.color, 80), 
                           (screen_x + i, self.rect.y), 
                           (screen_x + i, self.rect.bottom))
        for i in range(0, self.rect.height, grid_size):
            pygame.draw.line(screen, (*self.color, 80), 
                           (screen_x, self.rect.y + i), 
                           (screen_x + self.rect.right, self.rect.y + i))
    
    def _draw_gap(self, screen, screen_x):
        """Draw gap (visual indicator)"""
        # Gaps are handled as missing ground, this is just visual
        pass
    
    def _draw_jump_pad(self, screen, screen_x):
        """Draw jump pad"""
        pygame.draw.rect(screen, NEON_GREEN, (screen_x, self.rect.y, self.rect.width, self.rect.height))
        pygame.draw.rect(screen, WHITE, (screen_x, self.rect.y, self.rect.width, self.rect.height), 2)
        
        # Arrow indicator
        arrow_y = self.rect.top - 15
        points = [
            (screen_x + self.rect.width/2, arrow_y - 10),
            (screen_x + self.rect.width/2 - 10, arrow_y + 5),
            (screen_x + self.rect.width/2 + 10, arrow_y + 5)
        ]
        pygame.draw.polygon(screen, NEON_GREEN, points)
    
    def get_collision_rect(self):
        """Get collision rectangle"""
        if self.type == "spike":
            # Smaller hitbox for spikes (fairer)
            margin = 8
            return pygame.Rect(
                self.rect.x + margin,
                self.rect.y + margin,
                self.rect.width - margin * 2,
                self.rect.height - margin // 2
            )
        return self.rect


class Level:
    """Level manager that generates and manages obstacles"""
    
    def __init__(self):
        self.obstacles = []
        self.length = LEVEL_LENGTH
        self.difficulty = 1.0
        self.generated_distance = 0
        self.next_obstacle_x = 600
        
    def reset(self):
        """Reset level"""
        self.obstacles = []
        self.generated_distance = 0
        self.next_obstacle_x = 600
        self.difficulty = 1.0
        
    def generate_ahead(self, player_x, screen_width):
        """Generate obstacles ahead of player - Currently disabled for clear level"""
        # No obstacles generated - clear level
        pass
    
    def _generate_obstacle(self):
        """Generate a single obstacle"""
        # Increase difficulty over distance
        progress = self.next_obstacle_x / self.length
        self.difficulty = 1.0 + progress * 2
        
        # Random spacing based on difficulty
        spacing = random.randint(
            int(OBSTACLE_SPACING_MIN / self.difficulty),
            int(OBSTACLE_SPACING_MAX / self.difficulty)
        )
        spacing = max(200, spacing)  # Minimum spacing
        
        obstacle_type = self._choose_obstacle_type(progress)
        
        if obstacle_type == "spike":
            self._place_spike(spacing)
        elif obstacle_type == "block":
            self._place_block(spacing)
        elif obstacle_type == "jump_pad":
            self._place_jump_pad(spacing)
            
    def _choose_obstacle_type(self, progress):
        """Choose obstacle type based on progress"""
        roll = random.random()
        
        if progress < 0.3:
            # Early game: mostly spikes
            return "spike" if roll < 0.8 else "jump_pad"
        elif progress < 0.6:
            # Mid game: mix of spikes and blocks
            if roll < 0.5:
                return "spike"
            elif roll < 0.85:
                return "block"
            else:
                return "jump_pad"
        else:
            # Late game: all types, more blocks
            if roll < 0.4:
                return "spike"
            elif roll < 0.85:
                return "block"
            else:
                return "jump_pad"
    
    def _place_spike(self, spacing):
        """Place spike obstacle"""
        self.next_obstacle_x += spacing
        
        # Random size
        width = random.choice([30, 40, 40])
        height = random.choice([30, 40, 50])
        
        # Sometimes place on ceiling
        if random.random() < 0.2 and self.difficulty > 1.5:
            y = 50
            height = 40
        else:
            y = GROUND_Y - height
            
        obstacle = Obstacle(self.next_obstacle_x, y, width, height, "spike")
        self.obstacles.append(obstacle)
        
    def _place_block(self, spacing):
        """Place block obstacle"""
        self.next_obstacle_x += spacing
        
        width = random.choice([40, 60, 80])
        height = random.choice([40, 60, 80, 120])
        
        # Sometimes make it moving
        moving = random.random() < 0.3 and self.difficulty > 1.3
        
        if moving:
            y = GROUND_Y - height - 100
            obstacle = Obstacle(self.next_obstacle_x, y, width, height, "block")
            obstacle.moving = True
            obstacle.move_range = 80
            obstacle.move_speed = 100
        else:
            y = GROUND_Y - height
            obstacle = Obstacle(self.next_obstacle_x, y, width, height, "block")
            
        self.obstacles.append(obstacle)
        
    def _place_jump_pad(self, spacing):
        """Place jump pad"""
        self.next_obstacle_x += spacing
        
        width = 50
        height = 20
        y = GROUND_Y - height
        
        obstacle = Obstacle(self.next_obstacle_x, y, width, height, "jump_pad")
        self.obstacles.append(obstacle)
        
        # Place spike after jump pad to create challenge
        if random.random() < 0.6:
            spike_x = self.next_obstacle_x + 150
            spike_height = 40
            spike = Obstacle(spike_x, GROUND_Y - spike_height, 30, spike_height, "spike")
            self.obstacles.append(spike)
            self.next_obstacle_x = spike_x
    
    def check_collisions(self, player_rect):
        """Check player collision with obstacles"""
        for obstacle in self.obstacles:
            obs_rect = obstacle.get_collision_rect()
            if player_rect.colliderect(obs_rect):
                if obstacle.type == "jump_pad":
                    return "jump_pad", obstacle
                else:
                    return "collision", obstacle
        return None, None
    
    def get_progress(self, player_x):
        """Get level progress as percentage"""
        progress = (player_x / self.length) * 100
        return min(100, max(0, progress))
    
    def draw_ground(self, screen, camera_x, screen_width):
        """Draw ground with neon style"""
        # Main ground line
        ground_screen_y = GROUND_Y
        pygame.draw.line(screen, NEON_BLUE, (0, ground_screen_y), (screen_width, ground_screen_y), 3)
        
        # Grid pattern below ground
        grid_size = 40
        start_grid_x = int(camera_x // grid_size) * grid_size
        
        for x in range(start_grid_x, camera_x + screen_width + grid_size, grid_size):
            screen_x = x - camera_x
            alpha = 50
            pygame.draw.line(screen, (*GRID_COLOR, alpha), 
                           (screen_x, ground_screen_y), 
                           (screen_x, screen_height := SCREEN_HEIGHT))
        
        for y in range(ground_screen_y, SCREEN_HEIGHT, grid_size // 2):
            pygame.draw.line(screen, (*GRID_COLOR, 30), 
                           (0, y), 
                           (screen_width, y))
        
        # Ground glow effect
        glow_surface = pygame.Surface((screen_width, 10), pygame.SRCALPHA)
        for y in range(10):
            alpha = int(100 * (1 - y/10))
            pygame.draw.line(glow_surface, (*NEON_BLUE, alpha), 
                           (0, y), (screen_width, y))
        screen.blit(glow_surface, (0, ground_screen_y))
    
    def is_complete(self, player_x):
        """Check if level is complete"""
        return player_x >= self.length
