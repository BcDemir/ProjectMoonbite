#!/bin/bash

echo "Checking for pygame installation..."

# Check if pygame is installed
if ! python3 -c "import pygame" &> /dev/null; then
    echo "Pygame is not installed. Attempting to install..."
    pip3 install pygame || {
        echo "Failed to install pygame with pip3. Trying with pip..."
        pip install pygame || {
            echo "Failed to install pygame. Please install it manually with:"
            echo "pip install pygame"
            exit 1
        }
    }
    echo "Pygame installed successfully!"
else
    echo "Pygame is already installed."
fi

echo "Starting Zombie Survival Game..."
python3 main.py
