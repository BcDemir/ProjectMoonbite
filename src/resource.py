import pygame
import random

class Resource:
    def __init__(self, x, y, resource_type="wood"):
        self.x = x
        self.y = y
        self.type = resource_type
        
        # Set attributes based on resource type
        if resource_type == "wood":
            self.width = 30
            self.height = 30
            self.color = (139, 69, 19)  # Brown
            self.value = 1
        elif resource_type == "metal":
            self.width = 25
            self.height = 25
            self.color = (169, 169, 169)  # Gray
            self.value = 2
        elif resource_type == "food":
            self.width = 20
            self.height = 20
            self.color = (255, 0, 0)  # Red
            self.value = 3
        elif resource_type == "medicine":
            self.width = 15
            self.height = 15
            self.color = (255, 255, 255)  # White
            self.value = 5
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.collected = False
    
    @classmethod
    def random_resource(cls, screen_width, screen_height):
        """Create a resource at a random position on the screen"""
        resource_type = random.choice(["wood", "metal", "food", "medicine"])
        
        # Random position, but not too close to edges
        x = random.randint(50, screen_width - 50)
        y = random.randint(50, screen_height - 150)  # Keep above ground level
        
        return cls(x, y, resource_type)
    
    def update(self):
        # Resources don't need much updating in this simple implementation
        pass
    
    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
