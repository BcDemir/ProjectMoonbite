# ProjectMoonbite

I started with the following prompt:

```bash
i want to develop a game with pygame which is a 2d platformer where you defend zombie hordes at night. You will scavange for resources at daytime. The night should be an arcade game where you shoot at incoming zombies behind cover.
```

The structure of the game in return is:

## Game Structure Overview

I've created a 2D platformer with day/night cycle mechanics as you requested:

1. Main Game Loop (main.py): Entry point that initializes pygame and runs the game

2. Game Class (game.py): Manages the game state, day/night cycle, and coordinates all game elements

3. Player Class (player.py): Handles player movement, shooting mechanics, and health

4. Zombie Class (zombie.py): Different zombie types that chase the player during night

5. Resource Class (resource.py): Resources to collect during daytime

6. World Class (world.py): Manages the game environment, platforms, and obstacles

## Game Mechanics

### Day/Night Cycle
• **Day**: Focus on exploration and resource gathering
• **Night**: Defend against zombie hordes with shooting mechanics
• The cycle automatically switches after a set duration

### Gameplay Elements
• **Player Movement**: Platform-based movement with jumping
• **Combat**: Mouse-aimed shooting with limited ammo
• **Resources**: Collect different types during day (wood, metal, food, medicine)
• **Zombies**: Different types attack at night (normal, fast, tank)
• **Cover**: Use obstacles for protection during night battles

## Running the Game

To run the game, you'll need to install pygame first:

bash
pip install pygame
python3 main.py


## Next Steps for Development

1. Graphics: Replace the simple rectangles with proper sprites
   • Create player animations for walking, jumping, shooting
   • Design zombie sprites with animations
   • Add resource and environment graphics

2. Sound Effects:
   • Add shooting sounds
   • Zombie groans
   • Resource collection sounds
   • Day/night transition sounds

3. Game Mechanics Expansion:
   • Add a building system to create defenses for night
   • Implement a crafting system using collected resources
   • Add weapon upgrades and different weapon types
   • Create a progression system with unlockable abilities

4. UI Improvements:
   • Add a proper menu system
   • Create a tutorial
   • Implement a minimap
   • Add visual indicators for day/night transitions

5. Game Balance:
   • Adjust difficulty progression
   • Balance resource spawning
   • Fine-tune zombie behavior and spawn rates

The code structure is modular, so you can easily extend any part of the game. For example, to add new zombie
types, you can simply add new options in the Zombie class.

There was an issue with starting to game so i asked to fix it which fixed the issue.

```bash
I need to change the day time game. The day time should be a map of a small city. The player can choose places to visit such as homes, police station, hardware store etc. Once the mouse is on top of a place, it should highlight what can be scavenged and the risk of getting bit by zombies. Once the player clicked on a place, it will show the end results such as if the player is bit, the things they scavenged. Then the night game starts.
```

**- This prompt lead to an error where the AI stuck at some point so I have to revert and ask a simpler prompt.**

- From this point forward, I used simpler prompts and step by step approach. I modified small parts of the game to reach the final game I wanted to develop.