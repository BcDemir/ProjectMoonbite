import pygame
import random

class Platform:
    def __init__(self, x, y, width, height, platform_type="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        
        # Set appearance based on type
        if platform_type == "normal":
            self.color = (169, 169, 169)  # Gray
        elif platform_type == "grass":
            self.color = (34, 139, 34)  # Green
        elif platform_type == "metal":
            self.color = (192, 192, 192)  # Silver
        elif platform_type == "wood":
            self.color = (139, 69, 19)  # Brown
        else:
            self.color = (169, 169, 169)  # Default gray
    
    def render(self, screen, camera):
        # Only render if platform is visible on screen
        camera_rect = camera.apply(self.rect)
        if camera_rect.right >= 0 and camera_rect.left <= camera.width:
            pygame.draw.rect(screen, self.color, camera_rect)
            pygame.draw.rect(screen, (0, 0, 0), camera_rect, 2)  # Black border

class Resource:
    def __init__(self, x, y, resource_type="ammo"):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.type = resource_type
        self.collected = False
        
        # Set appearance based on type
        if resource_type == "ammo":
            self.color = (255, 255, 0)  # Yellow
        elif resource_type == "health":
            self.color = (255, 0, 0)  # Red
        elif resource_type == "weapon":
            self.color = (0, 0, 255)  # Blue
        else:
            self.color = (255, 255, 255)  # White
    
    def render(self, screen, camera):
        if not self.collected:
            # Only render if resource is visible on screen
            camera_rect = camera.apply(self.rect)
            if camera_rect.right >= 0 and camera_rect.left <= camera.width:
                pygame.draw.rect(screen, self.color, camera_rect)
                pygame.draw.rect(screen, (0, 0, 0), camera_rect, 2)  # Black border

class World:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create a world that's 3x the screen width
        self.width = screen_width * 3
        self.height = screen_height
        
        # Create ground
        self.ground_height = 100
        self.ground_rect = pygame.Rect(0, self.height - self.ground_height, self.width, self.ground_height)
        
        # Create platforms and resources
        self.platforms = []
        self.resources = []
        
        # Generate level layout
        self.generate_level()
    
    def generate_level(self):
        # Clear existing objects
        self.platforms.clear()
        self.resources.clear()
        
        # Add ground platform
        ground = Platform(0, self.height - self.ground_height, self.width, self.ground_height, "grass")
        self.platforms.append(ground)
        
        # Create platforms across the entire world width
        # First section (screen 1)
        self.platforms.append(Platform(100, 550, 200, 20, "wood"))
        self.platforms.append(Platform(50, 450, 150, 20, "wood"))
        self.platforms.append(Platform(200, 350, 150, 20, "metal"))
        self.platforms.append(Platform(400, 500, 200, 20, "metal"))
        self.platforms.append(Platform(450, 400, 150, 20, "wood"))
        self.platforms.append(Platform(350, 300, 100, 20, "metal"))
        self.platforms.append(Platform(650, 550, 200, 20, "wood"))
        self.platforms.append(Platform(700, 450, 150, 20, "metal"))
        self.platforms.append(Platform(600, 350, 150, 20, "wood"))
        self.platforms.append(Platform(500, 200, 100, 20, "metal"))
        self.platforms.append(Platform(300, 200, 100, 20, "metal"))
        
        # Second section (screen 2)
        self.platforms.append(Platform(1100, 500, 200, 20, "wood"))
        self.platforms.append(Platform(1300, 400, 150, 20, "metal"))
        self.platforms.append(Platform(1500, 300, 200, 20, "wood"))
        self.platforms.append(Platform(1200, 200, 100, 20, "metal"))
        self.platforms.append(Platform(1400, 550, 180, 20, "wood"))
        self.platforms.append(Platform(1600, 450, 150, 20, "metal"))
        self.platforms.append(Platform(1750, 350, 120, 20, "wood"))
        self.platforms.append(Platform(1900, 250, 100, 20, "metal"))
        
        # Third section (screen 3)
        self.platforms.append(Platform(2100, 550, 200, 20, "wood"))
        self.platforms.append(Platform(2300, 450, 150, 20, "metal"))
        self.platforms.append(Platform(2500, 350, 200, 20, "wood"))
        self.platforms.append(Platform(2200, 250, 100, 20, "metal"))
        self.platforms.append(Platform(2400, 150, 150, 20, "wood"))
        self.platforms.append(Platform(2600, 500, 180, 20, "metal"))
        self.platforms.append(Platform(2750, 400, 120, 20, "wood"))
        self.platforms.append(Platform(2900, 300, 100, 20, "metal"))
        
        # Add some resources throughout the world
        resource_types = ["ammo", "health", "weapon"]
        for platform in self.platforms:
            # 30% chance to spawn a resource on a platform
            if random.random() < 0.3:
                resource_type = random.choice(resource_types)
                x = platform.rect.x + random.randint(20, platform.rect.width - 40)
                y = platform.rect.y - 30
                self.resources.append(Resource(x, y, resource_type))
    
    def check_platform_collisions(self, player_rect, dy):
        """Check if player collides with platforms and adjust position"""
        for platform in self.platforms:
            # Check if falling onto platform
            if dy > 0 and player_rect.bottom <= platform.rect.top + dy and player_rect.bottom + dy >= platform.rect.top and \
               player_rect.right > platform.rect.left and player_rect.left < platform.rect.right:
                return platform.rect.top - player_rect.height, True
        
        # No collision with platforms
        return player_rect.y + dy, False
    
    def check_resource_collisions(self, player_rect):
        """Check if player collects resources and return collected items"""
        collected = []
        for resource in self.resources:
            if not resource.collected and resource.rect.colliderect(player_rect):
                resource.collected = True
                collected.append(resource.type)
        return collected
    
    def update(self):
        # No enemies to update in daytime
        pass
    
    def render(self, screen, camera):
        # Draw sky gradient background
        for y in range(0, self.height - self.ground_height, 2):
            # Calculate color gradient from top (light blue) to bottom (darker blue)
            blue_val = 235 - int((y / (self.height - self.ground_height)) * 50)
            pygame.draw.line(screen, (135, 206, blue_val), (0, y), (self.screen_width, y))
        
        # Draw ground (only the visible part)
        visible_ground_rect = camera.apply(self.ground_rect)
        pygame.draw.rect(screen, (34, 139, 34), visible_ground_rect)  # Green
        
        # Draw platforms
        for platform in self.platforms:
            platform.render(screen, camera)
        
        # Draw resources
        for resource in self.resources:
            resource.render(screen, camera)
