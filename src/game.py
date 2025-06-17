import pygame
import time
import random
import math
from enum import Enum
from src.player import Player
from src.zombie import Zombie
from src.world import World
from src.barricade import Barricade
from src.camera import Camera
from src.shop import Shop

class GameState(Enum):
    DAY = 1
    NIGHT = 2
    MENU = 3
    GAME_OVER = 4
    SHOP = 5

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
        self.player = Player(self.width // 2, self.height - 200)
        self.zombies = []
        self.barricade = Barricade(200, self.height - 200, 30, 200)
        self.explosions = []
        
        # Camera system
        self.camera = Camera(self.width, self.height, self.world.width)
        
        # Shop system
        self.shop = Shop(self.width, self.height)
        
        # Game stats
        self.score = 0
        self.resources = 0  # Currency for shop
        self.resources_collected = 0  # Counter for collected resources
        self.zombies_killed = 0
        
        # Zombie spawn tracking
        self.zombies_spawned_tonight = 0
        self.max_zombies_tonight = 20
        
        # Load assets
        self.load_assets()
    
    def load_assets(self):
        # Initialize pygame modules
        pygame.font.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # In a real implementation, you would load more assets here
    
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
        elif self.state == GameState.SHOP:
            self.update_shop()
    
    def update_day(self):
        # Update world
        self.world.update()
        
        # Update player with world collision
        self.player.update(self.world)
        
        # Update camera to follow player
        self.camera.update(self.player.rect.centerx)
        
        # Track resources collected
        collected_count = sum(1 for resource in self.world.resources if resource.collected)
        
        # Add resources for newly collected items
        new_collected = collected_count - self.resources_collected
        if new_collected > 0:
            self.resources += new_collected * 5  # Each resource is worth 5 currency
            self.resources_collected = collected_count
        
        # Check if day is over
        self.cycle_timer += 1 / self.fps
        if self.cycle_timer >= self.day_duration:
            self.cycle_timer = 0
            self.state = GameState.SHOP  # Go to shop before night
            self.shop.open(self.player, self.barricade, self.resources)
    
    def update_night(self):
        # Position player behind barricade
        self.player.rect.x = 100
        self.player.rect.y = self.height - self.world.ground_height - self.player.height
        self.player.x = self.player.rect.x
        self.player.y = self.player.rect.y
        self.player.on_ground = True
        
        # Handle player shooting
        if self.player.reloading:
            self.player.reload_timer += 1
            if self.player.reload_timer >= self.player.reload_time:
                self.player.finish_reload()
        
        if self.player.shooting and self.player.shoot_cooldown <= 0 and self.player.magazine_current > 0 and not self.player.reloading:
            self.player.shoot()
        
        if self.player.shoot_cooldown > 0:
            self.player.shoot_cooldown -= 1
        
        # Update bullets
        for bullet in self.player.bullets[:]:
            bullet.update()
            # Remove bullets that go off screen
            if (bullet.x < 0 or bullet.x > self.width or 
                bullet.y < 0 or bullet.y > self.height):
                self.player.bullets.remove(bullet)
        
        # Update zombies
        for zombie in self.zombies[:]:
            # Update zombie with barricade
            zombie.update(self.player, self.barricade)
            
            # Check if player hit zombie
            if self.player.check_bullet_hits(zombie):
                # Check if zombie explodes
                if zombie.health <= 0:
                    if hasattr(zombie, 'explodes') and zombie.explodes:
                        # Create explosion
                        self.explosions.append({
                            "x": zombie.rect.centerx,
                            "y": zombie.rect.centery,
                            "radius": 0,
                            "max_radius": 60,
                            "damage": 50,
                            "growth_rate": 3,
                            "color": (255, 165, 0)
                        })
                    
                    # Remove dead zombie and add score
                    self.zombies.remove(zombie)
                    self.score += 10
                    self.zombies_killed += 1
                    
                    # Add resources for killing zombies
                    if zombie.type == "normal":
                        self.resources += 2
                    elif zombie.type == "fast":
                        self.resources += 3
                    elif zombie.type == "tank":
                        self.resources += 8
                    elif zombie.type == "exploder":
                        self.resources += 5
                    elif zombie.type == "spitter":
                        self.resources += 6
            
            # Check if zombie reached player (if barricade is destroyed)
            elif self.barricade.is_destroyed() and zombie.rect.colliderect(self.player.rect):
                self.player.take_damage(zombie.damage)
                # Knock zombie back
                zombie.x += 50
                zombie.rect.x = zombie.x
                
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion["radius"] += explosion["growth_rate"]
            
            # Check if explosion hits zombies
            for zombie in self.zombies[:]:
                # Calculate distance between explosion center and zombie center
                dx = zombie.rect.centerx - explosion["x"]
                dy = zombie.rect.centery - explosion["y"]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # If zombie is within explosion radius
                if distance < explosion["radius"]:
                    # Damage decreases with distance
                    damage_factor = 1 - (distance / explosion["radius"])
                    damage = explosion["damage"] * damage_factor
                    zombie.take_damage(damage)
                    
                    # Check if zombie died
                    if zombie.health <= 0:
                        self.zombies.remove(zombie)
                        self.score += 10
                        self.zombies_killed += 1
            
            # Check if explosion hits barricade
            dx = self.barricade.rect.centerx - explosion["x"]
            dy = self.barricade.rect.centery - explosion["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < explosion["radius"]:
                damage_factor = 1 - (distance / explosion["radius"])
                damage = explosion["damage"] * damage_factor * 0.5  # Reduced damage to barricade
                self.barricade.take_damage(damage)
            
            # Remove explosion when it reaches max size
            if explosion["radius"] >= explosion["max_radius"]:
                self.explosions.remove(explosion)
        
        # Check if zombies are damaging the barricade
        if self.barricade.check_zombie_collision(self.zombies):
            # Apply damage from all zombies touching the barricade
            total_damage = 0
            for zombie in self.zombies:
                if zombie.rect.colliderect(self.barricade.rect):
                    total_damage += zombie.barricade_damage
            
            self.barricade.take_damage(total_damage)
        
        # Spawn new zombies based on difficulty (day count)
        # Calculate max active zombies based on day count
        if self.day_count == 1:
            max_active_zombies = 8  # First night is easier
        else:
            max_active_zombies = 8 + (self.day_count - 1) * 3  # +3 active zombies per night
        
        # Spawn frequency increases with difficulty
        base_spawn_chance = 60  # Higher is less frequent
        spawn_chance = max(10, base_spawn_chance - (self.day_count * 5))  # Minimum 10
        
        # Spawn zombies if under both the active limit and total night limit
        if (len(self.zombies) < max_active_zombies and 
            self.zombies_spawned_tonight < self.max_zombies_tonight and 
            random.randint(0, spawn_chance) == 0):
            self.zombies.append(Zombie.spawn_zombie(self.width, self.height, self.day_count))
            self.zombies_spawned_tonight += 1
        
        # Check if night is over
        self.cycle_timer += 1 / self.fps
        if self.cycle_timer >= self.night_duration or self.barricade.is_destroyed():
            if self.barricade.is_destroyed() and self.player.health > 0:
                # If barricade was destroyed but player survived, reduce health
                self.player.health = max(10, self.player.health - 30)
            
            self.cycle_timer = 0
            self.state = GameState.DAY
            self.prepare_day()
    
    def update_menu(self):
        # Menu logic - nothing to update in this simple implementation
        pass
    
    def update_game_over(self):
        # Game over logic - nothing to update in this simple implementation
        pass
    
    def update_shop(self):
        """Update shop state"""
        # Shop is handled through events
        if not self.shop.active:
            # Shop is closed, proceed to night
            self.state = GameState.NIGHT
            self.prepare_night()
            
        # Update resources from shop
        self.resources = self.shop.resources
    
    def reset_game(self):
        # Reset game state for a new game
        self.state = GameState.DAY
        self.cycle_timer = 0
        self.day_count = 1
        self.score = 0
        self.resources = 0
        self.resources_collected = 0
        self.zombies_killed = 0
        self.zombies_spawned_tonight = 0
        self.max_zombies_tonight = 20
        
        # Reset player
        self.player = Player(self.width // 2, self.height - 200)
        
        # Reset barricade
        self.barricade = Barricade(200, self.height - 200, 30, 200)
        
        # Clear entities
        self.zombies.clear()
        self.explosions.clear()
        
        # Generate new level
        self.world = World(self.width, self.height)
        
        # Reset camera
        self.camera = Camera(self.width, self.height, self.world.width)
    
    def prepare_day(self):
        # Clear zombies
        self.zombies.clear()
        
        # Heal player slightly
        self.player.health = min(100, self.player.health + 20)
        
        # Reset player position
        self.player.rect.x = self.width // 2
        self.player.rect.y = self.height - 200
        self.player.x = self.player.rect.x
        self.player.y = self.player.rect.y
        
        # Reset camera
        self.camera.x = 0
        
        # Generate new level layout
        self.world.generate_level()
        
        # Reset resources collected counter for the new day
        self.resources_collected = 0
        
        # Increment day count
        self.day_count += 1
    
    def prepare_night(self):
        # Reset player position for night phase
        self.player.rect.x = 100
        self.player.rect.y = self.height - self.world.ground_height - self.player.height
        self.player.x = self.player.rect.x
        self.player.y = self.player.rect.y
        
        # Reset barricade
        self.barricade = Barricade(200, self.height - 200, 30, 200)
        
        # Clear any existing zombies and explosions
        self.zombies.clear()
        self.explosions.clear()
        
        # Reset zombie counter for the night
        self.zombies_spawned_tonight = 0
        
        # Calculate max zombies for this night
        if self.day_count == 1:
            self.max_zombies_tonight = 20  # First night limit
        else:
            self.max_zombies_tonight = 20 + (self.day_count - 1) * 10  # +10 zombies per night
        
        # Spawn initial zombies based on day count
        self.spawn_initial_zombies()
        
        # Make sure player has at least some ammo for the night
        min_total_ammo = self.player.magazine_size * 3
        if self.player.ammo_total < min_total_ammo:
            self.player.ammo_total = min_total_ammo
        
        # Fill the magazine
        bullets_needed = self.player.magazine_size - self.player.magazine_current
        if bullets_needed > 0:
            bullets_to_add = min(bullets_needed, self.player.ammo_total)
            self.player.magazine_current += bullets_to_add
            self.player.ammo_total -= bullets_to_add
    
    def spawn_initial_zombies(self):
        """Spawn an initial wave of zombies based on day count"""
        # Calculate number of zombies to spawn
        if self.day_count == 1:
            # First night: 3 normal zombies
            common_count = 3
            rare_count = 0
        else:
            # Later nights: increasing numbers
            common_count = 3 + (self.day_count - 1) * 2
            rare_count = self.day_count - 1
        
        # Update zombie counter
        self.zombies_spawned_tonight = common_count + rare_count
        
        # Spawn common zombies (normal and fast)
        for _ in range(common_count):
            # Position zombies at different distances
            x = self.width + random.randint(50, 500)
            y = self.height - 100 - random.randint(0, 20)
            
            # 70% normal, 30% fast for common zombies
            zombie_type = "fast" if random.random() < 0.3 else "normal"
            self.zombies.append(Zombie(x, y, zombie_type))
        
        # Spawn rare zombies (tank, exploder, spitter)
        for _ in range(rare_count):
            # Position rare zombies further back
            x = self.width + random.randint(300, 800)
            y = self.height - 100 - random.randint(0, 20)
            
            # Equal chance for each rare type
            zombie_type = random.choice(["tank", "exploder", "spitter"])
            self.zombies.append(Zombie(x, y, zombie_type))
            
            # Equal chance for each rare type
            zombie_type = random.choice(["tank", "exploder", "spitter"])
            self.zombies.append(Zombie(x, y, zombie_type))
    
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
        
        # Update display
        pygame.display.flip()
    
    def render_day(self):
        # Draw world (includes sky, ground, platforms, resources)
        self.world.render(self.screen, self.camera)
        
        # Draw player (adjusted for camera)
        self.player.render(self.screen, self.camera)
        
        # Draw UI
        self.render_ui()
    
    def render_night(self):
        # Draw night background (dark blue)
        self.screen.fill((25, 25, 50))
        
        # Draw ground
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (0, self.height - self.world.ground_height, self.width, self.world.ground_height))
        
        # Draw barricade
        self.barricade.render(self.screen)
        
        # Draw player
        self.player.render(self.screen)
        
        # Draw zombies
        for zombie in self.zombies:
            zombie.render(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            pygame.draw.circle(self.screen, explosion["color"], 
                              (int(explosion["x"]), int(explosion["y"])), 
                              int(explosion["radius"]))
            # Draw explosion border
            pygame.draw.circle(self.screen, (255, 255, 255), 
                              (int(explosion["x"]), int(explosion["y"])), 
                              int(explosion["radius"]), 2)
        
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
    
    def render_shop(self):
        # Draw the world in the background (dimmed)
        self.render_day()
        
        # Let the shop system handle its own rendering
        self.shop.render(self.screen)
    
    def render_ui(self):
        # Draw UI elements like health, ammo, day/night indicator
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        # Health bar
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, self.player.health * 2, 20))
        health_text = small_font.render(f"Health: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (25, 22))
        
        # Day/Night indicator
        if self.state == GameState.DAY:
            time_text = font.render(f"Day {self.day_count} - {int(self.day_duration - self.cycle_timer)}s until night", True, (0, 0, 0))
            skip_text = small_font.render("Press N to skip to shop", True, (100, 100, 100))
            self.screen.blit(skip_text, (20, 80))
        else:
            time_text = font.render(f"Night {self.day_count} - {int(self.night_duration - self.cycle_timer)}s until day", True, (255, 255, 255))
            skip_text = small_font.render("Press N to skip to day", True, (150, 150, 150))
            self.screen.blit(skip_text, (20, 80))
        
        self.screen.blit(time_text, (20, 50))
        
        # Score and stats
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        
        # Count collected resources
        collected_count = sum(1 for resource in self.world.resources if resource.collected)
        total_count = len(self.world.resources)
        
        if self.state == GameState.DAY:
            resources_text = font.render(f"Resources: {collected_count}/{total_count}", True, (255, 255, 255))
            currency_text = font.render(f"Currency: {self.resources}", True, (255, 255, 0))
        else:
            resources_text = font.render(f"Zombies Killed: {self.zombies_killed}", True, (255, 255, 255))
            currency_text = font.render(f"Currency: {self.resources}", True, (255, 255, 0))
        
        self.screen.blit(score_text, (self.width - score_text.get_width() - 20, 20))
        self.screen.blit(resources_text, (self.width - resources_text.get_width() - 20, 60))
        self.screen.blit(currency_text, (self.width - currency_text.get_width() - 20, 100))
        
        # Barricade health (only during night)
        if self.state == GameState.NIGHT:
            barricade_health = int(self.barricade.health / self.barricade.max_health * 100)
            barricade_text = font.render(f"Barricade: {barricade_health}%", True, (255, 255, 255))
            self.screen.blit(barricade_text, (self.width - barricade_text.get_width() - 20, 100))
            
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
                
            difficulty_label = font.render(f"Difficulty: ", True, (255, 255, 255))
            difficulty_value = font.render(difficulty_text, True, difficulty_color)
            
            self.screen.blit(difficulty_label, (self.width - difficulty_label.get_width() - difficulty_value.get_width() - 20, 140))
            self.screen.blit(difficulty_value, (self.width - difficulty_value.get_width() - 20, 140))
            
            # Zombie counter
            zombie_text = font.render(f"Zombies: {self.zombies_spawned_tonight}/{self.max_zombies_tonight}", True, (255, 255, 255))
            self.screen.blit(zombie_text, (self.width - zombie_text.get_width() - 20, 180))
        
        # Ammo display
        if self.state == GameState.NIGHT:
            # Draw magazine indicator
            mag_x = 20
            mag_y = 100
            mag_width = 150
            mag_height = 30
            
            # Magazine background
            pygame.draw.rect(self.screen, (50, 50, 50), (mag_x, mag_y, mag_width, mag_height))
            
            # Current bullets in magazine
            bullet_width = mag_width / self.player.magazine_size
            for i in range(self.player.magazine_current):
                pygame.draw.rect(self.screen, (255, 255, 0), 
                                (mag_x + i * bullet_width, mag_y, bullet_width - 2, mag_height))
            
            # Magazine border
            pygame.draw.rect(self.screen, (200, 200, 200), (mag_x, mag_y, mag_width, mag_height), 2)
            
            # Ammo text
            if self.player.reloading:
                ammo_text = font.render("RELOADING...", True, (255, 255, 0))
            else:
                # Show magazine/total (excluding what's in the magazine)
                remaining_ammo = max(0, self.player.ammo_total)
                ammo_text = font.render(f"Ammo: {self.player.magazine_current}/{remaining_ammo}", True, (255, 255, 255))
            
            self.screen.blit(ammo_text, (mag_x, mag_y + mag_height + 10))
    
    def run(self):
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
