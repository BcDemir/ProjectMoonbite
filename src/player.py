import pygame
import math
import random
from src.assets import Assets

class Bullet:
    def __init__(self, x, y, direction, damage=10, speed=15, size=3):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.size = size
        self.active = True
        self.rect = pygame.Rect(x, y, size*2, size*2)
    
    def update(self):
        # Move bullet in direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.rect.x = self.x
        self.rect.y = self.y
    
    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.size)

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
        
        # Weapon system
        self.current_weapon = "pistol"
        self.has_shotgun = False
        self.has_rifle = False
        self.has_machine_gun = False
        
        # Weapon stats
        self.weapon_stats = {
            "pistol": {
                "damage": 10,
                "magazine_size": 10,
                "reload_time": 60,  # frames
                "cooldown": 15,     # frames between shots
                "bullet_speed": 15,
                "bullet_size": 3,
                "base_accuracy": 0.85,  # Base accuracy (0-1)
                "accuracy_dropoff": 0.4  # How much accuracy drops at max distance
            },
            "shotgun": {
                "damage": 8,
                "magazine_size": 6,
                "reload_time": 90,
                "cooldown": 30,
                "bullet_speed": 12,
                "bullet_size": 4,
                "spread": 5,        # number of pellets
                "spread_angle": 0.3,  # radians
                "base_accuracy": 0.7,  # Lower base accuracy
                "accuracy_dropoff": 0.6  # Severe accuracy drop at range
            },
            "rifle": {
                "damage": 25,
                "magazine_size": 8,
                "reload_time": 75,
                "cooldown": 20,
                "bullet_speed": 20,
                "bullet_size": 3,
                "base_accuracy": 0.95,  # High base accuracy
                "accuracy_dropoff": 0.2  # Minimal accuracy drop at range
            },
            "machine_gun": {
                "damage": 8,
                "magazine_size": 30,
                "reload_time": 120,
                "cooldown": 5,
                "bullet_speed": 15,
                "bullet_size": 2,
                "base_accuracy": 0.75,  # Lower accuracy due to rapid fire
                "accuracy_dropoff": 0.5  # Significant accuracy drop at range
            }
        }
        
        # Initialize with pistol stats
        self.bullet_damage = self.weapon_stats["pistol"]["damage"]
        self.magazine_size = self.weapon_stats["pistol"]["magazine_size"]
        self.magazine_current = self.magazine_size
        self.reload_time = self.weapon_stats["pistol"]["reload_time"]
        self.shoot_cooldown_max = self.weapon_stats["pistol"]["cooldown"]
        
        # Ammo
        self.ammo_total = 30
        self.bullets = []
        self.shoot_cooldown = 0
        self.reloading = False
        self.reload_timer = 0
        
        # Upgrade levels
        self.reload_speed_level = 0
        self.magazine_size_level = 0
        self.damage_level = 0
        self.fire_rate_level = 0
        
        # Controls
        self.moving_left = False
        self.moving_right = False
        self.shooting = False
        
        # Visual elements
        self.assets = Assets()
        self.aim_angle = 0  # Angle in radians
        self.arm_offset = (20, 30)  # Offset from player center
        
        # Animation
        self.muzzle_flash_active = False
        self.muzzle_flash_frame = 0
        self.muzzle_flash_duration = 3  # frames per animation frame
        self.muzzle_flash_timer = 0
        self.muzzle_flash_position = (0, 0)
    
    def calculate_weapon_tip(self, base_x, base_y):
        """Calculate the position of the weapon tip based on arm position and aim angle"""
        arm_length = 20  # Length of arm
        weapon_length = 30  # Length of weapon barrel
        
        # Calculate weapon tip position
        weapon_tip_x = base_x + math.cos(self.aim_angle) * (arm_length + weapon_length)
        weapon_tip_y = base_y + math.sin(self.aim_angle) * (arm_length + weapon_length)
        
        return weapon_tip_x, weapon_tip_y
    
    def switch_weapon(self, weapon_name):
        """Switch to a different weapon if available"""
        if weapon_name == "pistol" or \
           (weapon_name == "shotgun" and self.has_shotgun) or \
           (weapon_name == "rifle" and self.has_rifle) or \
           (weapon_name == "machine_gun" and self.has_machine_gun):
            
            # Save current magazine for old weapon
            old_weapon = self.current_weapon
            
            # Switch weapon
            self.current_weapon = weapon_name
            
            # Update weapon stats
            stats = self.weapon_stats[weapon_name]
            self.bullet_damage = stats["damage"]
            self.magazine_size = stats["magazine_size"]
            
            # Apply upgrades
            if self.magazine_size_level > 0:
                self.magazine_size += self.magazine_size_level * 2
            
            self.magazine_current = min(self.magazine_size, self.ammo_total)
            self.reload_time = stats["reload_time"]
            
            # Apply reload speed upgrade
            if self.reload_speed_level > 0:
                self.reload_time *= (1 - 0.15 * self.reload_speed_level)
            
            self.shoot_cooldown_max = stats["cooldown"]
            
            # Apply fire rate upgrade
            if self.fire_rate_level > 0:
                self.shoot_cooldown_max *= (1 - 0.15 * self.fire_rate_level)
            
            return True
        
        return False
    
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
            
            # Weapon switching
            if event.key == pygame.K_1:
                self.switch_weapon("pistol")
            if event.key == pygame.K_2 and self.has_shotgun:
                self.switch_weapon("shotgun")
            if event.key == pygame.K_3 and self.has_rifle:
                self.switch_weapon("rifle")
            if event.key == pygame.K_4 and self.has_machine_gun:
                self.switch_weapon("machine_gun")
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.moving_left = False
            if event.key == pygame.K_d:
                self.moving_right = False
        
        # Mouse controls for shooting
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.shooting = True
                # Return a signal that shooting has started
                return "shooting_started"
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.shooting = False
                
        return None
    
    def update(self, world, allow_movement=True):
        # Reset movement
        dx = 0
        
        # Apply movement based on controls if movement is allowed
        if allow_movement:
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
        
        # Update aim angle based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculate direction to mouse from player center
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.aim_angle = math.atan2(dy, dx)
        
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
            self.shoot()  # Always allow shooting regardless of movement
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullets that go off screen or out of world bounds
            if (bullet.x < 0 or bullet.x > world.width or 
                bullet.y < 0 or bullet.y > world.height):
                self.bullets.remove(bullet)
        
        # Update muzzle flash animation
        if self.muzzle_flash_active:
            self.muzzle_flash_timer += 1
            if self.muzzle_flash_timer >= self.muzzle_flash_duration:
                self.muzzle_flash_timer = 0
                self.muzzle_flash_frame += 1
                if self.muzzle_flash_frame >= 3:  # 3 frames of animation
                    self.muzzle_flash_active = False
                    self.muzzle_flash_frame = 0
    
    def jump(self):
        self.velocity_y = -self.jump_power
        self.on_ground = False
    
    def get_accuracy(self, distance):
        """Calculate accuracy based on weapon and distance"""
        # Get weapon stats
        stats = self.weapon_stats[self.current_weapon]
        
        # Get base accuracy for current weapon
        base_accuracy = stats.get("base_accuracy", 0.8)
        accuracy_dropoff = stats.get("accuracy_dropoff", 0.4)
        
        # Adjust for distance
        max_accurate_distance = {
            "pistol": 300,
            "shotgun": 150,
            "rifle": 500,
            "smg": 250,
            "machine_gun": 250
        }
        
        # Get max accurate distance for current weapon
        max_dist = max_accurate_distance.get(self.current_weapon, 300)
        
        # Calculate distance penalty
        if distance > max_dist:
            # Accuracy drops off after max distance
            distance_factor = min(1.0, max_dist / distance)
            # Apply accuracy dropoff based on weapon type
            accuracy = base_accuracy - ((1.0 - distance_factor) * accuracy_dropoff)
        else:
            # Within effective range, use base accuracy
            accuracy = base_accuracy
        
        # Apply accuracy upgrade if player has it
        if hasattr(self, 'accuracy_level') and self.accuracy_level > 0:
            # Each level improves accuracy by 5% (up to maximum of 1.0)
            accuracy = min(1.0, accuracy + (0.05 * self.accuracy_level))
        
        return max(0.3, accuracy)  # Minimum accuracy of 30%
    
    def shoot(self):
        # Get mouse position for aiming (this is the crosshair center)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate direction and distance to mouse/crosshair
        dx = mouse_x - (self.rect.centerx)
        dy = mouse_y - (self.rect.centery)
        distance = math.sqrt(dx*dx + dy*dy)
        direction = math.atan2(dy, dx)
        
        # Calculate accuracy based on distance
        accuracy = self.get_accuracy(distance)
        
        # Update aim angle
        self.aim_angle = direction
        
        # Get weapon stats
        stats = self.weapon_stats[self.current_weapon]
        damage = stats["damage"]
        
        # Apply damage upgrade
        if self.damage_level > 0:
            damage *= (1 + 0.2 * self.damage_level)
        
        # Calculate arm position (matching the render method)
        arm_x = self.rect.centerx
        arm_y = self.rect.centery - 10  # Slightly above center
        
        # Calculate weapon tip position (where bullets spawn)
        weapon_tip_x, weapon_tip_y = self.calculate_weapon_tip(arm_x, arm_y)
        
        # Set muzzle flash position
        self.muzzle_flash_position = (weapon_tip_x, weapon_tip_y)
        self.muzzle_flash_active = True
        self.muzzle_flash_frame = 0
        
        # Play sound effect
        self.assets.play_sound(self.current_weapon)
        
        # Calculate inaccuracy angle based on accuracy
        max_inaccuracy = (1.0 - accuracy) * 0.2  # Up to 0.2 radians (about 11.5 degrees) of inaccuracy at lowest accuracy
        
        # Create bullet(s) based on weapon type
        if self.current_weapon == "shotgun":
            # Create multiple pellets with spread
            for i in range(stats["spread"]):
                # Base spread for shotgun
                spread_direction = direction - stats["spread_angle"]/2 + stats["spread_angle"] * i/(stats["spread"]-1)
                
                # Add additional random spread based on accuracy
                if accuracy < 1.0:
                    # More random spread for shotgun
                    random_spread = random.uniform(-max_inaccuracy * 1.5, max_inaccuracy * 1.5)
                    spread_direction += random_spread
                
                # Calculate bullet direction to hit the crosshair center
                # This adjusts the trajectory based on the weapon tip position
                bullet = self.create_bullet_aimed_at_target(
                    weapon_tip_x, 
                    weapon_tip_y,
                    mouse_x,
                    mouse_y,
                    spread_direction,
                    damage,
                    stats["bullet_speed"],
                    stats["bullet_size"]
                )
                self.bullets.append(bullet)
        else:
            # Create a single bullet with accuracy-based spread
            actual_direction = direction
            
            # Add random spread based on accuracy
            if accuracy < 1.0:
                random_spread = random.uniform(-max_inaccuracy, max_inaccuracy)
                actual_direction += random_spread
            
            # Calculate bullet direction to hit the crosshair center
            bullet = self.create_bullet_aimed_at_target(
                weapon_tip_x, 
                weapon_tip_y,
                mouse_x,
                mouse_y,
                actual_direction,
                damage,
                stats["bullet_speed"],
                stats["bullet_size"]
            )
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
        self.assets.play_sound("reload")
    
    def finish_reload(self):
        """Complete the reload process"""
        if not self.reloading:
            return
        
        # Calculate how many bullets to add to magazine
        bullets_needed = self.magazine_size - self.magazine_current
        bullets_to_add = min(bullets_needed, self.ammo_total)
        
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
            
            # Get arm and weapon images
            rotated_arm, rotated_weapon = self.assets.get_rotated_arm_and_weapon(self.current_weapon, self.aim_angle)
            
            # Calculate arm position
            arm_x = player_rect.centerx
            arm_y = player_rect.centery - 10  # Slightly above center
            
            # Draw arm
            arm_rect = rotated_arm.get_rect(center=(arm_x, arm_y))
            screen.blit(rotated_arm, arm_rect)
            
            # Draw weapon
            weapon_offset_x = math.cos(self.aim_angle) * 20
            weapon_offset_y = math.sin(self.aim_angle) * 20
            weapon_rect = rotated_weapon.get_rect(center=(arm_x + weapon_offset_x, arm_y + weapon_offset_y))
            screen.blit(rotated_weapon, weapon_rect)
            
            # Draw muzzle flash if active
            if self.muzzle_flash_active:
                flash = self.assets.get_muzzle_flash(self.muzzle_flash_frame)
                if flash:
                    # Calculate muzzle position (at the tip of the weapon)
                    weapon_tip_x, weapon_tip_y = self.calculate_weapon_tip(arm_x, arm_y)
                    flash_rect = flash.get_rect(center=(weapon_tip_x, weapon_tip_y))
                    screen.blit(flash, flash_rect)
            
            # Draw weapon indicator
            weapon_color = (255, 255, 0)  # Yellow for pistol
            if self.current_weapon == "shotgun":
                weapon_color = (255, 165, 0)  # Orange
            elif self.current_weapon == "rifle":
                weapon_color = (0, 255, 0)  # Green
            elif self.current_weapon == "machine_gun":
                weapon_color = (255, 0, 0)  # Red
            
            pygame.draw.circle(screen, weapon_color, 
                              (player_rect.centerx, player_rect.centery), 5)
            
            # Draw bullets
            for bullet in self.bullets:
                bullet_x, bullet_y = camera.apply_point(bullet.x, bullet.y)
                pygame.draw.circle(screen, (255, 255, 0), (int(bullet_x), int(bullet_y)), bullet.size)
            
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
            
            # Get arm and weapon images
            rotated_arm, rotated_weapon = self.assets.get_rotated_arm_and_weapon(self.current_weapon, self.aim_angle)
            
            # Calculate arm position
            arm_x = self.rect.centerx
            arm_y = self.rect.centery - 10  # Slightly above center
            
            # Draw arm
            arm_rect = rotated_arm.get_rect(center=(arm_x, arm_y))
            screen.blit(rotated_arm, arm_rect)
            
            # Draw weapon
            weapon_offset_x = math.cos(self.aim_angle) * 20
            weapon_offset_y = math.sin(self.aim_angle) * 20
            weapon_rect = rotated_weapon.get_rect(center=(arm_x + weapon_offset_x, arm_y + weapon_offset_y))
            screen.blit(rotated_weapon, weapon_rect)
            
            # Draw muzzle flash if active
            if self.muzzle_flash_active:
                flash = self.assets.get_muzzle_flash(self.muzzle_flash_frame)
                if flash:
                    # Calculate muzzle position (at the tip of the weapon)
                    weapon_tip_x, weapon_tip_y = self.calculate_weapon_tip(arm_x, arm_y)
                    flash_rect = flash.get_rect(center=(weapon_tip_x, weapon_tip_y))
                    screen.blit(flash, flash_rect)
            
            # Draw weapon indicator
            weapon_color = (255, 255, 0)  # Yellow for pistol
            if self.current_weapon == "shotgun":
                weapon_color = (255, 165, 0)  # Orange
            elif self.current_weapon == "rifle":
                weapon_color = (0, 255, 0)  # Green
            elif self.current_weapon == "machine_gun":
                weapon_color = (255, 0, 0)  # Red
            
            pygame.draw.circle(screen, weapon_color, 
                              (self.rect.centerx, self.rect.centery), 5)
            
            # Draw bullets
            for bullet in self.bullets:
                pygame.draw.circle(screen, (255, 255, 0), (int(bullet.x), int(bullet.y)), bullet.size)
            
            # Draw reloading indicator if reloading
            if self.reloading:
                # Draw a circular progress indicator above player
                progress = self.reload_timer / self.reload_time
                radius = 15
                pygame.draw.arc(screen, (255, 255, 0), 
                               (self.rect.centerx - radius, self.rect.top - radius*2, radius*2, radius*2),
                               0, progress * 2 * math.pi, 3)
    def create_bullet_aimed_at_target(self, start_x, start_y, target_x, target_y, base_direction, damage, speed, size):
        """Create a bullet that will hit the target point, accounting for the offset start position"""
        # Calculate the exact direction from the weapon tip to the target (crosshair center)
        dx = target_x - start_x
        dy = target_y - start_y
        exact_direction = math.atan2(dy, dx)
        
        # Use the exact direction for the bullet trajectory
        # This ensures the bullet will hit exactly where the crosshair is
        # The base_direction parameter is used for applying spread/inaccuracy
        
        # Calculate final direction by applying spread to the exact direction
        spread_offset = base_direction - math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        final_direction = exact_direction + spread_offset
        
        # Create the bullet with the adjusted direction
        return Bullet(
            start_x,
            start_y,
            final_direction,
            damage=damage,
            speed=speed,
            size=size
        )
    def reset_position(self, x, y):
        """Reset player position to the specified coordinates"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.on_ground = False
    def update_bullets(self, zombies):
        """Update bullets and check for collisions with zombies"""
        # Update each bullet
        for bullet in self.bullets[:]:
            bullet.update()
            
            # Check for collisions with zombies
            hit = False
            for zombie in zombies[:]:
                if bullet.rect.colliderect(zombie.rect):
                    zombie.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    hit = True
                    break
            
            # Remove bullets that go off screen
            if not hit and (bullet.x < 0 or bullet.x > 2000 or bullet.y < 0 or bullet.y > 1000):
                self.bullets.remove(bullet)
