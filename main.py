import pygame
import sys
import json
import os
import random

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.settings import *
from game.player import Player
from game.obstacles import Level
from game.ui import UIManager


class SaveManager:
    """Manages saving and loading game data"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {
            "best_score": 0,
            "last_score": 0,
            "skin_index": 0
        }
        self.load()
    
    def load(self):
        """Load save data from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
            except (json.JSONDecodeError, IOError):
                print("Warning: Could not load save file, using defaults")
    
    def save(self):
        """Save data to file"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save data: {e}")
    
    def update_score(self, score):
        """Update score and best score"""
        self.data["last_score"] = score
        if score > self.data["best_score"]:
            self.data["best_score"] = score
            self.save()
            return True  # New best
        self.save()
        return False
    
    @property
    def best_score(self):
        return self.data["best_score"]
    
    @property
    def last_score(self):
        return self.data["last_score"]
    
    @property
    def skin_index(self):
        return self.data["skin_index"]
    
    @skin_index.setter
    def skin_index(self, value):
        self.data["skin_index"] = value
        self.save()


class SoundManager:
    """Manages game sounds"""
    
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._init_sounds()
    
    def _init_sounds(self):
        """Initialize sound effects"""
        try:
            # Try to load sounds, use placeholders if not found
            self.sounds['jump'] = None
            self.sounds['death'] = None
            self.sounds['jump_pad'] = None
            
            # Check if sound files exist
            jump_sound_path = os.path.join("assets", "sounds", "jump.wav")
            if os.path.exists(jump_sound_path):
                self.sounds['jump'] = pygame.mixer.Sound(jump_sound_path)
                
            death_sound_path = os.path.join("assets", "sounds", "death.wav")
            if os.path.exists(death_sound_path):
                self.sounds['death'] = pygame.mixer.Sound(death_sound_path)
                
            jump_pad_path = os.path.join("assets", "sounds", "jump_pad.wav")
            if os.path.exists(jump_pad_path):
                self.sounds['jump_pad'] = pygame.mixer.Sound(jump_pad_path)
                
        except Exception as e:
            print(f"Warning: Could not load sounds: {e}")
            self.enabled = False
    
    def play(self, sound_name):
        """Play a sound effect"""
        if not self.enabled:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except:
                pass
    
    def generate_placeholder_sounds(self):
        """Generate simple placeholder sounds using pygame"""
        try:
            # Generate jump sound (short upward tone)
            self.sounds['jump'] = self._generate_tone(440, 660, 0.15)
            
            # Generate death sound (short downward noise)
            self.sounds['death'] = self._generate_tone(440, 220, 0.2)
            
            # Generate jump pad sound (bright tone)
            self.sounds['jump_pad'] = self._generate_tone(550, 880, 0.1)
            
            self.enabled = True
        except Exception as e:
            print(f"Warning: Could not generate placeholder sounds: {e}")
    
    def _generate_tone(self, start_freq, end_freq, duration):
        """Generate a simple tone"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        
        # Create buffer
        buffer = bytearray(n_samples * 2)
        
        import struct
        import math
        
        for i in range(n_samples):
            t = i / sample_rate
            progress = i / n_samples
            freq = start_freq + (end_freq - start_freq) * progress
            value = int(10000 * math.sin(2 * math.pi * freq * t))
            # Clamp value
            value = max(-32768, min(32767, value))
            struct.pack_into('<h', buffer, i * 2, value)
        
        sound = pygame.mixer.Sound(buffer=buffer)
        return sound


