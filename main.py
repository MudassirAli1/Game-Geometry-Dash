import pygame
import sys
import json
import os
import asyncio

from game.settings import *
from game.player import Player
from game.obstacles import Level
from game.ui import UIManager


class SaveManager:
    """Saves and loads your best score."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {"best_score": 0, "last_score": 0, "skin_index": 0}
        self.load()

    def load(self):
        """Load save data from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.data.update(json.load(f))
            except:
                pass

    def save(self):
        """Save data to file."""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

    def update_score(self, score):
        """Update score and check if new best."""
        self.data["last_score"] = score
        if score > self.data["best_score"]:
            self.data["best_score"] = score
            self.save()
            return True
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
    """Makes simple sound effects."""

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._generate_sounds()

    def _generate_sounds(self):
        """Generate simple beep sounds."""
        try:
            self.sounds['jump'] = self._make_tone(440, 660, 0.15)
            self.sounds['death'] = self._make_tone(440, 220, 0.2)
            self.sounds['jump_pad'] = self._make_tone(550, 880, 0.1)
        except Exception as e:
            print(f"Sound error: {e}")
            self.enabled = False

    def play(self, sound_name):
        """Play a sound."""
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except:
                pass

    def _make_tone(self, start_freq, end_freq, duration):
        """Create a simple tone."""
        import struct
        import math
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buffer = bytearray(n_samples * 2)

        for i in range(n_samples):
            t = i / sample_rate
            progress = i / n_samples
            freq = start_freq + (end_freq - start_freq) * progress
            value = int(10000 * math.sin(2 * math.pi * freq * t))
            value = max(-32768, min(32767, value))
            struct.pack_into('<h', buffer, i * 2, value)

        return pygame.mixer.Sound(buffer=buffer)


