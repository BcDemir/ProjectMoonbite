import pygame
import math

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 15
        self.damage = 10  # Reduced damage to make zombies tougher
        self.active = True
        self.rect = pygame.Rect(x, y, 5, 5)
    
    def update(self):
        # Move bullet in direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.rect.x = self.x
        self.rect.y = self.y
    
    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Movement
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Combat
        self.health = 100
        self.max_health = 100
        self.magazine_size = 10  # Bullets per magazine
        self.magazine_current = 10  # Current bullets in magazine
        self.ammo_total = 30  # Total ammo (including magazine)
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 10  # frames between shots
        self.reloading = False
        self.reload_time = 60  # frames to reload (1 second at 60 FPS)
        self.reload_timer = 0
        
        # Controls
        self.moving_left = False
        self.moving_right = False
        self.shooting = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.moving_left = True
            if event.key == pygame.K_d:
                self.moving_right = True
            if event.key == pygame.K_SPACE and self.on_ground:
                self.jump()
            if event.key == pygame.K_r and not self.reloading and self.magazine_current < self.magazine_size:
                self.start_reload()
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            if event.key == pygame.K_d:
                self.moving_right = False
        
        # Mouse controls for shooting
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.shooting = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.shooting = False
    
    def update(self, world):
        # Reset movement
        dx = 0
        
        # Apply movement based on controls
        if self.moving_left:
            dx = -self.speed
            self.facing_right = False
        if self.moving_right:
            dx = self.speed
            self.facing_right = True
        
        # Apply gravity
        self.velocity_y += self.gravity
        if self.velocity_y > 15:  # Terminal velocity
            self.velocity_y = 15
        
        # Check for horizontal collisions with world boundaries
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > world.width:  # Use world width instead of screen width
            dx = world.width - self.rect.right
        
        # Update horizontal position
        self.rect.x += dx
        self.x = self.rect.x
        
        # Check for vertical collisions with platforms
        self.rect.y, self.on_ground = world.check_platform_collisions(self.rect, self.velocity_y)
        
        # Reset velocity if on ground
        if self.on_ground:
            self.velocity_y = 0
        
        self.y = self.rect.y
        
        # Check for resource collisions
        collected_resources = world.check_resource_collisions(self.rect)
        for resource_type in collected_resources:
            if resource_type == "ammo":
                self.ammo_total += 10
            elif resource_type == "health":
                self.health = min(self.max_health, self.health + 25)
            elif resource_type == "weapon":
                # Could implement weapon upgrades here
                self.ammo_total += 20
        
        # Handle reloading
        if self.reloading:
            self.reload_timer += 1
            if self.reload_timer >= self.reload_time:
                self.finish_reload()
        
        # Handle shooting
        if self.shooting and self.shoot_cooldown <= 0 and self.magazine_current > 0 and not self.reloading:
            self.shoot()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullets that go off screen or out of world bounds
            if (bullet.x < 0 or bullet.x > world.width or 
                bullet.y < 0 or bullet.y > world.height):
                self.bullets.remove(bullet)
    
    def jump(self):
        self.velocity_y = -self.jump_power
        self.on_ground = False
    
    def shoot(self):
        # Get mouse position for aiming
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate direction
        dx = mouse_x - (self.rect.centerx)
        dy = mouse_y - (self.rect.centery)
        direction = math.atan2(dy, dx)
        
        # Create bullet
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.append(bullet)
        
        # Apply cooldown and use ammo
        self.shoot_cooldown = self.shoot_cooldown_max
        self.magazine_current -= 1
    
    def start_reload(self):
        """Start the reload process"""
        if self.reloading or self.magazine_current >= self.magazine_size or self.ammo_total <= 0:
            return  # Already reloading, magazine full, or no ammo to reload
        
        self.reloading = True
        self.reload_timer = 0
    
    def finish_reload(self):
        """Complete the reload process"""
        if not self.reloading:
            return
        
        # Calculate how many bullets to add to magazine
        bullets_needed = self.magazine_size - self.magazine_current
        bullets_available = self.ammo_total - self.magazine_current
        bullets_to_add = min(bullets_needed, bullets_available)
        
        # Add bullets to magazine and subtract from total
        self.magazine_current += bullets_to_add
        self.ammo_total -= bullets_to_add
        
        self.reloading = False
        self.reload_timer = 0
    
    def reload(self):
        """Instantly reload (for compatibility with existing code)"""
        if self.magazine_current >= self.magazine_size or self.ammo_total <= 0:
            return
            
        # Calculate how many bullets to add to magazine
        bullets_needed = self.magazine_size - self.magazine_current
        bullets_to_add = min(bullets_needed, self.ammo_total)
        
        # Add bullets to magazine and subtract from total
        self.magazine_current += bullets_to_add
        self.ammo_total -= bullets_to_add
    
    def add_ammo(self, amount):
        """Add ammo to total supply"""
        self.ammo_total += amount
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
    
    def check_bullet_hits(self, target):
        for bullet in self.bullets[:]:
            if bullet.rect.colliderect(target.rect):
                target.take_damage(bullet.damage)
                self.bullets.remove(bullet)
                return True
        return False
    
    def render(self, screen, camera=None):
        # If camera is provided (day mode), apply camera offset
        if camera:
            # Draw player
            player_rect = camera.apply(self.rect)
            if self.facing_right:
                pygame.draw.rect(screen, (0, 0, 255), player_rect)
            else:
                pygame.draw.rect(screen, (0, 0, 200), player_rect)
            
            # Draw bullets
            for bullet in self.bullets:
                bullet_x, bullet_y = camera.apply_point(bullet.x, bullet.y)
                pygame.draw.circle(screen, (255, 255, 0), (int(bullet_x), int(bullet_y)), 3)
            
            # Draw reloading indicator if reloading
            if self.reloading:
                # Draw a circular progress indicator above player
                progress = self.reload_timer / self.reload_time
                radius = 15
                pygame.draw.arc(screen, (255, 255, 0), 
                               (player_rect.centerx - radius, player_rect.top - radius*2, radius*2, radius*2),
                               0, progress * 2 * math.pi, 3)
        else:
            # Night mode - no camera offset
            # Draw player
            if self.facing_right:
                pygame.draw.rect(screen, (0, 0, 255), self.rect)
            else:
                pygame.draw.rect(screen, (0, 0, 200), self.rect)
            
            # Draw bullets
            for bullet in self.bullets:
                pygame.draw.circle(screen, (255, 255, 0), (int(bullet.x), int(bullet.y)), 3)
            
            # Draw reloading indicator if reloading
            if self.reloading:
                # Draw a circular progress indicator above player
                progress = self.reload_timer / self.reload_time
                radius = 15
                pygame.draw.arc(screen, (255, 255, 0), 
                               (self.rect.centerx - radius, self.rect.top - radius*2, radius*2, radius*2),
                               0, progress * 2 * math.pi, 3)