class Game:
    """Main game class"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Clock for delta time
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        
        # Game state
        self.state = STATE_MENU
        self.camera_x = 0
        
        # Initialize systems
        self.save_manager = SaveManager(SAVE_FILE)
        self.sound_manager = SoundManager()
        self.sound_manager.generate_placeholder_sounds()
        self.ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Game objects
        self.player = Player(PLAYER_X, GROUND_Y - PLAYER_SIZE, self.save_manager.skin_index)
        self.level = Level()
        
        # Effects
        self.death_flash = 0
        
        # Level editor
        self.editor_selected_type = "spike"
        
        # FPS display
        self.fps = 0
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            self.delta_time = self.clock.tick(FPS) / 1000.0
            # Clamp delta time
            self.delta_time = max(MIN_DELTA, min(MAX_DELTA, self.delta_time))
            
            # Handle events
            running = self._handle_events()
            
            # Update
            if self.state == STATE_PLAYING:
                self._update_game()
            elif self.state == STATE_MENU:
                self.ui_manager.background.update(self.delta_time, self.camera_x)
            elif self.state == STATE_LEVEL_EDITOR:
                self._update_level_editor()
            
            # Update particles
            self.ui_manager.particles.update(self.delta_time)
            
            # Draw
            self._draw()
            
            # Update display
            pygame.display.flip()
            
            # Track FPS
            self.fps = self.clock.get_fps()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # UI events for buttons (must be checked first)
            if self.state == STATE_MENU:
                result = self.ui_manager.handle_event(event, self.ui_manager.menu_buttons)
                if result:
                    self._handle_menu_button(result)
            elif self.state == STATE_PAUSED:
                result = self.ui_manager.handle_event(event, self.ui_manager.pause_buttons)
                if result:
                    self._handle_pause_button(result)
            elif self.state == STATE_GAME_OVER:
                result = self.ui_manager.handle_event(event, self.ui_manager.game_over_buttons)
                if result:
                    self._handle_game_over_button(result)
            elif self.state == STATE_SETTINGS:
                result = self.ui_manager.handle_event(event, self.ui_manager.settings_buttons)
                if result:
                    self._handle_settings_button(result)
            elif self.state == STATE_LEVEL_EDITOR:
                result = self.ui_manager.handle_event(event, self.ui_manager.editor_buttons)
                if result:
                    self._handle_editor_button(result)

            # Then handle key/mouse events that aren't handled by UI
            if event.type == pygame.KEYDOWN:
                self._handle_key_down(event)

            if event.type == pygame.KEYUP:
                self._handle_key_up(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_button(event)

        return True
    
    def _handle_key_down(self, event):
        """Handle key press"""
        if event.key == pygame.K_ESCAPE:
            if self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
            elif self.state in [STATE_SETTINGS, STATE_LEVEL_EDITOR]:
                self.state = STATE_MENU
            elif self.state == STATE_GAME_OVER:
                self._restart_game()

        elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
            if self.state == STATE_PLAYING:
                self.player.is_holding_jump = True
                if self.player.jump():
                    self.sound_manager.play('jump')
                    self.ui_manager.particles.emit_jump_particles(
                        self.player.rect.centerx,
                        self.player.rect.bottom,
                        self.player.color
                    )

        elif event.key == pygame.K_r:
            if self.state in [STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER]:
                self._restart_game()

        return True

    def _handle_key_up(self, event):
        """Handle key release"""
        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
            if self.state == STATE_PLAYING:
                self.player.release_jump()
    
    def _handle_mouse_button(self, event):
        """Handle mouse click"""
        if self.state == STATE_LEVEL_EDITOR and event.button == 1:
            # Place obstacle in level editor
            world_x = event.pos[0] + self.camera_x
            world_y = event.pos[1]
            
            # Snap to grid
            grid_size = 40
            world_x = (world_x // grid_size) * grid_size
            world_y = (world_y // grid_size) * grid_size
            
            # Don't place above ground
            if world_y < GROUND_Y:
                height = GROUND_Y - world_y
                if height >= 40:
                    obstacle = Obstacle(world_x, world_y, 40, height, self.editor_selected_type)
                    self.level.obstacles.append(obstacle)
        
        return True
    
    def _handle_menu_button(self, button_text):
        """Handle menu button clicks"""
        if button_text == "START GAME":
            self._start_game()
        elif button_text == "SETTINGS":
            self.state = STATE_SETTINGS
        elif button_text == "LEVEL EDITOR":
            self.state = STATE_LEVEL_EDITOR
        elif button_text == "EXIT":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def _handle_pause_button(self, button_text):
        """Handle pause button clicks"""
        if button_text == "RESUME":
            self.state = STATE_PLAYING
        elif button_text == "RESTART":
            self._restart_game()
        elif button_text == "MAIN MENU":
            self.state = STATE_MENU
    
    def _handle_game_over_button(self, button_text):
        """Handle game over button clicks"""
        if button_text == "RETRY":
            self._restart_game()
        elif button_text == "MAIN MENU":
            self.state = STATE_MENU
    
    def _handle_settings_button(self, button_text):
        """Handle settings button clicks"""
        if button_text == "CHANGE SKIN":
            self.save_manager.skin_index = (self.save_manager.skin_index + 1) % len(PLAYER_SKINS)
            self.player.change_skin(self.save_manager.skin_index)
        elif button_text == "BACK":
            self.state = STATE_MENU
    
    def _handle_editor_button(self, button_text):
        """Handle level editor button clicks"""
        if button_text == "SPIKE":
            self.editor_selected_type = "spike"
        elif button_text == "BLOCK":
            self.editor_selected_type = "block"
        elif button_text == "JUMP PAD":
            self.editor_selected_type = "jump_pad"
        elif button_text == "BACK":
            self.state = STATE_MENU
    
    def _start_game(self):
        """Start/restart the game"""
        self.player = Player(PLAYER_X, GROUND_Y - PLAYER_SIZE, self.save_manager.skin_index)
        self.level = Level()
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.death_flash = 0
    
    def _restart_game(self):
        """Restart current game"""
        self.player.reset()
        self.level.reset()
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.death_flash = 0
    
    def _update_game(self):
        """Update game logic"""
        try:
            dt = self.delta_time

            # Update player
            self.player.update(dt, GROUND_Y)

            # Update camera to follow player
            self.camera_x = self.player.rect.x - PLAYER_X

            # Generate level ahead
            self.level.generate_ahead(self.player.rect.x, SCREEN_WIDTH)

            # Update moving obstacles
            for obstacle in self.level.obstacles:
                obstacle.update(dt)

            # Check collisions (no obstacles in clear level mode)
            # Player can fly freely without collision

            # Emit trail particles
            if self.player.on_ground:
                self.ui_manager.particles.emit_trail_particles(
                    self.player.rect.left,
                    self.player.rect.centery,
                    self.player.color
                )

            # Check level complete
            if self.level.is_complete(self.player.rect.x):
                self._level_complete()

            # Death flash countdown
            if self.death_flash > 0:
                self.death_flash -= self.delta_time * 3
        except Exception as e:
            print(f"ERROR in _update_game: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _player_die(self):
        """Handle player death"""
        self.player.alive = False
        self.sound_manager.play('death')
        self.ui_manager.particles.emit_death_particles(
            self.player.rect.centerx,
            self.player.rect.centery,
            self.player.color
        )
        self.death_flash = 1.0
        
        # Save score
        score = int(self.level.get_progress(self.player.rect.x) * 10)
        self.save_manager.update_score(score)
        
        # Transition to game over after brief delay
        pygame.time.delay(500)
        self.state = STATE_GAME_OVER
    
    def _level_complete(self):
        """Handle level completion"""
        score = 1000  # Max score
        self.save_manager.update_score(score)
        pygame.time.delay(500)
        self.state = STATE_GAME_OVER
    
    def _update_level_editor(self):
        """Update level editor"""
        # Move camera with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_x -= 300 * self.delta_time
        if keys[pygame.K_RIGHT]:
            self.camera_x += 300 * self.delta_time
        
        self.camera_x = max(0, self.camera_x)
        self.ui_manager.background.update(self.delta_time, self.camera_x)
    
    def _draw(self):
        """Draw everything"""
        # Draw background
        self.ui_manager.background.draw(self.screen, self.camera_x)
        
        if self.state == STATE_MENU:
            self.ui_manager.draw_menu(self.screen)
            
        elif self.state == STATE_PLAYING:
            self._draw_game()
            
        elif self.state == STATE_PAUSED:
            self._draw_game()
            self.ui_manager.draw_pause_menu(self.screen)
            
        elif self.state == STATE_GAME_OVER:
            self._draw_game()
            score = self.save_manager.last_score
            best_score = self.save_manager.best_score
            won = score >= 1000
            self.ui_manager.draw_game_over(self.screen, score, best_score, won)
            
        elif self.state == STATE_SETTINGS:
            self.ui_manager.draw_settings(self.screen, self.save_manager.skin_index)
            
        elif self.state == STATE_LEVEL_EDITOR:
            self._draw_level_editor()
        
        # Draw particles (always)
        self.ui_manager.particles.draw(self.screen, self.camera_x)
        
        # Death flash effect
        if self.death_flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(150 * self.death_flash)
            flash_surface.fill((255, 0, 0, alpha))
            self.screen.blit(flash_surface, (0, 0))

        # FPS counter (debug)
        # fps_font = pygame.font.Font(None, 24)
        # fps_text = fps_font.render(f"FPS: {self.fps:.0f}", True, WHITE)
        # self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
    
    def _draw_game(self):
        """Draw game world"""
        # Draw ground
        self.level.draw_ground(self.screen, self.camera_x, SCREEN_WIDTH)
        
        # Draw obstacles
        for obstacle in self.level.obstacles:
            obstacle.draw(self.screen, self.camera_x)
        
        # Draw player (only if alive)
        if self.player.alive:
            self.player.draw(self.screen, self.camera_x)
        
        # Draw HUD
        progress = self.level.get_progress(self.player.rect.x)
        score = int(progress * 10)
        self.ui_manager.draw_hud(self.screen, progress, score, self.save_manager.best_score)
        
        # Finish line
        if self.level.length - self.camera_x < SCREEN_WIDTH:
            finish_x = self.level.length - self.camera_x
            pygame.draw.line(self.screen, NEON_GREEN, 
                           (finish_x, 0), (finish_x, GROUND_Y), 5)
            # Flag
            flag_points = [
                (finish_x, 20),
                (finish_x + 40, 40),
                (finish_x, 60)
            ]
            pygame.draw.polygon(self.screen, NEON_GREEN, flag_points)
    
    def _draw_level_editor(self):
        """Draw level editor"""
        # Draw ground
        self.level.draw_ground(self.screen, self.camera_x, SCREEN_WIDTH)
        
        # Draw grid
        grid_size = 40
        start_x = int(self.camera_x // grid_size) * grid_size
        
        for x in range(start_x, start_x + SCREEN_WIDTH + grid_size, grid_size):
            screen_x = x - self.camera_x
            pygame.draw.line(self.screen, (50, 50, 100), 
                           (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, (50, 50, 100), 
                           (0, y), (SCREEN_WIDTH, y))
        
        # Draw obstacles
        for obstacle in self.level.obstacles:
            obstacle.draw(self.screen, self.camera_x)
        
        # Draw selected type indicator
        font = pygame.font.Font(None, FONT_SIZE_SMALL)
        text = f"Selected: {self.editor_selected_type.upper()}"
        text_surface = font.render(text, True, WHITE)
        self.screen.blit(text_surface, (SCREEN_WIDTH - 250, 20))


# Import Obstacle for level editor
from game.obstacles import Obstacle


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
