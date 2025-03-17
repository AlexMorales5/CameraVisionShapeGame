# CameraVisionShapeGame

# Shape Popper Game - Setup Instructions

Here's a comprehensive guide for setting up and running the Shape Popper game:

## Prerequisites

1. **Python Installation**
   - Install Python 3.7 or newer from [python.org](https://python.org)
   - During installation, make sure to check "Add Python to PATH"

2. **Required Libraries**
   - The game requires several Python libraries. Install them using pip:
   ```
   pip install opencv-python mediapipe numpy
   ```

## Installation Steps

1. **Download the Code**
   - Clone this repository or download the ZIP file
   - Extract the files to a directory of your choice

2. **Running the Game**
   - Navigate to the directory containing the game files
   - Run the game launcher with:
   ```
   python shape_popper_launcher.py
   ```
   - The game will automatically create the necessary game file on first launch

## Game Setup

1. **Hardware Requirements**
   - Webcam: The game requires a working webcam
   - Sufficient lighting: Make sure your play area is well lit for better hand detection
   - Recommended: Stand/sit about 2-3 feet away from your webcam

2. **Camera Configuration**
   - The game will attempt to use your default webcam
   - If you have multiple cameras, it will use camera index 0 (typically the built-in webcam)
   - For best results, position the camera so it can clearly see your hand movements

## Troubleshooting

1. **Camera Not Working**
   - Ensure your webcam is properly connected and functioning
   - Check if other applications can access your camera
   - Try closing any other applications that might be using the camera

2. **Hand Detection Issues**
   - Improve lighting in your play area
   - Move to a location with a plain background
   - Ensure your hands are clearly visible to the camera
   - Try moving closer to or further from the camera

3. **Game Crashes on Startup**
   - Verify all required libraries are installed correctly
   - Check console output for specific error messages
   - Update your graphics drivers if you experience display issues

4. **Performance Issues**
   - Close other resource-intensive applications
   - Reduce the resolution of your webcam if the game runs slowly
   - Try running the game in a window rather than fullscreen (press ESC during gameplay)

## How to Play

1. **Game Objective**
   - Pop shapes as they fall from the top of the screen
   - The game lasts for 60 seconds
   - Player Blue controls the left side, Player Green controls the right side

2. **Scoring System**
   - Regular circles: 1 point
   - Squares and gold squares: 4 points
   - Black circles: -2 points (avoid these!)

3. **Controls**
   - Use your index finger to pop shapes
   - Your finger position is tracked by the webcam
   - The side of the screen you're on determines your player color
   - Press ESC or Q to exit the game early

## Customization

If you want to modify game parameters:
- Edit `shape_popper_game.py` to change:
  - Game duration (modify `countdown_seconds`)
  - Fruit size (modify `SPECIAL_FRUIT_SIZE`)
  - Fruit speed (modify `SPECIAL_FRUIT_SPEED`)
  - Point values for different shapes

Enjoy playing Shape Popper!
