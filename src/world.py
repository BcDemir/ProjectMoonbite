import pygame

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create ground
        self.ground_height = 100
        self.ground_rect = pygame.Rect(0, height - self.ground_height, width, self.ground_height)
        
        # Create platforms and obstacles
        self.platforms = []
        self.obstacles = []
        
        # Add some basic platforms
        self.platforms.append(pygame.Rect(100, 500, 200, 20))
        self.platforms.append(pygame.Rect(400, 400, 200, 20))
        self.platforms.append(pygame.Rect(700, 500, 200, 20))
        
        # Add some obstacles (for cover during night)
        self.obstacles.append(pygame.Rect(150, 450, 50, 50))
        self.obstacles.append(pygame.Rect(450, 350, 50, 50))
        self.obstacles.append(pygame.Rect(750, 450, 50, 50))
    
    def render(self, screen):
        # Draw ground
        pygame.draw.rect(screen, (139, 69, 19), self.ground_rect)  # Brown
        
        # Draw grass on top of ground
        pygame.draw.rect(screen, (34, 139, 34), 
                        (0, self.height - self.ground_height, self.width, 20))  # Green
        
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(screen, (169, 169, 169), platform)  # Gray
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (139, 69, 19), obstacle)  # Brown
