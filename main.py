#!/usr/bin/env python3
"""
Zombie Survival Game - A 2D platformer with day/night cycle
- Daytime: Scavenge for resources
- Nighttime: Defend against zombie hordes
"""
import sys
import pygame
from src.game import Game

def main():
    # Initialize pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    
    # Run the game
    game.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
