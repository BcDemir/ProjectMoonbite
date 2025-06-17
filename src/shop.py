import pygame

class ShopItem:
    def __init__(self, name, description, cost, effect_func, max_level=None, current_level=0):
        self.name = name
        self.description = description
        self.cost = cost  # Can be a function that takes level as input
        self.effect_func = effect_func  # Function to call when purchased
        self.max_level = max_level  # None means unlimited
        self.current_level = current_level
    
    def get_cost(self):
        """Get the cost at the current level"""
        if callable(self.cost):
            return self.cost(self.current_level)
        return self.cost
    
    def can_purchase(self, resources):
        """Check if player has enough resources to purchase"""
        if self.max_level is not None and self.current_level >= self.max_level:
            return False
        return resources >= self.get_cost()
    
    def purchase(self, resources):
        """Attempt to purchase the item"""
        if not self.can_purchase(resources):
            return resources, False
        
        # Get the cost before applying the upgrade
        cost = self.get_cost()
        
        # Apply effect
        self.effect_func()
        
        # Increment level if applicable
        if self.max_level is not None:
            self.current_level += 1
        
        # Deduct the stored cost
        return resources - cost, True

class Shop:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.resources = 0
        self.player = None
        self.barricade = None
        
        # Shop UI
        self.title_font = pygame.font.SysFont(None, 48)
        self.item_font = pygame.font.SysFont(None, 36)
        self.desc_font = pygame.font.SysFont(None, 24)
        
        # Shop items
        self.items = []
        self.selected_item = 0
        self.current_category = 0
        self.category_items = {}
        
        # Category names
        self.categories = ["Ammo", "Barricade", "Weapons", "Upgrades"]
        
        # Buttons
        self.buttons = {
            "prev_cat": pygame.Rect(20, self.height - 60, 100, 40),
            "next_cat": pygame.Rect(140, self.height - 60, 100, 40),
            "buy": pygame.Rect(self.width - 120, self.height - 60, 100, 40),
            "exit": pygame.Rect(self.width // 2 - 50, self.height - 60, 100, 40)
        }
    
    def open(self, player, barricade, resources):
        """Open the shop with current player stats"""
        self.active = True
        self.resources = resources
        self.player = player
        self.barricade = barricade
        self.setup_items()
        self.selected_item = 0
        self.current_category = 0
        
        # Print debug info about current weapon
        current_weapon = self.player.current_weapon
        print(f"Current weapon: {current_weapon}")
        print(f"Has shotgun: {self.player.has_shotgun}")
        print(f"Has rifle: {self.player.has_rifle}")
        print(f"Has machine gun: {self.player.has_machine_gun}")
    
    def close(self):
        """Close the shop and return to game"""
        self.active = False
        return self.resources
    
    def setup_items(self):
        """Set up shop items based on player's current stats"""
        self.items = []
        
        # Ammo items
        ammo_items = [
            ShopItem(
                "10 Bullets", 
                "Add 10 bullets to your ammo supply", 
                10, 
                lambda: setattr(self.player, "ammo_total", self.player.ammo_total + 10)
            ),
            ShopItem(
                "25 Bullets", 
                "Add 25 bullets to your ammo supply", 
                20, 
                lambda: setattr(self.player, "ammo_total", self.player.ammo_total + 25)
            ),
            ShopItem(
                "50 Bullets", 
                "Add 50 bullets to your ammo supply", 
                35, 
                lambda: setattr(self.player, "ammo_total", self.player.ammo_total + 50)
            )
        ]
        
        # Barricade items
        barricade_items = [
            ShopItem(
                "Repair Barricade", 
                "Restore barricade health by 25%", 
                15, 
                lambda: setattr(self.barricade, "health", min(self.barricade.max_health, self.barricade.health + self.barricade.max_health * 0.25))
            ),
            ShopItem(
                "Reinforce Barricade", 
                "Increase maximum barricade health by 10%", 
                lambda level: 20 + level * 10, 
                lambda: self._upgrade_barricade_max_health(0.1),
                max_level=5,
                current_level=0
            ),
            ShopItem(
                "Steel Plating", 
                "Reduce damage taken by barricade by 10%", 
                lambda level: 25 + level * 15, 
                lambda: self._add_barricade_damage_reduction(0.1),
                max_level=3,
                current_level=0
            )
        ]
        
        # Get weapon stats for descriptions
        pistol_stats = self.player.weapon_stats["pistol"]
        shotgun_stats = self.player.weapon_stats["shotgun"]
        rifle_stats = self.player.weapon_stats["rifle"]
        machine_gun_stats = self.player.weapon_stats["machine_gun"]
        
        # Format weapon stats for display
        def format_weapon_stats(stats):
            damage = stats["damage"]
            fire_rate = round(60 / stats["cooldown"], 1)  # Convert cooldown frames to shots per second
            mag_size = stats["magazine_size"]
            reload = round(stats["reload_time"] / 60, 1)  # Convert frames to seconds
            
            return f"DMG: {damage} | Fire Rate: {fire_rate}/s | Mag: {mag_size} | Reload: {reload}s"
        
        # Weapon items (new weapons)
        weapon_items = [
            ShopItem(
                "Shotgun", 
                f"Short range but hits multiple zombies\n{format_weapon_stats(shotgun_stats)}", 
                50, 
                lambda: self._unlock_weapon("shotgun"),
                max_level=1,
                current_level=0 if not hasattr(self.player, "has_shotgun") or not self.player.has_shotgun else 1
            ),
            ShopItem(
                "Rifle", 
                f"Higher damage and longer range\n{format_weapon_stats(rifle_stats)}", 
                75, 
                lambda: self._unlock_weapon("rifle"),
                max_level=1,
                current_level=0 if not hasattr(self.player, "has_rifle") or not self.player.has_rifle else 1
            ),
            ShopItem(
                "Machine Gun", 
                f"Rapid fire with larger magazine\n{format_weapon_stats(machine_gun_stats)}", 
                100, 
                lambda: self._unlock_weapon("machine_gun"),
                max_level=1,
                current_level=0 if not hasattr(self.player, "has_machine_gun") or not self.player.has_machine_gun else 1
            )
        ]
        
        # Upgrade items (for current weapon)
        upgrade_items = [
            ShopItem(
                "Faster Reload", 
                "Decrease reload time by 15%", 
                lambda level: 15 + level * 10, 
                lambda: self._upgrade_reload_speed(0.15),
                max_level=3,
                current_level=getattr(self.player, "reload_speed_level", 0)
            ),
            ShopItem(
                "Larger Magazine", 
                "Increase magazine size by 2", 
                lambda level: 20 + level * 15, 
                lambda: self._upgrade_magazine_size(2),
                max_level=4,
                current_level=getattr(self.player, "magazine_size_level", 0)
            ),
            ShopItem(
                "Increased Damage", 
                "Increase bullet damage by 20%", 
                lambda level: 25 + level * 20, 
                lambda: self._upgrade_bullet_damage(0.2),
                max_level=3,
                current_level=getattr(self.player, "damage_level", 0)
            ),
            ShopItem(
                "Faster Fire Rate", 
                "Decrease time between shots by 15%", 
                lambda level: 20 + level * 15, 
                lambda: self._upgrade_fire_rate(0.15),
                max_level=3,
                current_level=getattr(self.player, "fire_rate_level", 0)
            )
        ]
        
        # Organize items by category
        self.category_items = {
            0: ammo_items,
            1: barricade_items,
            2: weapon_items,
            3: upgrade_items
        }
        
        # Set initial items
        self.items = self.category_items[self.current_category]
    
    def _upgrade_barricade_max_health(self, percent):
        """Increase barricade max health"""
        self.barricade.max_health *= (1 + percent)
        self.barricade.health *= (1 + percent)
    
    def _add_barricade_damage_reduction(self, percent):
        """Add damage reduction to barricade"""
        if not hasattr(self.barricade, "damage_reduction"):
            self.barricade.damage_reduction = 0
        self.barricade.damage_reduction += percent
    
    def _unlock_weapon(self, weapon_type):
        """Unlock a new weapon"""
        if weapon_type == "shotgun":
            self.player.has_shotgun = True
            # Switch to the new weapon immediately
            self.player.switch_weapon("shotgun")
        elif weapon_type == "rifle":
            self.player.has_rifle = True
            # Switch to the new weapon immediately
            self.player.switch_weapon("rifle")
        elif weapon_type == "machine_gun":
            self.player.has_machine_gun = True
            # Switch to the new weapon immediately
            self.player.switch_weapon("machine_gun")
    
    def _upgrade_reload_speed(self, percent):
        """Upgrade reload speed"""
        self.player.reload_speed_level += 1
        self.player.reload_time *= (1 - percent)
    
    def _upgrade_magazine_size(self, amount):
        """Upgrade magazine size"""
        self.player.magazine_size_level += 1
        self.player.magazine_size += amount
    
    def _upgrade_bullet_damage(self, percent):
        """Upgrade bullet damage"""
        self.player.damage_level += 1
    
    def _upgrade_fire_rate(self, percent):
        """Upgrade fire rate"""
        self.player.fire_rate_level += 1
        self.player.shoot_cooldown_max *= (1 - percent)
    
    def handle_event(self, event):
        """Handle shop events"""
        if not self.active:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on a button
                mouse_pos = pygame.mouse.get_pos()
                
                # Previous category button
                if self.buttons["prev_cat"].collidepoint(mouse_pos):
                    self.current_category = (self.current_category - 1) % len(self.categories)
                    self.items = self.category_items[self.current_category]
                    self.selected_item = 0
                    return True
                
                # Next category button
                elif self.buttons["next_cat"].collidepoint(mouse_pos):
                    self.current_category = (self.current_category + 1) % len(self.categories)
                    self.items = self.category_items[self.current_category]
                    self.selected_item = 0
                    return True
                
                # Exit button
                elif self.buttons["exit"].collidepoint(mouse_pos):
                    self.active = False
                    return True
                
                # Buy button
                elif self.buttons["buy"].collidepoint(mouse_pos):
                    if 0 <= self.selected_item < len(self.items):
                        item = self.items[self.selected_item]
                        if item.can_purchase(self.resources):
                            self.resources, success = item.purchase(self.resources)
                    return True
                
                # Check if clicked on an item
                item_y = 200  # Starting y position for items
                for i, item in enumerate(self.items):
                    item_height = 80 if self.current_category == 2 else 60
                    item_rect = pygame.Rect(self.width // 4, item_y, self.width // 2, item_height)
                    if item_rect.collidepoint(mouse_pos):
                        self.selected_item = i
                        return True
                    # Adjust spacing based on item height
                    item_spacing = 90 if self.current_category == 2 else 70
                    item_y += item_spacing
        
        elif event.type == pygame.KEYDOWN:
            # Navigation
            if event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_item = min(len(self.items) - 1, self.selected_item + 1)
                return True
            elif event.key == pygame.K_LEFT:
                self.current_category = (self.current_category - 1) % len(self.categories)
                self.items = self.category_items[self.current_category]
                self.selected_item = 0
                return True
            elif event.key == pygame.K_RIGHT:
                self.current_category = (self.current_category + 1) % len(self.categories)
                self.items = self.category_items[self.current_category]
                self.selected_item = 0
                return True
            
            # Purchase
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if 0 <= self.selected_item < len(self.items):
                    item = self.items[self.selected_item]
                    if item.can_purchase(self.resources):
                        self.resources, success = item.purchase(self.resources)
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return True
        
        return False
    
    def render(self, screen):
        """Render the shop UI"""
        if not self.active:
            return
        
        # Background
        pygame.draw.rect(screen, (20, 20, 30), (0, 0, self.width, self.height))
        
        # Title
        title_text = self.title_font.render(f"Shop - {self.categories[self.current_category]}", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 20))
        
        # Resources
        resources_text = self.item_font.render(f"Resources: {self.resources}", True, (255, 255, 0))
        screen.blit(resources_text, (self.width // 2 - resources_text.get_width() // 2, 70))
        
        # Draw current weapon info
        if self.current_category == 2 or self.current_category == 3:  # Weapons or upgrades category
            current_weapon = self.player.current_weapon
            weapon_stats = self.player.weapon_stats[current_weapon]
            
            # Format weapon stats
            damage = weapon_stats["damage"]
            if self.player.damage_level > 0:
                damage *= (1 + 0.2 * self.player.damage_level)
                damage = round(damage, 1)
                
            fire_rate = round(60 / weapon_stats["cooldown"], 1)
            if self.player.fire_rate_level > 0:
                fire_rate = round(fire_rate / (1 - 0.15 * self.player.fire_rate_level), 1)
                
            mag_size = weapon_stats["magazine_size"]
            if self.player.magazine_size_level > 0:
                mag_size += self.player.magazine_size_level * 2
                
            reload_time = round(weapon_stats["reload_time"] / 60, 1)
            if self.player.reload_speed_level > 0:
                reload_time = round(reload_time * (1 - 0.15 * self.player.reload_speed_level), 1)
            
            # Draw current weapon box
            weapon_box = pygame.Rect(self.width // 4, 100, self.width // 2, 80)
            pygame.draw.rect(screen, (40, 40, 60), weapon_box)
            pygame.draw.rect(screen, (100, 100, 150), weapon_box, 2)
            
            # Draw weapon name
            weapon_name = current_weapon.replace("_", " ").title()
            name_text = self.title_font.render(f"Current Weapon: {weapon_name}", True, (200, 200, 255))
            screen.blit(name_text, (weapon_box.x + 10, weapon_box.y + 10))
            
            # Draw weapon stats
            stats_text = self.desc_font.render(f"Damage: {damage} | Fire Rate: {fire_rate}/s | Magazine: {mag_size} | Reload: {reload_time}s", True, (180, 180, 255))
            screen.blit(stats_text, (weapon_box.x + 10, weapon_box.y + 40))
            
            # Adjust starting position for items
            items_start_y = 200
        else:
            items_start_y = 150
        
        # Items
        item_y = items_start_y
        for i, item in enumerate(self.items):
            # Item background
            item_color = (50, 50, 50) if i == self.selected_item else (30, 30, 30)
            if not item.can_purchase(self.resources):
                item_color = (50, 20, 20) if i == self.selected_item else (30, 10, 10)
            
            # Make weapon items taller to accommodate stats
            item_height = 80 if self.current_category == 2 else 60
            item_rect = pygame.Rect(self.width // 4, item_y, self.width // 2, item_height)
            pygame.draw.rect(screen, item_color, item_rect)
            pygame.draw.rect(screen, (100, 100, 100), item_rect, 2)
            
            # Item name and cost
            name_text = self.item_font.render(item.name, True, (255, 255, 255))
            
            # Show level if applicable
            if item.max_level is not None:
                level_text = f" (Level {item.current_level}/{item.max_level})"
                name_text = self.item_font.render(f"{item.name}{level_text}", True, (255, 255, 255))
            
            cost_text = self.item_font.render(f"Cost: {item.get_cost()}", True, (255, 255, 0))
            
            screen.blit(name_text, (item_rect.x + 10, item_rect.y + 10))
            screen.blit(cost_text, (item_rect.right - cost_text.get_width() - 10, item_rect.y + 10))
            
            # Item description - handle multi-line descriptions
            desc_lines = item.description.split('\n')
            for i, line in enumerate(desc_lines):
                desc_text = self.desc_font.render(line, True, (200, 200, 200))
                screen.blit(desc_text, (item_rect.x + 10, item_rect.y + 35 + i * 20))
            
            # If this is a weapon, show current weapon indicator
            if self.current_category == 2:  # Weapons category
                if (item.name == "Shotgun" and self.player.current_weapon == "shotgun") or \
                   (item.name == "Rifle" and self.player.current_weapon == "rifle") or \
                   (item.name == "Machine Gun" and self.player.current_weapon == "machine_gun"):
                    equipped_text = self.desc_font.render("EQUIPPED", True, (0, 255, 0))
                    screen.blit(equipped_text, (item_rect.right - equipped_text.get_width() - 10, item_rect.y + 35))
            
            # Adjust spacing based on item height
            item_spacing = 90 if self.current_category == 2 else 70
            item_y += item_spacing
        
        # Buy button
        buy_color = (0, 100, 0) if self.items and self.selected_item < len(self.items) and self.items[self.selected_item].can_purchase(self.resources) else (100, 0, 0)
        pygame.draw.rect(screen, buy_color, self.buttons["buy"])
        pygame.draw.rect(screen, (200, 200, 200), self.buttons["buy"], 2)
        buy_text = self.item_font.render("Buy", True, (255, 255, 255))
        screen.blit(buy_text, (self.buttons["buy"].centerx - buy_text.get_width() // 2, self.buttons["buy"].centery - buy_text.get_height() // 2))
        
        # Exit button
        pygame.draw.rect(screen, (50, 50, 50), self.buttons["exit"])
        pygame.draw.rect(screen, (200, 200, 200), self.buttons["exit"], 2)
        exit_text = self.item_font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (self.buttons["exit"].centerx - exit_text.get_width() // 2, self.buttons["exit"].centery - exit_text.get_height() // 2))
        
        # Category navigation buttons
        pygame.draw.rect(screen, (50, 50, 50), self.buttons["prev_cat"])
        pygame.draw.rect(screen, (200, 200, 200), self.buttons["prev_cat"], 2)
        prev_text = self.item_font.render("< Prev", True, (255, 255, 255))
        screen.blit(prev_text, (self.buttons["prev_cat"].centerx - prev_text.get_width() // 2, self.buttons["prev_cat"].centery - prev_text.get_height() // 2))
        
        pygame.draw.rect(screen, (50, 50, 50), self.buttons["next_cat"])
        pygame.draw.rect(screen, (200, 200, 200), self.buttons["next_cat"], 2)
        next_text = self.item_font.render("Next >", True, (255, 255, 255))
        screen.blit(next_text, (self.buttons["next_cat"].centerx - next_text.get_width() // 2, self.buttons["next_cat"].centery - next_text.get_height() // 2))
