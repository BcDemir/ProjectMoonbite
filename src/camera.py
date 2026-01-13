import pygame

class Camera:
    def __init__(self, width, height, world_width):
        self.width = width
        self.height = height
        self.world_width = world_width  # Total width of the game world
        self.x = 0  # Camera's x position in the world
        
        # Camera movement settings
        self.edge_buffer = 300  # Distance from screen edge before camera starts moving
        self.smooth_factor = 0.1  # Lower values = smoother camera (0-1)
    
    def update(self, player_x):
        """Update camera position based on player position"""
        # Calculate target camera position
        # If player is beyond the edge buffer from the left of the camera view
        if player_x - self.x < self.edge_buffer:
            target_x = max(0, player_x - self.edge_buffer)
        # If player is beyond the edge buffer from the right of the camera view
        elif player_x - self.x > self.width - self.edge_buffer:
            target_x = min(self.world_width - self.width, player_x - (self.width - self.edge_buffer))
        else:
            # Player is within the buffer zone, no need to move camera
            return
        
        # Smooth camera movement
        self.x += (target_x - self.x) * self.smooth_factor
        
        # Ensure camera stays within world bounds
        self.x = max(0, min(self.world_width - self.width, self.x))
    
    def apply(self, rect):
        """Apply camera offset to a rect and return a new rect"""
        return pygame.Rect(rect.x - self.x, rect.y, rect.width, rect.height)
    
    def apply_point(self, x, y):
        """Apply camera offset to a point and return new coordinates"""
        return (x - self.x, y)
    
    def apply_reverse(self, screen_x):
        """Convert screen coordinates to world coordinates"""
        return screen_x + self.x