class Game:
    """Main game class - keeps everything running."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # SCALED | RESIZABLE is the best combination for browser games
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.delta_time = 0

        self.state = STATE_MENU
        self.camera_x = 0

        self.save_manager = SaveManager(SAVE_FILE)
        self.sound_manager = SoundManager()
        self.ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player = Player(PLAYER_X, GROUND_Y - PLAYER_SIZE, self.save_manager.skin_index)
        self.level = Level()
        self.death_flash = 0

    async def run(self):
        """Main game loop - runs forever."""
        running = True

        while running:
            self.delta_time = self.clock.tick(FPS) / 1000.0
            self.delta_time = max(MIN_DELTA, min(MAX_DELTA, self.delta_time))

            running = self._handle_events()
            self._update()
            self._draw()

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handle all button presses and clicks."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Unified Input Logic for Jumping
            if self.state == STATE_PLAYING:
                jump_started = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_UP]:
                        jump_started = True
                        self.player.is_holding_jump = True
                
                elif event.type == pygame.KEYUP:
                    if event.key in [pygame.K_SPACE, pygame.K_UP]:
                        self.player.is_holding_jump = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Ignore touch-emulated mouse events
                    if not hasattr(event, 'touch') or not event.touch:
                        jump_started = True
                        self.player.is_holding_jump = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if not hasattr(event, 'touch') or not event.touch:
                        self.player.is_holding_jump = False

                elif event.type == pygame.FINGERDOWN:
                    jump_started = True
                    self.player.is_holding_jump = True
                
                elif event.type == pygame.FINGERUP:
                    self.player.is_holding_jump = False

                if jump_started:
                    if self.player.jump():
                        self.sound_manager.play('jump')
                        self.ui_manager.particles.emit_jump_particles(self.player.rect.centerx, self.player.rect.bottom, self.player.color)

            # UI Event Handling
            if self.state == STATE_MENU:
                result = self.ui_manager.handle_event(event, self.ui_manager.menu_buttons)
                if result == "START GAME":
                    self._start_game()
                elif result == "SETTINGS":
                    self.state = STATE_SETTINGS
                elif result == "EXIT":
                    return False

            elif self.state == STATE_PAUSED:
                result = self.ui_manager.handle_event(event, self.ui_manager.pause_buttons)
                if result == "RESUME":
                    self.state = STATE_PLAYING
                elif result == "RESTART":
                    self._restart_game()
                elif result == "MAIN MENU":
                    self.state = STATE_MENU

            elif self.state == STATE_GAME_OVER:
                result = self.ui_manager.handle_event(event, self.ui_manager.game_over_buttons)
                if result == "RETRY":
                    self._restart_game()
                elif result == "MAIN MENU":
                    self.state = STATE_MENU

            elif self.state == STATE_SETTINGS:
                result = self.ui_manager.handle_event(event, self.ui_manager.settings_buttons)
                if result == "CHANGE SKIN":
                    self.save_manager.skin_index = (self.save_manager.skin_index + 1) % len(PLAYER_SKINS)
                    self.player.change_skin(self.save_manager.skin_index)
                elif result == "BACK":
                    self.state = STATE_MENU

            # Global Shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING
                elif event.key == pygame.K_r:
                    if self.state in [STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER]:
                        self._restart_game()

        return True

    def _update(self):
        """Update game logic."""
        self.ui_manager.particles.update(self.delta_time)

        if self.state == STATE_MENU or self.state == STATE_SETTINGS:
            self.ui_manager.background.update(self.delta_time, self.camera_x)

        if self.state == STATE_PLAYING:
            self.player.update(self.delta_time, GROUND_Y)
            self.camera_x = self.player.rect.x - PLAYER_X
            self.level.generate_ahead(self.player.rect.x, SCREEN_WIDTH)
            for obstacle in self.level.obstacles:
                obstacle.update(self.delta_time)

            if self.player.alive:
                collision_type, obstacle = self.level.check_collisions(self.player.get_collision_rects())
                if collision_type == "collision":
                    self._player_die()
                elif collision_type == "jump_pad":
                    self.player.velocity_y = JUMP_FORCE * 1.3
                    self.sound_manager.play('jump_pad')

            if self.player.on_ground and self.player.alive:
                self.ui_manager.particles.emit_trail_particles(self.player.rect.left, self.player.rect.centery, self.player.color)

            if self.level.is_complete(self.player.rect.x):
                self._level_complete()

        if self.death_flash > 0:
            self.death_flash -= self.delta_time * 3

    def _player_die(self):
        self.player.alive = False
        self.sound_manager.play('death')
        self.ui_manager.particles.emit_death_particles(self.player.rect.centerx, self.player.rect.centery, self.player.color)
        self.death_flash = 1.0
        score = int(self.level.get_progress(self.player.rect.x) * 10)
        self.save_manager.update_score(score)
        self.state = STATE_GAME_OVER

    def _level_complete(self):
        score = 1000
        self.save_manager.update_score(score)
        self.state = STATE_GAME_OVER

    def _start_game(self):
        self.player = Player(PLAYER_X, GROUND_Y - PLAYER_SIZE, self.save_manager.skin_index)
        self.level = Level()
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.death_flash = 0

    def _restart_game(self):
        self.player.reset()
        self.level.reset()
        self.camera_x = 0
        self.state = STATE_PLAYING
        self.death_flash = 0

    def _draw(self):
        """Draw everything on screen."""
        self.ui_manager.background.draw(self.screen, self.camera_x)

        if self.state == STATE_MENU:
            self.ui_manager.draw_menu(self.screen)
        elif self.state == STATE_SETTINGS:
            self.ui_manager.draw_settings(self.screen, self.save_manager.skin_index)
        elif self.state in [STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER]:
            self._draw_game()
            if self.state == STATE_PAUSED:
                self.ui_manager.draw_pause_menu(self.screen)
            elif self.state == STATE_GAME_OVER:
                self.ui_manager.draw_game_over(self.screen, int(self.level.get_progress(self.player.rect.x) * 10), self.save_manager.best_score)

        self.ui_manager.particles.draw(self.screen, self.camera_x)

        if self.death_flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(150 * self.death_flash)
            flash_surface.fill((255, 0, 0, alpha))
            self.screen.blit(flash_surface, (0, 0))

    def _draw_game(self):
        self.level.draw_ground(self.screen, self.camera_x, SCREEN_WIDTH)
        for obstacle in self.level.obstacles:
            obstacle.draw(self.screen, self.camera_x)
        if self.player.alive:
            self.player.draw(self.screen, self.camera_x)
        progress = self.level.get_progress(self.player.rect.x)
        self.ui_manager.draw_hud(self.screen, progress, int(progress * 10), self.save_manager.best_score)

        if self.level.length - self.camera_x < SCREEN_WIDTH:
            finish_x = self.level.length - self.camera_x
            pygame.draw.line(self.screen, NEON_GREEN, (finish_x, 0), (finish_x, GROUND_Y), 5)


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
