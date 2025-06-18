import pygame
import math
import random

class Crosshair:
    def __init__(self):
        # Crosshair properties
        self.color = (255, 0, 0)  # Red crosshair
        self.line_length = 15     # Fixed length of each line
        self.thickness = 2        # Line thickness
        
        # Gap properties
        self.min_gap = 3          # Minimum gap when close to player
        self.max_gap = 20         # Maximum gap when far from player
        self.current_gap = 10     # Current gap between center and lines
        
        # Position
        self.position = (0, 0)
        
    def update(self, player_pos, mouse_pos):
        """Update crosshair gap based on distance from player"""
        # Get current mouse position
        self.position = mouse_pos
        
        # Calculate distance from player to mouse
        dx = mouse_pos[0] - player_pos[0]
        dy = mouse_pos[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Scale gap based on distance (closer = smaller gap, farther = larger gap)
        max_distance = 500  # Maximum distance to consider
        distance_factor = min(distance / max_distance, 1.0)
        
        # Calculate gap - only affected by distance
        self.current_gap = self.min_gap + distance_factor * (self.max_gap - self.min_gap)
        
    def render(self, screen):
        """Draw the crosshair at the current mouse position"""
        x, y = self.position
        gap = self.current_gap
        line_length = self.line_length
        
        # Draw four lines (up, down, left, right)
        # Up line
        pygame.draw.line(
            screen, 
            self.color, 
            (x, y - gap), 
            (x, y - gap - line_length), 
            self.thickness
        )
        
        # Down line
        pygame.draw.line(
            screen, 
            self.color, 
            (x, y + gap), 
            (x, y + gap + line_length), 
            self.thickness
        )
        
        # Left line
        pygame.draw.line(
            screen, 
            self.color, 
            (x - gap, y), 
            (x - gap - line_length, y), 
            self.thickness
        )
        
        # Right line
        pygame.draw.line(
            screen, 
            self.color, 
            (x + gap, y), 
            (x + gap + line_length, y), 
            self.thickness
        )
    
    def set_color_for_weapon(self, weapon_type):
        """Set crosshair color based on weapon type"""
        weapon_colors = {
            "pistol": (255, 255, 0),    # Yellow
            "shotgun": (255, 165, 0),   # Orange
            "rifle": (255, 0, 0),       # Red
            "smg": (0, 255, 255),       # Cyan
            "machine_gun": (0, 255, 255)  # Cyan
        }
        
        self.color = weapon_colors.get(weapon_type, (255, 0, 0))  # Default to red
    
    def on_shoot(self):
        """Called when player shoots"""
        # No animation effects as requested
        pass
