import pygame
import random

class Location:
    def __init__(self, name, x, y, width, height, resources, risk):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.resources = resources  # Dictionary of possible resources and their quantities
        self.risk = risk  # Percentage chance of zombie bite (0-100)
        self.highlighted = False
        self.visited = False
        self.color = (100, 100, 100)  # Default color
        self.highlight_color = (150, 150, 150)  # Highlight color
        self.visited_color = (70, 70, 70)  # Visited color
    
    def is_mouse_over(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def visit(self):
        """Simulate visiting this location and return results"""
        if self.visited:
            return {"success": False, "message": "Already visited today"}
        
        self.visited = True
        
        # Check if player gets bitten
        bitten = random.random() * 100 < self.risk
        
        # Determine gathered resources
        gathered_resources = {}
        for resource, max_amount in self.resources.items():
            # Random amount between 40-100% of max
            amount = int(max_amount * (0.4 + 0.6 * random.random()))
            if amount > 0:
                gathered_resources[resource] = amount
        
        return {
            "success": True,
            "bitten": bitten,
            "resources": gathered_resources,
            "message": "You were bitten by a zombie!" if bitten else "Scavenging successful!"
        }
    
    def render(self, screen, font):
        # Draw the location
        if self.highlighted:
            pygame.draw.rect(screen, self.highlight_color, self.rect)
        elif self.visited:
            pygame.draw.rect(screen, self.visited_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw name
        name_text = font.render(self.name, True, (0, 0, 0))
        screen.blit(name_text, (self.x + self.width//2 - name_text.get_width()//2, 
                               self.y + self.height//2 - name_text.get_height()//2))
    
    def render_tooltip(self, screen, font, mouse_pos):
        if not self.highlighted:
            return
        
        # Create tooltip content
        lines = [
            f"Location: {self.name}",
            f"Risk: {self.risk}% chance of zombie bite",
            "Possible resources:"
        ]
        
        for resource, amount in self.resources.items():
            lines.append(f"- {resource}: up to {amount}")
        
        if self.visited:
            lines.append("Already visited today")
        
        # Calculate tooltip dimensions
        line_height = font.get_height() + 2
        max_width = max(font.size(line)[0] for line in lines) + 20
        tooltip_height = line_height * len(lines) + 10
        
        # Position tooltip near mouse but ensure it stays on screen
        x = mouse_pos[0] + 15
        y = mouse_pos[1] + 15
        
        if x + max_width > screen.get_width():
            x = screen.get_width() - max_width - 5
        
        if y + tooltip_height > screen.get_height():
            y = screen.get_height() - tooltip_height - 5
        
        # Draw tooltip background
        tooltip_rect = pygame.Rect(x, y, max_width, tooltip_height)
        pygame.draw.rect(screen, (255, 255, 220), tooltip_rect)
        pygame.draw.rect(screen, (0, 0, 0), tooltip_rect, 2)
        
        # Draw text
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (x + 10, y + 5 + i * line_height))


class CityMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.locations = []
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36)
        self.result_font = pygame.font.SysFont(None, 28)
        self.showing_result = False
        self.result_data = None
        self.result_timer = 0
        self.result_duration = 3  # seconds
        self.visits_remaining = 3  # Number of locations player can visit per day
        
        # Create locations
        self.create_locations()
    
    def create_locations(self):
        # Define some locations with their resources and risk levels
        locations_data = [
            {
                "name": "House 1",
                "x": 100,
                "y": 150,
                "width": 120,
                "height": 80,
                "resources": {"food": 3, "medicine": 1},
                "risk": 20
            },
            {
                "name": "House 2",
                "x": 300,
                "y": 200,
                "width": 120,
                "height": 80,
                "resources": {"food": 2, "wood": 3},
                "risk": 15
            },
            {
                "name": "Police Station",
                "x": 500,
                "y": 150,
                "width": 150,
                "height": 100,
                "resources": {"ammo": 10, "medicine": 2, "weapon": 1},
                "risk": 40
            },
            {
                "name": "Hardware Store",
                "x": 200,
                "y": 350,
                "width": 140,
                "height": 90,
                "resources": {"wood": 8, "metal": 5, "tools": 2},
                "risk": 25
            },
            {
                "name": "Pharmacy",
                "x": 450,
                "y": 300,
                "width": 130,
                "height": 80,
                "resources": {"medicine": 8, "food": 1},
                "risk": 30
            },
            {
                "name": "Grocery Store",
                "x": 700,
                "y": 250,
                "width": 160,
                "height": 100,
                "resources": {"food": 12, "water": 8},
                "risk": 35
            },
            {
                "name": "Gas Station",
                "x": 650,
                "y": 400,
                "width": 120,
                "height": 80,
                "resources": {"fuel": 5, "food": 3},
                "risk": 20
            },
            {
                "name": "Hospital",
                "x": 350,
                "y": 450,
                "width": 180,
                "height": 120,
                "resources": {"medicine": 15, "food": 2},
                "risk": 60
            }
        ]
        
        # Create Location objects
        for loc_data in locations_data:
            location = Location(
                loc_data["name"],
                loc_data["x"],
                loc_data["y"],
                loc_data["width"],
                loc_data["height"],
                loc_data["resources"],
                loc_data["risk"]
            )
            self.locations.append(location)
    
    def update(self, mouse_pos, mouse_clicked):
        # Reset all highlights
        for location in self.locations:
            location.highlighted = False
        
        # If showing result, update timer
        if self.showing_result:
            self.result_timer += 1/60  # Assuming 60 FPS
            if self.result_timer >= self.result_duration:
                self.showing_result = False
                self.result_timer = 0
            return False  # No day end while showing results
        
        # Check for mouse over and clicks
        for location in self.locations:
            if location.is_mouse_over(mouse_pos):
                location.highlighted = True
                
                if mouse_clicked and not location.visited and self.visits_remaining > 0:
                    result = location.visit()
                    self.showing_result = True
                    self.result_data = result
                    self.visits_remaining -= 1
                    return False  # Day not over yet
        
        # Check if day should end (no more visits or all locations visited)
        if self.visits_remaining <= 0 or all(loc.visited for loc in self.locations):
            return True  # Day is over
        
        return False  # Day continues
    
    def render(self, screen, mouse_pos):
        # Draw city background
        screen.fill((200, 200, 200))  # Light gray background
        
        # Draw some simple roads
        pygame.draw.rect(screen, (50, 50, 50), (50, 300, self.width - 100, 30))  # Horizontal road
        pygame.draw.rect(screen, (50, 50, 50), (400, 100, 30, self.height - 200))  # Vertical road
        
        # Draw locations
        for location in self.locations:
            location.render(screen, self.font)
        
        # Draw tooltips for highlighted locations
        for location in self.locations:
            if location.highlighted:
                location.render_tooltip(screen, self.font, mouse_pos)
        
        # Draw UI elements
        title = self.title_font.render("Scavenging Phase - Choose locations to visit", True, (0, 0, 0))
        screen.blit(title, (self.width//2 - title.get_width()//2, 20))
        
        visits_text = self.font.render(f"Visits remaining today: {self.visits_remaining}", True, (0, 0, 0))
        screen.blit(visits_text, (20, 60))
        
        if self.visits_remaining <= 0:
            end_text = self.font.render("No more visits available. Night is coming...", True, (200, 0, 0))
            screen.blit(end_text, (self.width//2 - end_text.get_width()//2, 60))
        
        # Draw result popup if showing
        if self.showing_result:
            self.render_result(screen)
    
    def render_result(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Create result box
        box_width = 500
        box_height = 300
        box_x = self.width//2 - box_width//2
        box_y = self.height//2 - box_height//2
        
        pygame.draw.rect(screen, (240, 240, 240), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 3)
        
        # Draw result content
        if self.result_data["bitten"]:
            title = self.title_font.render("Oh no! You were bitten!", True, (200, 0, 0))
        else:
            title = self.title_font.render("Scavenging Successful!", True, (0, 100, 0))
        
        screen.blit(title, (self.width//2 - title.get_width()//2, box_y + 20))
        
        # Draw resources gathered
        y_offset = box_y + 80
        if self.result_data["resources"]:
            resource_title = self.result_font.render("Resources gathered:", True, (0, 0, 0))
            screen.blit(resource_title, (box_x + 30, y_offset))
            y_offset += 40
            
            for resource, amount in self.result_data["resources"].items():
                text = self.font.render(f"- {resource}: {amount}", True, (0, 0, 0))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 30
        else:
            no_resources = self.result_font.render("No resources found!", True, (150, 0, 0))
            screen.blit(no_resources, (box_x + 30, y_offset))
        
        # Draw continue message
        continue_text = self.font.render("Click to continue...", True, (100, 100, 100))
        screen.blit(continue_text, (self.width//2 - continue_text.get_width()//2, box_y + box_height - 40))
    
    def reset_for_new_day(self):
        """Reset the map for a new day"""
        for location in self.locations:
            location.visited = False
        self.visits_remaining = 3
        self.showing_result = False
        self.result_data = None
        self.result_timer = 0
    
    def get_scavenged_resources(self):
        """Return a dictionary of all resources gathered today"""
        resources = {}
        for location in self.locations:
            if not location.visited:
                continue
                
            # This is a simplification - in a real implementation, 
            # you'd track the actual resources gathered from each visit
            for resource, max_amount in location.resources.items():
                if resource not in resources:
                    resources[resource] = 0
                # Add a random amount between 40-100% of max
                amount = int(max_amount * (0.4 + 0.6 * random.random()))
                resources[resource] += amount
        
        return resources
