import pygame
import time
from enum import Enum
from src.player import Player
from src.zombie import Zombie
from src.resource import Resource
from src.world import World

class GameState(Enum):
    DAY = 1
    NIGHT = 2
    MENU = 3
    GAME_OVER = 4

class Game:
    def __init__(self):
        # Game window settings
        self.width = 1024
        self.height = 768
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Zombie Survival")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        
        # Day/night cycle
        self.day_duration = 60  # seconds
        self.night_duration = 90  # seconds
        self.cycle_timer = 0
        self.day_count = 1
        
        # Game objects
        self.world = World(self.width, self.height)
        self.player = Player(self.width // 2, self.height // 2)
        self.zombies = []
        self.resources = []
        
        # Game stats
        self.score = 0
        self.resources_collected = 0
        
        # Load assets
        self.load_assets()
    
    def load_assets(self):
        # Placeholder for loading images, sounds, etc.
        # In a real implementation, you would load your assets here
        pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle menu and game over state key presses
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU and event.key == pygame.K_SPACE:
                    self.state = GameState.DAY
                    self.prepare_day()
                elif self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                    self.reset_game()
            
            # Handle player input (only when playing)
            if self.state == GameState.DAY or self.state == GameState.NIGHT:
                self.player.handle_event(event)
    
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
    
    def update_day(self):
        # Update player
        self.player.update()
        
        # Update resources
        for resource in self.resources[:]:
            resource.update()
            # Check if player collected resource
            if resource.rect.colliderect(self.player.rect):
                self.resources.remove(resource)
                self.resources_collected += 1
        
        # Spawn new resources occasionally
        if len(self.resources) < 5 and pygame.time.get_ticks() % 1000 < 20:
            self.resources.append(Resource.random_resource(self.width, self.height))
        
        # Check if day is over
        self.cycle_timer += 1 / self.fps
        if self.cycle_timer >= self.day_duration:
            self.cycle_timer = 0
            self.state = GameState.NIGHT
            self.prepare_night()
    
    def update_night(self):
        # Update player
        self.player.update()
        
        # Update zombies
        for zombie in self.zombies[:]:
            zombie.update(self.player)
            # Check if player hit zombie
            if self.player.check_bullet_hits(zombie):
                self.zombies.remove(zombie)
                self.score += 10
            # Check if zombie hit player
            elif zombie.rect.colliderect(self.player.rect):
                self.player.take_damage(zombie.damage)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
        
        # Spawn new zombies based on difficulty (day count)
        if len(self.zombies) < 5 + self.day_count and pygame.time.get_ticks() % 2000 < 20:
            self.zombies.append(Zombie.spawn_zombie(self.width, self.height))
        
        # Check if night is over
        self.cycle_timer += 1 / self.fps
        if self.cycle_timer >= self.night_duration:
            self.cycle_timer = 0
            self.state = GameState.DAY
            self.prepare_day()
    
    def update_menu(self):
        # Menu logic - nothing to update in this simple implementation
        pass
    
    def update_game_over(self):
        # Game over logic - nothing to update in this simple implementation
        pass
    
    def reset_game(self):
        # Reset game state for a new game
        self.state = GameState.DAY
        self.cycle_timer = 0
        self.day_count = 1
        self.score = 0
        self.resources_collected = 0
        
        # Reset player
        self.player = Player(self.width // 2, self.height // 2)
        
        # Clear entities
        self.zombies.clear()
        self.resources.clear()
    
    def prepare_day(self):
        # Clear zombies
        self.zombies.clear()
        # Heal player slightly
        self.player.health = min(100, self.player.health + 20)
        # Increment day count
        self.day_count += 1
    
    def prepare_night(self):
        # Clear resources
        self.resources.clear()
        # Player prepares defenses
        self.player.reload()
    
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
        
        # Update display
        pygame.display.flip()
    
    def render_day(self):
        # Draw sky background (blue)
        self.screen.fill((135, 206, 235))
        
        # Draw world
        self.world.render(self.screen)
        
        # Draw resources
        for resource in self.resources:
            resource.render(self.screen)
        
        # Draw player
        self.player.render(self.screen)
        
        # Draw UI
        self.render_ui()
    
    def render_night(self):
        # Draw night background (dark blue)
        self.screen.fill((25, 25, 50))
        
        # Draw world
        self.world.render(self.screen)
        
        # Draw zombies
        for zombie in self.zombies:
            zombie.render(self.screen)
        
        # Draw player
        self.player.render(self.screen)
        
        # Draw UI
        self.render_ui()
    
    def render_menu(self):
        # Draw menu
        font = pygame.font.SysFont(None, 72)
        title = font.render("Zombie Survival", True, (255, 255, 255))
        start = font.render("Press SPACE to Start", True, (255, 255, 255))
        
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 3))
        self.screen.blit(start, (self.width // 2 - start.get_width() // 2, self.height // 2))
    
    def render_game_over(self):
        # Draw game over screen
        font = pygame.font.SysFont(None, 72)
        game_over = font.render("GAME OVER", True, (255, 0, 0))
        score = font.render(f"Score: {self.score}", True, (255, 255, 255))
        restart = font.render("Press R to Restart", True, (255, 255, 255))
        
        self.screen.blit(game_over, (self.width // 2 - game_over.get_width() // 2, self.height // 3))
        self.screen.blit(score, (self.width // 2 - score.get_width() // 2, self.height // 2))
        self.screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 100))
    
    def render_ui(self):
        # Draw UI elements like health, ammo, day/night indicator
        font = pygame.font.SysFont(None, 36)
        
        # Health bar
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, self.player.health * 2, 20))
        
        # Day/Night indicator
        if self.state == GameState.DAY:
            time_text = font.render(f"Day {self.day_count} - {int(self.day_duration - self.cycle_timer)}s until night", True, (0, 0, 0))
        else:
            time_text = font.render(f"Night {self.day_count} - {int(self.night_duration - self.cycle_timer)}s until day", True, (255, 255, 255))
        
        self.screen.blit(time_text, (20, 50))
        
        # Score and resources
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        resources_text = font.render(f"Resources: {self.resources_collected}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (self.width - score_text.get_width() - 20, 20))
        self.screen.blit(resources_text, (self.width - resources_text.get_width() - 20, 60))
    
    def run(self):
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
