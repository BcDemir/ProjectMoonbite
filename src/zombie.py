import pygame
import random
import math

class Zombie:
    def __init__(self, x, y, zombie_type=None):
        self.x = x
        self.y = y
        
        # Randomly select zombie type if not specified
        if zombie_type is None:
            # 80% common zombies, 20% rare zombies
            if random.random() < 0.8:
                zombie_type = random.choice(["normal", "fast"])
            else:
                zombie_type = random.choice(["tank", "exploder", "spitter"])
        
        self.type = zombie_type
        
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
    def spawn_zombie(cls, screen_width, screen_height):
        """Create a zombie at the right edge of the screen"""
        # Randomly determine zombie type based on rarity
        zombie_type = None  # Will be determined in __init__
        
        # Always spawn from right side
        x = screen_width + random.randint(10, 50)
        
        # Y position is on the ground
        y = screen_height - 100 - random.randint(0, 20)
        
        return cls(x, y, zombie_type)
    
    def update(self, player, barricade=None):
        # Move towards player/barricade
        target_x = barricade.rect.right if barricade else player.rect.centerx
        
        # If barricade exists and is not destroyed, don't move past it
        if barricade and not barricade.is_destroyed() and self.rect.left > barricade.rect.right:
            target_x = barricade.rect.right
        
        # Move towards target
        if self.x > target_x:
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
        
        # Draw projectiles
        for projectile in self.projectiles:
            pygame.draw.circle(screen, (0, 255, 0), 
                              (int(projectile["x"]), int(projectile["y"])), 
                              projectile["size"])
