import pygame

class Barricade:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
        # Barricade properties
        self.max_health = 1000
        self.health = self.max_health
        self.damage_timer = 0
        self.damage_interval = 120  # 2 seconds at 60 FPS
        self.damage_reduction = 0  # Percentage reduction (0-1)
        
        # Visual properties
        self.base_color = (139, 69, 19)  # Brown
        self.damage_colors = [
            (139, 69, 19),  # 100-75% - Brown
            (165, 42, 42),  # 75-50% - Medium brown
            (178, 34, 34),  # 50-25% - Reddish brown
            (220, 20, 60)   # 25-0% - Crimson
        ]
        
        # Barricade sections (for visual damage)
        self.sections = []
        section_height = height // 10
        for i in range(10):
            self.sections.append({
                "rect": pygame.Rect(x, y + i * section_height, width, section_height),
                "damage": 0  # 0-100% damage per section
            })
    
    def take_damage(self, amount):
        """Apply damage to the barricade"""
        # Apply damage reduction if any
        if hasattr(self, 'damage_reduction') and self.damage_reduction > 0:
            amount = amount * (1 - self.damage_reduction)
            
        self.health -= amount
        if self.health < 0:
            self.health = 0
            
        # Update section damage based on overall health
        health_percent = self.health / self.max_health
        for i, section in enumerate(self.sections):
            # More damage to upper sections
            section_threshold = (10 - i) / 10
            if health_percent < section_threshold:
                damage_factor = (section_threshold - health_percent) / section_threshold
                section["damage"] = min(100, section["damage"] + damage_factor * 100)
    
    def is_destroyed(self):
        """Check if barricade is completely destroyed"""
        return self.health <= 0
    
    def check_zombie_collision(self, zombies):
        """Check for zombie collisions and apply damage after interval"""
        zombies_touching = False
        
        for zombie in zombies:
            if zombie.rect.colliderect(self.rect):
                zombies_touching = True
                break
        
        if zombies_touching:
            self.damage_timer += 1
            if self.damage_timer >= self.damage_interval:
                self.damage_timer = 0
                return True  # Time to damage the barricade
        else:
            self.damage_timer = 0
            
        return False
    
    def render(self, screen):
        # Draw base barricade
        pygame.draw.rect(screen, self.base_color, self.rect)
        
        # Draw sections with damage
        for section in self.sections:
            if section["damage"] > 0:
                # Calculate color based on damage
                damage_index = min(3, int(section["damage"] / 25))
                color = self.damage_colors[damage_index]
                
                # Draw damage overlay
                damage_rect = section["rect"].copy()
                # Adjust width based on damage
                damage_width = int(self.width * (section["damage"] / 100))
                damage_rect.width = damage_width
                pygame.draw.rect(screen, color, damage_rect)
                
                # Draw cracks
                if section["damage"] > 50:
                    crack_start = (section["rect"].right - 10, section["rect"].top)
                    crack_end = (section["rect"].left + 10, section["rect"].bottom)
                    pygame.draw.line(screen, (0, 0, 0), crack_start, crack_end, 2)
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw health bar above barricade
        health_percent = self.health / self.max_health
        bar_width = self.width
        bar_height = 10
        bar_x = self.x
        bar_y = self.y - 20
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Foreground (green)
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Draw damage reduction indicator if any
        if hasattr(self, 'damage_reduction') and self.damage_reduction > 0:
            dr_text = pygame.font.SysFont(None, 20).render(
                f"DR: {int(self.damage_reduction * 100)}%", True, (255, 255, 255))
            screen.blit(dr_text, (bar_x, bar_y - 20))
