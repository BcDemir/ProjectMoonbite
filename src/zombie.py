import pygame
import random
import math

class Zombie:
    def __init__(self, x, y, zombie_type="normal"):
        self.x = x
        self.y = y
        self.type = zombie_type
        print(f"Creating zombie of type: {zombie_type}")
        self.state = "approaching"  # Initial state: approaching, attacking_barricade, attacking_player
        
        # Default attack cooldown values for all zombies
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # 1 second at 60 FPS
        
        # Set attributes based on zombie type
        if zombie_type == "normal":
            self.width = 40
            self.height = 60
            self.color = (0, 128, 0)  # Green
            self.speed = 1.5
            self.health = 30
            self.damage = 10
            self.barricade_damage = 15
        elif zombie_type == "fast":
            self.width = 30
            self.height = 50
            self.color = (144, 238, 144)  # Light green
            self.speed = 3
            self.health = 20
            self.damage = 5
            self.barricade_damage = 10
        elif zombie_type == "tank":
            self.width = 50
            self.height = 70
            self.color = (0, 100, 0)  # Dark green
            self.speed = 0.8
            self.health = 100
            self.damage = 20
            self.barricade_damage = 30
        elif zombie_type == "exploder":
            self.width = 45
            self.height = 45
            self.color = (255, 165, 0)  # Orange
            self.speed = 2
            self.health = 40
            self.damage = 50
            self.barricade_damage = 100
            self.explodes = True
        elif zombie_type == "spitter":
            self.width = 35
            self.height = 55
            self.color = (173, 255, 47)  # GreenYellow
            self.speed = 1.2
            self.health = 45
            self.damage = 15
            self.barricade_damage = 25
            self.range_attack = True
            self.attack_cooldown = 0
            self.attack_cooldown_max = 180  # 3 seconds at 60 FPS
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
        
        # Special attributes
        self.explodes = hasattr(self, 'explodes') and self.explodes
        self.range_attack = hasattr(self, 'range_attack') and self.range_attack
        self.projectiles = []
    
    @classmethod
    def spawn_zombie(cls, screen_width, screen_height, difficulty=1):
        """Create a zombie at the right edge of the screen
        
        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
            difficulty: Day count, affects zombie type probability
        """
        # Determine zombie type based on difficulty
        # As difficulty increases, rare zombies become more common
        rare_zombie_chance = min(0.1 + (difficulty * 0.03), 0.5)  # Caps at 50% for rare zombies
        
        if random.random() < rare_zombie_chance:
            # Spawn a rare zombie
            # As difficulty increases, tougher rare zombies become more common
            if difficulty <= 3:
                # Early nights: mostly exploders
                weights = [0.2, 0.7, 0.1]  # tank, exploder, spitter
            elif difficulty <= 6:
                # Mid nights: balanced mix
                weights = [0.3, 0.4, 0.3]  # tank, exploder, spitter
            else:
                # Later nights: more tanks and spitters
                weights = [0.4, 0.2, 0.4]  # tank, exploder, spitter
                
            # Choose based on weights
            r = random.random()
            if r < weights[0]:
                zombie_type = "tank"
            elif r < weights[0] + weights[1]:
                zombie_type = "exploder"
            else:
                zombie_type = "spitter"
        else:
            # Spawn a common zombie
            # As difficulty increases, fast zombies become more common
            fast_zombie_chance = min(0.3 + (difficulty * 0.05), 0.7)  # Caps at 70% for fast zombies
            zombie_type = "fast" if random.random() < fast_zombie_chance else "normal"
        
        # Always spawn from right side
        x = screen_width + random.randint(10, 50)
        
        # Y position is on the ground
        y = screen_height - 100 - random.randint(0, 20)
        
        return cls(x, y, zombie_type)
    
    def update(self, player, barricade=None):
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Determine target based on barricade state
        if barricade and not barricade.is_destroyed():
            # Target the barricade if it's not destroyed
            target_x = barricade.rect.left  # Target the left side of the barricade
            
            # Check if colliding with barricade
            if self.rect.right >= barricade.rect.left:
                self.state = "attacking_barricade"
                # Move back to prevent overlap
                self.x = barricade.rect.left - self.width
            elif abs(self.rect.right - barricade.rect.left) < 10:
                self.state = "attacking_barricade"
            else:
                self.state = "approaching"
        else:
            # Target the player if barricade is destroyed or doesn't exist
            target_x = player.rect.centerx
            
            # Check if close enough to attack player
            if abs(self.rect.centerx - player.rect.centerx) < 20:
                self.state = "attacking_player"
            else:
                self.state = "approaching"
        
        # Move towards target if not attacking
        if self.state == "approaching":
            # Always move left (towards barricade/player)
            self.x -= self.speed
        
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Simple ground collision (assuming ground is at y=700)
        if self.y + self.height > 700:
            self.y = 700 - self.height
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update rect position - IMPORTANT: This ensures collision detection works properly
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Handle range attacks for spitter zombies
        if self.range_attack:
            if self.attack_cooldown <= 0:
                if barricade and not barricade.is_destroyed():
                    # Create a projectile aimed at the barricade
                    self.projectiles.append({
                        "x": self.rect.centerx,
                        "y": self.rect.centery,
                        "speed_x": -5,
                        "speed_y": -2,
                        "size": 8,
                        "damage": 15,
                        "rect": pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8)
                    })
                    self.attack_cooldown = self.attack_cooldown_max
                elif barricade and barricade.is_destroyed():
                    # Create a projectile aimed at the player
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    distance = max(1, math.sqrt(dx*dx + dy*dy))
                    
                    # Normalize and scale
                    speed_x = dx / distance * 6
                    speed_y = dy / distance * 6 - 2  # Add slight upward arc
                    
                    self.projectiles.append({
                        "x": self.rect.centerx,
                        "y": self.rect.centery,
                        "speed_x": speed_x,
                        "speed_y": speed_y,
                        "size": 8,
                        "damage": 15,
                        "rect": pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8)
                    })
                    self.attack_cooldown = self.attack_cooldown_max
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile["x"] += projectile["speed_x"]
            projectile["y"] += projectile["speed_y"]
            
            # Apply gravity to projectile
            projectile["speed_y"] += 0.2
            
            # Update projectile rect
            projectile["rect"].x = projectile["x"]
            projectile["rect"].y = projectile["y"]
            
            # Check if projectile hits barricade
            if barricade and not barricade.is_destroyed() and projectile["rect"].colliderect(barricade.rect):
                barricade.take_damage(projectile["damage"])
                self.projectiles.remove(projectile)
            # Check if projectile hits player
            elif barricade and barricade.is_destroyed() and projectile["rect"].colliderect(player.rect):
                player.take_damage(projectile["damage"])
                self.projectiles.remove(projectile)
            # Check if projectile hits ground or goes off screen
            elif projectile["y"] > 700 or projectile["x"] < 0 or projectile["x"] > 1024:
                self.projectiles.remove(projectile)
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Handle range attacks for spitter zombies
        if self.range_attack:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0 and barricade and not barricade.is_destroyed():
                # Create a projectile aimed at the barricade
                self.projectiles.append({
                    "x": self.rect.centerx,
                    "y": self.rect.centery,
                    "speed_x": -5,
                    "speed_y": -2,
                    "size": 8,
                    "damage": 15,
                    "rect": pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8)
                })
                self.attack_cooldown = self.attack_cooldown_max
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile["x"] += projectile["speed_x"]
            projectile["y"] += projectile["speed_y"]
            projectile["speed_y"] += 0.2  # Gravity effect
            
            # Update rect
            projectile["rect"].x = projectile["x"]
            projectile["rect"].y = projectile["y"]
            
            # Check if projectile hits barricade
            if barricade and projectile["rect"].colliderect(barricade.rect):
                barricade.take_damage(projectile["damage"])
                self.projectiles.remove(projectile)
            
            # Check if projectile hits ground or goes off screen
            elif projectile["y"] > 700 or projectile["x"] < 0:
                self.projectiles.remove(projectile)
    
    def take_damage(self, amount):
        self.health -= amount
        
        # Handle exploder zombie death
        if self.health <= 0 and self.explodes:
            return True  # Signal an explosion
        
        return False
    
    def render(self, screen):
        # Draw zombie body
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw health bar above zombie
        max_health = 100 if self.type == "tank" else 30 if self.type == "normal" else 20
        health_percent = max(0, self.health / max_health)
        health_width = self.width * health_percent
        
        # Health bar background (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.rect.x, self.rect.y - 10, self.width, 5))
        
        # Health bar foreground (green)
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), 
                            (self.rect.x, self.rect.y - 10, health_width, 5))
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw zombie type indicator
        if self.type == "tank":
            # Draw a shield symbol
            pygame.draw.circle(screen, (200, 200, 200), 
                              (self.rect.centerx, self.rect.centery), 10)
        elif self.type == "fast":
            # Draw a speed symbol (lightning)
            points = [
                (self.rect.centerx - 5, self.rect.centery - 10),
                (self.rect.centerx + 5, self.rect.centery),
                (self.rect.centerx - 2, self.rect.centery),
                (self.rect.centerx + 5, self.rect.centery + 10)
            ]
            pygame.draw.lines(screen, (255, 255, 0), False, points, 2)
        elif self.type == "exploder":
            # Draw an explosion symbol
            pygame.draw.circle(screen, (255, 0, 0), 
                              (self.rect.centerx, self.rect.centery), 8)
        elif self.type == "spitter":
            # Draw a spit symbol
            pygame.draw.circle(screen, (0, 255, 0), 
                              (self.rect.centerx, self.rect.centery - 10), 5)
        
        # Draw attack indicator when attacking barricade or player
        if self.state == "attacking_barricade" or self.state == "attacking_player":
            # Draw attack animation (red flash)
            if self.attack_cooldown < 10:  # Flash during the first part of attack cooldown
                pygame.draw.rect(screen, (255, 0, 0), 
                                (self.rect.x - 5, self.rect.y - 5, self.width + 10, self.height + 10), 2)
        
        # Draw projectiles
        for projectile in self.projectiles:
            pygame.draw.circle(screen, (0, 255, 0), 
                              (int(projectile["x"]), int(projectile["y"])), 
                              projectile["size"])
    def is_attacking_barricade(self):
        """Check if zombie is close enough to attack the barricade"""
        return self.state == "attacking_barricade"
    def attack_barricade(self, barricade):
        """Attack the barricade if cooldown allows"""
        if self.attack_cooldown <= 0:
            # Apply damage to barricade
            barricade.take_damage(self.barricade_damage)
            # Reset attack cooldown
            self.attack_cooldown = self.attack_cooldown_max
            
    def attack_player(self, player):
        """Attack the player if cooldown allows"""
        if self.attack_cooldown <= 0:
            # Apply damage to player
            player.take_damage(self.damage)
            # Reset attack cooldown
            self.attack_cooldown = self.attack_cooldown_max
            
    def take_damage(self, damage):
        """Take damage from player attacks"""
        self.health -= damage
