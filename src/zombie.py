import pygame
import random
import math

class Zombie:
    def __init__(self, x, y, zombie_type="normal"):
        self.x = x
        self.y = y
        self.type = zombie_type
        
        # Set attributes based on zombie type
        if zombie_type == "normal":
            self.width = 40
            self.height = 60
            self.color = (0, 128, 0)  # Green
            self.speed = 2
            self.health = 50
            self.damage = 10
        elif zombie_type == "fast":
            self.width = 30
            self.height = 50
            self.color = (144, 238, 144)  # Light green
            self.speed = 3.5
            self.health = 30
            self.damage = 5
        elif zombie_type == "tank":
            self.width = 50
            self.height = 70
            self.color = (0, 100, 0)  # Dark green
            self.speed = 1
            self.health = 100
            self.damage = 20
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.velocity_y = 0
        self.gravity = 0.8
        self.on_ground = False
    
    @classmethod
    def spawn_zombie(cls, screen_width, screen_height):
        """Create a zombie at a random edge of the screen"""
        zombie_type = random.choice(["normal", "fast", "tank"])
        
        # Decide which edge to spawn from
        edge = random.choice(["left", "right"])
        
        if edge == "left":
            x = -50
        else:
            x = screen_width + 50
        
        # Y position is on the ground
        y = screen_height - 100
        
        return cls(x, y, zombie_type)
    
    def update(self, player):
        # Calculate direction to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        
        # Normalize direction
        dx = dx / distance
        dy = dy / distance
        
        # Move towards player
        self.x += dx * self.speed
        
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
    
    def take_damage(self, amount):
        self.health -= amount
    
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
