import pygame
import os
import math

class Assets:
    def __init__(self):
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
            os.makedirs("assets/sounds")
            os.makedirs("assets/images")
        
        # Initialize pygame mixer for sounds
        pygame.mixer.init()
        
        # Load or create weapon images
        self.weapons = {
            "pistol": self._create_weapon_image((50, 15), (150, 150, 150)),
            "shotgun": self._create_weapon_image((70, 20), (120, 100, 80)),
            "rifle": self._create_weapon_image((90, 12), (100, 100, 100)),
            "machine_gun": self._create_weapon_image((80, 18), (80, 80, 80))
        }
        
        # Load or create arm image
        self.arm = self._create_arm_image()
        
        # Create muzzle flash animation frames
        self.muzzle_flash = self._create_muzzle_flash()
        
        # Load or create sound effects
        self.sounds = self._load_sounds()
    
    def _create_weapon_image(self, size, color):
        """Create a simple weapon image"""
        surface = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
        
        # Draw weapon body
        pygame.draw.rect(surface, color, (0, 0, size[0], size[1]))
        
        # Draw barrel
        pygame.draw.rect(surface, (50, 50, 50), (size[0] - 10, size[1] // 2 - 3, 10, 6))
        
        # Draw handle
        pygame.draw.rect(surface, (80, 50, 20), (10, size[1], 15, 20))
        
        return surface
    
    def _create_arm_image(self):
        """Create a simple arm image"""
        surface = pygame.Surface((40, 15), pygame.SRCALPHA)
        
        # Draw arm (flesh color)
        pygame.draw.rect(surface, (255, 213, 170), (0, 0, 40, 15))
        
        # Add shading
        pygame.draw.rect(surface, (220, 170, 140), (0, 10, 40, 5))
        
        return surface
    
    def _create_muzzle_flash(self):
        """Create muzzle flash animation frames"""
        frames = []
        
        # Frame 1 - small flash
        surface1 = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(surface1, (255, 255, 150, 200), (15, 15), 10)
        pygame.draw.circle(surface1, (255, 200, 50, 150), (15, 15), 5)
        frames.append(surface1)
        
        # Frame 2 - medium flash
        surface2 = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(surface2, (255, 255, 150, 180), (20, 20), 15)
        pygame.draw.circle(surface2, (255, 200, 50, 130), (20, 20), 8)
        frames.append(surface2)
        
        # Frame 3 - large flash
        surface3 = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surface3, (255, 255, 150, 150), (25, 25), 20)
        pygame.draw.circle(surface3, (255, 200, 50, 100), (25, 25), 10)
        frames.append(surface3)
        
        return frames
    
    def _load_sounds(self):
        """Load or create sound effects"""
        sounds = {}
        
        # Create simple sound files if they don't exist
        self._create_sound_files()
        
        # Load sound files
        sounds["pistol"] = pygame.mixer.Sound("assets/sounds/pistol.wav")
        sounds["shotgun"] = pygame.mixer.Sound("assets/sounds/shotgun.wav")
        sounds["rifle"] = pygame.mixer.Sound("assets/sounds/rifle.wav")
        sounds["machine_gun"] = pygame.mixer.Sound("assets/sounds/machine_gun.wav")
        sounds["empty"] = pygame.mixer.Sound("assets/sounds/empty.wav")
        sounds["reload"] = pygame.mixer.Sound("assets/sounds/reload.wav")
        
        # Set volumes
        sounds["pistol"].set_volume(0.3)
        sounds["shotgun"].set_volume(0.4)
        sounds["rifle"].set_volume(0.3)
        sounds["machine_gun"].set_volume(0.2)
        sounds["empty"].set_volume(0.2)
        sounds["reload"].set_volume(0.3)
        
        return sounds
    
    def _create_sound_files(self):
        """Create simple sound files if they don't exist"""
        # This is a placeholder - in a real game, you would include actual sound files
        # For this example, we'll just check if files exist and not create them
        # as pygame doesn't have built-in sound generation capabilities
        
        sound_files = [
            "assets/sounds/pistol.wav",
            "assets/sounds/shotgun.wav",
            "assets/sounds/rifle.wav",
            "assets/sounds/machine_gun.wav",
            "assets/sounds/empty.wav",
            "assets/sounds/reload.wav"
        ]
        
        for sound_file in sound_files:
            if not os.path.exists(sound_file):
                # In a real implementation, you would include actual sound files
                # For now, we'll just print a message
                print(f"Sound file {sound_file} not found. Using default sounds.")
    
    def get_rotated_arm_and_weapon(self, weapon_type, angle):
        """Get rotated arm and weapon images based on angle"""
        # Get the weapon image
        weapon = self.weapons.get(weapon_type, self.weapons["pistol"])
        
        # Rotate weapon
        rotated_weapon = pygame.transform.rotate(weapon, -angle * 180 / math.pi)
        
        # Rotate arm
        rotated_arm = pygame.transform.rotate(self.arm, -angle * 180 / math.pi)
        
        return rotated_arm, rotated_weapon
    
    def get_muzzle_flash(self, frame):
        """Get a specific frame of the muzzle flash animation"""
        if 0 <= frame < len(self.muzzle_flash):
            return self.muzzle_flash[frame]
        return None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
