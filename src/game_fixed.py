import pygame
import time
import random
import math
import os
from enum import Enum
from src.player import Player
from src.zombie import Zombie
from src.world import World
from src.barricade import Barricade
from src.camera import Camera
from src.shop import Shop
from src.leaderboard import Leaderboard
from src.crosshair import Crosshair

class GameState(Enum):
    MENU = 0
    DAY = 1
    NIGHT = 2
    SHOP = 3
    GAME_OVER = 4
    LEADERBOARD = 5
    NAME_ENTRY = 6  # New state for entering name for leaderboard

class Game:
    def __init__(self):
        # Game window settings
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Zombie Survival")
        
        # Initialize sound mixer
        pygame.mixer.init()
        
        # Music settings
        self.music_enabled = True
        self.music_volume = 0.5  # 50% volume
        
        # Load music
        self.load_music()
        
        # Current music track
        self.current_music = None
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        
        # Game cycle settings
        self.day_count = 1
        self.day_duration = 60  # seconds
        self.night_duration = 90  # seconds
        self.cycle_timer = 0
        
        # Resources
        self.resources = 0
        
        # Game objects
        self.world = World(self.width, self.height)
        self.player = Player(self.width // 2, self.height - 200)
        self.zombies = []
        self.barricade = Barricade(200, self.height - 200, 30, 200)
        self.explosions = []
        
        # Camera system
        self.camera = Camera(self.width, self.height, self.world.width)
        
        # Custom crosshair
        self.crosshair = Crosshair()
        
        # Shop system
        self.shop = Shop(self.width, self.height)
        
        # Leaderboard system
        self.leaderboard = Leaderboard()
        self.player_name = ""
        self.name_entry_active = False
        self.name_entry_cursor_visible = True
        self.name_entry_cursor_timer = 0
        
        # Game stats
        self.score = 0
        self.zombies_killed = 0
        
        # Night phase variables
        self.max_zombies_tonight = 10
        self.zombies_spawned_tonight = 0
        self.zombies_cleared_timer = 0
        
        # Load assets
        self.load_assets()
    def load_assets(self):
        # Load game assets
        # In a real implementation, you would load more assets here
    
    def load_music(self):
        """Load music files for different game states"""
        self.music = {
            "menu": os.path.join("assets", "music", "menu_music.mp3"),
            "day": os.path.join("assets", "music", "day_music.mp3"),
            "night": os.path.join("assets", "music", "night_music.mp3"),
            "shop": os.path.join("assets", "music", "shop_music.mp3"),
            "game_over": os.path.join("assets", "music", "game_over_music.mp3")
        }
        
        # Create placeholder music files if they don't exist
        music_dir = os.path.join("assets", "music")
        os.makedirs(music_dir, exist_ok=True)
        
        # Note: In a real implementation, you would include actual music files
        # For this example, we'll create placeholder text files to indicate where music should go
        for music_name, music_path in self.music.items():
            if not os.path.exists(music_path):
                with open(f"{music_path}.txt", "w") as f:
                    f.write(f"Place {music_name} music file here and rename to {os.path.basename(music_path)}")
    
    def play_music(self, music_key, loops=-1):
        """Play music for the specified game state"""
        if not self.music_enabled:
            return
            
        if self.current_music != music_key:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.music[music_key])
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = music_key
            except pygame.error:
                print(f"Could not load music: {self.music[music_key]}")
                # Try to load a placeholder if available
                try:
                    placeholder_path = os.path.join("assets", "music", "placeholder.mp3")
                    if os.path.exists(placeholder_path):
                        pygame.mixer.music.load(placeholder_path)
                        pygame.mixer.music.set_volume(self.music_volume)
                        pygame.mixer.music.play(loops)
                except:
                    print("Could not load placeholder music either")
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            # Resume music if it was playing before
            if self.current_music:
                self.play_music(self.current_music)
        else:
            # Stop music
            pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Global keyboard controls
            if event.type == pygame.KEYDOWN:
                # Toggle music with M key
                if event.key == pygame.K_m:
                    self.toggle_music()
                # Increase volume with + key
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.set_music_volume(self.music_volume + 0.1)
                # Decrease volume with - key
                elif event.key == pygame.K_MINUS:
                    self.set_music_volume(self.music_volume - 0.1)
            
            # Handle name entry state
            if self.state == GameState.NAME_ENTRY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(self.player_name) > 0:
                        # Save score and go to game over screen
                        position = self.leaderboard.add_score(
                            self.player_name, 
                            self.score, 
                            self.day_count, 
                            self.zombies_killed
                        )
                        self.state = GameState.GAME_OVER
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.unicode.isalnum() and len(self.player_name) < 15:
                        self.player_name += event.unicode
                continue
            
            # Handle menu and game over state key presses
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU and event.key == pygame.K_SPACE:
                    self.state = GameState.DAY
                    self.prepare_day()
                elif self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                    self.reset_game()
                # Skip to next phase with N key
                elif self.state == GameState.DAY and event.key == pygame.K_n:
                    self.cycle_timer = self.day_duration  # Force day to end
                elif self.state == GameState.NIGHT and event.key == pygame.K_n:
                    self.cycle_timer = self.night_duration  # Force night to end
            
            # Handle shop events
            if self.state == GameState.SHOP:
                if self.shop.handle_event(event):
                    continue  # Event was handled by shop
            
            # Handle player input (only when playing)
            if self.state == GameState.DAY or self.state == GameState.NIGHT:
                result = self.player.handle_event(event)
                if result == "shooting_started":
                    # Player started shooting, update crosshair
                    self.crosshair.on_shoot()
    
    def update(self):
        # Update game state based on current state
        if self.state == GameState.DAY:
            self.update_day()
        elif self.state == GameState.NIGHT:
            self.update_night()
        elif self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.GAME_OVER:
            self.update_game_over()
        elif self.state == GameState.SHOP:
            self.update_shop()
        elif self.state == GameState.NAME_ENTRY:
            self.update_name_entry()
            
        # Update crosshair only during day and night phases
        if self.state == GameState.DAY or self.state == GameState.NIGHT:
            mouse_pos = pygame.mouse.get_pos()
            player_pos = (self.player.rect.centerx, self.player.rect.centery)
            
            # Calculate distance for accuracy
            dx = mouse_pos[0] - player_pos[0]
            dy = mouse_pos[1] - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Update crosshair with position
            self.crosshair.update(player_pos, mouse_pos)
            
            # Set color based on current weapon
            self.crosshair.set_color_for_weapon(self.player.current_weapon)
    
    def update_name_entry(self):
        """Update name entry screen"""
        # Blink cursor
        self.name_entry_cursor_timer += 1
        if self.name_entry_cursor_timer > 30:  # Toggle every half second
            self.name_entry_cursor_visible = not self.name_entry_cursor_visible
            self.name_entry_cursor_timer = 0
    def update_day(self):
        # Play daytime music
        self.play_music("day")
        
        # Update world
        self.world.update()
        
        # Update player
        self.player.update()
        
        # Update camera to follow player
        self.camera.update(self.player.rect)
        
        # Update cycle timer
        self.cycle_timer += 1/60  # Assuming 60 FPS
        
        # Check if day is over
        if self.cycle_timer >= self.day_duration:
            self.state = GameState.SHOP
            self.shop.open(self.player, self.barricade, self.resources)
    
    def update_night(self):
        # Play nighttime music
        self.play_music("night")
        
        # Allow player movement if barricade is destroyed
        if self.barricade.is_destroyed():
            self.player.update()
        
        # Update zombies
        for zombie in list(self.zombies):
            zombie.update(self.player, self.barricade)
            
            # Check if zombie reached barricade
            if not self.barricade.is_destroyed() and zombie.rect.colliderect(self.barricade.rect):
                zombie.attack_barricade(self.barricade)
            
            # Check if zombie reached player
            if zombie.rect.colliderect(self.player.rect):
                zombie.attack_player(self.player)
            
            # Check if zombie is dead
            if zombie.health <= 0:
                self.zombies.remove(zombie)
                self.zombies_killed += 1
                self.score += 10
                self.resources += random.randint(1, 3)
        
        # Update player bullets
        self.player.update_bullets(self.zombies)
        
        # Update explosions
        for explosion in list(self.explosions):
            explosion["timer"] -= 1
            if explosion["timer"] <= 0:
                self.explosions.remove(explosion)
        
        # Spawn zombies
        if len(self.zombies) < 5 and self.zombies_spawned_tonight < self.max_zombies_tonight:
            # Spawn from right side of screen
            x = self.width + 50
            y = self.height - 100
            zombie = Zombie(x, y)
            self.zombies.append(zombie)
            self.zombies_spawned_tonight += 1
        
        # Update cycle timer
        self.cycle_timer += 1/60  # Assuming 60 FPS
        
        # Check if all zombies are cleared
        if len(self.zombies) == 0 and self.zombies_spawned_tonight >= self.max_zombies_tonight:
            self.zombies_cleared_timer += 1/60  # Assuming 60 FPS
            if self.zombies_cleared_timer >= 5:  # 5 second delay after clearing
                self.cycle_timer = self.night_duration  # Force night to end
        
        # Check if night is over
        if self.cycle_timer >= self.night_duration:
            self.state = GameState.DAY
            self.day_count += 1
            self.prepare_day()
    def update_menu(self):
        # Play menu music
        self.play_music("menu")
        
        # Simple menu animation could go here
        pass
    
    def update_game_over(self):
        # Play game over music
        self.play_music("game_over")
        
        # Game over screen animations could go here
        pass
    
    def update_shop(self):
        # Play shop music
        self.play_music("shop")
        
        # Update shop state
        if not self.shop.active:
            # Shop was closed, go to night phase
            self.resources = self.shop.close()
            self.state = GameState.NIGHT
            self.prepare_night()
    
    def prepare_day(self):
        """Setup for day phase"""
        self.cycle_timer = 0
        self.player.reset_position(self.width // 2, self.height - 200)
        
        # Scale difficulty based on day count
        self.day_duration = max(30, 60 - (self.day_count * 2))  # Days get shorter
    
    def prepare_night(self):
        """Setup for night phase"""
        self.cycle_timer = 0
        self.zombies = []
        self.zombies_spawned_tonight = 0
        self.zombies_cleared_timer = 0
        
        # Scale difficulty based on day count
        self.max_zombies_tonight = 10 + (self.day_count * 5)  # More zombies each night
        self.night_duration = max(60, 90 + (self.day_count * 5))  # Nights get longer
        
        # Reset player position for night defense
        self.player.reset_position(self.width // 2, self.height - 200)
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.state = GameState.MENU
        self.day_count = 1
        self.score = 0
        self.zombies_killed = 0
        self.resources = 0
        self.player = Player(self.width // 2, self.height - 200)
        self.barricade = Barricade(200, self.height - 200, 30, 200)
        self.zombies = []
        self.prepare_day()
    def render(self):
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render based on game state
        if self.state == GameState.DAY:
            self.render_day()
        elif self.state == GameState.NIGHT:
            self.render_night()
        elif self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state == GameState.SHOP:
            self.render_shop()
        elif self.state == GameState.NAME_ENTRY:
            self.render_name_entry()
        
        # Render crosshair (only during day and night gameplay)
        if self.state == GameState.DAY or self.state == GameState.NIGHT:
            pygame.mouse.set_visible(False)  # Hide default cursor
            self.crosshair.render(self.screen)
        else:
            pygame.mouse.set_visible(True)  # Show default cursor
        
        # Update display
        pygame.display.flip()
    
    def render_name_entry(self):
        """Render the name entry screen"""
        # Background
        self.screen.fill((0, 0, 50))
        
        # Title
        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 48)
        font_small = pygame.font.SysFont(None, 36)
        
        title_text = font_large.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))
        
        # Score display
        score_text = font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 200))
        
        day_text = font_medium.render(f"Survived to day: {self.day_count}", True, (255, 255, 255))
        self.screen.blit(day_text, (self.width // 2 - day_text.get_width() // 2, 250))
        
        zombies_text = font_medium.render(f"Zombies killed: {self.zombies_killed}", True, (255, 255, 255))
        self.screen.blit(zombies_text, (self.width // 2 - zombies_text.get_width() // 2, 300))
        
        # Name entry
        name_prompt = font_medium.render("Enter your name:", True, (255, 255, 255))
        self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 400))
        
        # Name input box
        name_box_rect = pygame.Rect(self.width // 2 - 150, 450, 300, 50)
        pygame.draw.rect(self.screen, (100, 100, 100), name_box_rect, 2)
        
        # Display entered name
        name_text = font_medium.render(self.player_name, True, (255, 255, 255))
        self.screen.blit(name_text, (name_box_rect.x + 10, name_box_rect.y + 10))
        
        # Blinking cursor
        if self.name_entry_cursor_visible:
            cursor_x = name_box_rect.x + 10 + name_text.get_width()
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (cursor_x, name_box_rect.y + 10),
                (cursor_x, name_box_rect.y + 40),
                2
            )
        
        # Instructions
        instructions_text = font_small.render("Press ENTER when done", True, (200, 200, 200))
        self.screen.blit(instructions_text, (self.width // 2 - instructions_text.get_width() // 2, 520))
    def render_game_over(self):
        """Render the game over screen"""
        # Background
        self.screen.fill((0, 0, 50))
        
        # Title
        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 48)
        font_small = pygame.font.SysFont(None, 36)
        
        title_text = font_large.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 100))
        
        # Score display
        score_text = font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 200))
        
        day_text = font_medium.render(f"Survived to day: {self.day_count}", True, (255, 255, 255))
        self.screen.blit(day_text, (self.width // 2 - day_text.get_width() // 2, 250))
        
        zombies_text = font_medium.render(f"Zombies killed: {self.zombies_killed}", True, (255, 255, 255))
        self.screen.blit(zombies_text, (self.width // 2 - zombies_text.get_width() // 2, 300))
        
        # Leaderboard
        leaderboard_title = font_medium.render("TOP SCORES", True, (255, 255, 255))
        self.screen.blit(leaderboard_title, (self.width // 2 - leaderboard_title.get_width() // 2, 350))
        
        # Display top 3 scores
        top_scores = self.leaderboard.get_top_scores(3)
        y_pos = 400
        
        if not top_scores:
            no_scores_text = font_small.render("No scores yet", True, (200, 200, 200))
            self.screen.blit(no_scores_text, (self.width // 2 - no_scores_text.get_width() // 2, y_pos))
        else:
            for i, entry in enumerate(top_scores):
                score_line = font_small.render(
                    f"{i+1}. {entry['name']} - {entry['score']} pts - Day {entry['day_count']}", 
                    True, 
                    (255, 255, 0) if i == 0 else (255, 255, 255)
                )
                self.screen.blit(score_line, (self.width // 2 - score_line.get_width() // 2, y_pos))
                y_pos += 40
        
        # Restart prompt
        restart_text = font_medium.render("Press R to restart", True, (255, 255, 255))
        self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height - 100))
    
    def render_menu(self):
        """Render the menu screen"""
        # Background
        self.screen.fill((0, 0, 50))
        
        # Title
        font_large = pygame.font.SysFont(None, 96)
        font_medium = pygame.font.SysFont(None, 48)
        font_small = pygame.font.SysFont(None, 36)
        
        title_text = font_large.render("ZOMBIE SURVIVAL", True, (255, 0, 0))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 150))
        
        # Start prompt
        start_text = font_medium.render("Press SPACE to start", True, (255, 255, 255))
        self.screen.blit(start_text, (self.width // 2 - start_text.get_width() // 2, 300))
        
        # Instructions
        instructions = [
            "Collect resources during the day",
            "Defend your barricade at night",
            "Buy upgrades in the shop",
            "Survive as long as possible"
        ]
        
        y_pos = 400
        for instruction in instructions:
            instruction_text = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(instruction_text, (self.width // 2 - instruction_text.get_width() // 2, y_pos))
            y_pos += 40
        
        # Show leaderboard
        leaderboard_title = font_medium.render("TOP SCORES", True, (255, 255, 255))
        self.screen.blit(leaderboard_title, (self.width // 2 - leaderboard_title.get_width() // 2, 400))
        
        # Display top 3 scores
        top_scores = self.leaderboard.get_top_scores(3)
        y_pos = 450
        font_small = pygame.font.SysFont(None, 36)
        
        if not top_scores:
            no_scores_text = font_small.render("No scores yet", True, (200, 200, 200))
            self.screen.blit(no_scores_text, (self.width // 2 - no_scores_text.get_width() // 2, y_pos))
        else:
            for i, entry in enumerate(top_scores):
                score_line = font_small.render(
                    f"{i+1}. {entry['name']} - {entry['score']} pts - Day {entry['day_count']}", 
                    True, 
                    (255, 255, 0) if i == 0 else (255, 255, 255)
                )
                self.screen.blit(score_line, (self.width // 2 - score_line.get_width() // 2, y_pos))
                y_pos += 40
    def render_day(self):
        """Render the day phase"""
        # Sky background
        self.screen.fill((135, 206, 235))
        
        # Render world with camera offset
        self.world.render(self.screen, self.camera)
        
        # Render player with camera offset
        self.player.render(self.screen, self.camera)
        
        # UI elements
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        # Left side UI - Player stats
        # Health bar
        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (20, 20))
        
        # Day indicator
        time_text = font.render(f"Day {self.day_count} - {int(self.day_duration - self.cycle_timer)}s until night", True, (0, 0, 0))
        self.screen.blit(time_text, (20, 60))
        
        # Resources
        resources_text = font.render(f"Resources: {self.resources}", True, (255, 255, 255))
        self.screen.blit(resources_text, (20, 100))
        
        # Right side UI - Weapon info
        # Ammo counter
        ammo_text = font.render(f"Ammo: {self.player.magazine_current}/{self.player.ammo_total}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (self.width - ammo_text.get_width() - 20, 20))
        
        # Weapon type
        weapon_text = font.render(f"Weapon: {self.player.current_weapon.capitalize()}", True, (255, 255, 255))
        self.screen.blit(weapon_text, (self.width - weapon_text.get_width() - 20, 60))
        
        # Bottom UI
        # Skip button
        skip_text = small_font.render("Press N to skip to shop", True, (100, 100, 100))
        self.screen.blit(skip_text, (20, self.height - 60))
        
        # Music controls
        music_status = "ON" if self.music_enabled else "OFF"
        music_text = small_font.render(f"Music: {music_status} (M to toggle, +/- volume)", True, (200, 200, 200))
        self.screen.blit(music_text, (self.width - music_text.get_width() - 20, self.height - 30))
    
    def render_night(self):
        """Render the night phase"""
        # Dark background
        self.screen.fill((20, 20, 40))
        
        # Render world (no camera during night)
        self.world.render_night(self.screen)
        
        # Render barricade
        self.barricade.render(self.screen)
        
        # Render zombies
        for zombie in self.zombies:
            zombie.render(self.screen)
        
        # Render player (fixed position during night)
        self.player.render(self.screen)
        
        # Render explosions
        for explosion in self.explosions:
            pygame.draw.circle(
                self.screen, 
                (255, 165, 0, 128), 
                (int(explosion["x"]), int(explosion["y"])), 
                explosion["radius"],
                3
            )
        
        # UI elements
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        # Left side UI - Player stats
        # Health bar
        health_text = font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (20, 20))
        
        # Night indicator
        time_text = font.render(f"Night {self.day_count} - {int(self.night_duration - self.cycle_timer)}s until day", True, (255, 255, 255))
        self.screen.blit(time_text, (20, 60))
        
        # Resources
        resources_text = font.render(f"Resources: {self.resources}", True, (255, 255, 255))
        self.screen.blit(resources_text, (20, 100))
        
        # Zombies remaining
        zombies_remaining = self.max_zombies_tonight - self.zombies_spawned_tonight + len(self.zombies)
        zombies_text = font.render(f"Zombies remaining: {max(0, zombies_remaining)}", True, (255, 200, 200))
        self.screen.blit(zombies_text, (20, 140))
        
        # Right side UI - Weapon and barricade info
        # Ammo counter - positioned below player
        ammo_text = font.render(f"Ammo: {self.player.magazine_current}/{self.player.ammo_total}", True, (255, 255, 255))
        self.screen.blit(ammo_text, (self.width // 2 - ammo_text.get_width() // 2, self.height - 60))
        
        # Weapon type
        weapon_text = font.render(f"Weapon: {self.player.current_weapon.capitalize()}", True, (255, 255, 255))
        self.screen.blit(weapon_text, (self.width // 2 - weapon_text.get_width() // 2, self.height - 100))
        
        # Barricade health - positioned above barricade
        barricade_health = int(self.barricade.health / self.barricade.max_health * 100)
        barricade_text = font.render(f"Barricade: {barricade_health}%", True, (255, 255, 255))
        
        # Position above the barricade
        barricade_x = self.barricade.x + self.barricade.width // 2
        barricade_y = self.barricade.y - 40
        self.screen.blit(barricade_text, (barricade_x - barricade_text.get_width() // 2, barricade_y))
        
        # Show countdown if all zombies are killed
        if len(self.zombies) == 0 and self.zombies_spawned_tonight >= self.max_zombies_tonight:
            countdown_text = font.render(f"Night ending in: {int(5 - self.zombies_cleared_timer)}s", True, (0, 255, 0))
            self.screen.blit(countdown_text, (self.width // 2 - countdown_text.get_width() // 2, 20))
        
        # Bottom UI
        # Skip button
        skip_text = small_font.render("Press N to skip to day", True, (150, 150, 150))
        self.screen.blit(skip_text, (20, self.height - 30))
        
        # Music controls
        music_status = "ON" if self.music_enabled else "OFF"
        music_text = small_font.render(f"Music: {music_status} (M to toggle, +/- volume)", True, (200, 200, 200))
        self.screen.blit(music_text, (self.width - music_text.get_width() - 20, self.height - 30))
        
        # Difficulty indicator
        difficulty_color = (0, 255, 0)  # Green for easy
        if self.day_count <= 3:
            difficulty_text = "Easy"
        elif self.day_count <= 6:
            difficulty_text = "Medium"
            difficulty_color = (255, 255, 0)  # Yellow
        elif self.day_count <= 9:
            difficulty_text = "Hard"
            difficulty_color = (255, 165, 0)  # Orange
        else:
            difficulty_text = "Nightmare"
            difficulty_color = (255, 0, 0)  # Red
    def render_shop(self):
        """Render the shop screen"""
        self.shop.render(self.screen)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Render game
            self.render()
            
            # Cap the frame rate
            self.clock.tick(self.fps)
        
        # Clean up
        pygame.quit()
