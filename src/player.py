import pygame
import math

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 15
        self.damage = 25
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
        self.ammo = 30
        self.max_ammo = 30
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 10  # frames between shots
        
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
            if event.key == pygame.K_r:
                self.reload()
        
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
    
    def update(self):
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
        dy = self.velocity_y
        
        # Ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > 1024:  # Assuming screen width is 1024
            dx = 1024 - self.rect.right
        
        # Simple ground collision (assuming ground is at y=700)
        if self.rect.bottom + dy > 700:
            dy = 700 - self.rect.bottom
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Update position
        self.rect.x += dx
        self.rect.y += dy
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Handle shooting
        if self.shooting and self.shoot_cooldown <= 0 and self.ammo > 0:
            self.shoot()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullets that go off screen
            if (bullet.x < 0 or bullet.x > 1024 or 
                bullet.y < 0 or bullet.y > 768):
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
        self.ammo -= 1
    
    def reload(self):
        self.ammo = self.max_ammo
    
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
    
    def render(self, screen):
        # Draw player
        if self.facing_right:
            pygame.draw.rect(screen, (0, 0, 255), self.rect)
        else:
            pygame.draw.rect(screen, (0, 0, 200), self.rect)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.render(screen)
