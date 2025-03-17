import mediapipe as mp
import random
import time
import cv2
import numpy as np
import sys
import tkinter as tk
from tkinter import font as tkfont
import subprocess
import os

# Save the game code to a file
def save_game_code():
    game_code = """import mediapipe as mp
import random
import time
import cv2
import numpy as np
import sys

# Try to initialize the camera with error handling
def initialize_camera(width=800, height=450):
    print("Initializing camera...")
    try:
        # Try to open the default camera (0)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            # If that fails, try with CAP_DSHOW on Windows
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Set resolution if camera was opened successfully
        if cap.isOpened():
            cap.set(3, width)
            cap.set(4, height)
            print("Camera initialized successfully")
            return cap
        else:
            print("ERROR: Could not open camera")
            return None
    except Exception as e:
        print(f"ERROR initializing camera: {e}")
        return None

# Initialize MediaPipe Hands with error handling
def initialize_mediapipe():
    print("Initializing MediaPipe...")
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        mp_drawing = mp.solutions.drawing_utils
        print("MediaPipe initialized successfully")
        return hands, mp_drawing
    except Exception as e:
        print(f"ERROR initializing MediaPipe: {e}")
        return None, None

# Main game function
def main():
    global score_blue, score_green
    # Initialize camera with default resolution
    default_width = 800
    default_height = 450
    cap = initialize_camera(default_width, default_height)
    if cap is None:
        print("Exiting due to camera initialization failure")
        return
    
    # Get actual camera dimensions
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Actual camera dimensions: {actual_width}x{actual_height}")
    
    # Use the actual camera dimensions for all calculations
    display_width = actual_width
    display_height = actual_height
    
    # Initialize MediaPipe
    hands, mp_drawing = initialize_mediapipe()
    if hands is None:
        print("Exiting due to MediaPipe initialization failure")
        cap.release()
        return
    
    # Initialize timer variables
    start_time = time.time()
    countdown_seconds = 60  # 1 minute
    
    # Function to flip the frame horizontally
    def flip_frame(frame):
        return cv2.flip(frame, 1)
    
    # List of fruits and their positions
    fruits = []
    fruit_size = 50  # INCREASED from 25 to 50
    fruit_speed = 5
    last_fruit_spawn_time = time.time()
    
    # Special fruit constants
    SPECIAL_FRUIT_INTERVAL_CIRCLES = 8
    SPECIAL_FRUIT_INTERVAL_SQUARE = 4
    SPECIAL_FRUIT_INTERVAL_RED_CIRCLE = 5
    SPECIAL_FRUIT_INTERVAL_BLACK_CIRCLE = 6
    SPECIAL_FRUIT_INTERVAL_GOLD_SQUARE = 10
    SPECIAL_FRUIT_SIZE = 40  # INCREASED from 20 to 40
    SPECIAL_FRUIT_SPEED = 5
    MAX_CIRCLE_COUNT = 10000
    
    # Initialize scores for Player Blue and Player Green
    score_blue = 0
    score_green = 0
    blue_circles = 0
    black_circle_count = 0
    
    # Function to create a random fruit at the top of the screen
    def create_fruit(circle_count, width, height):
        nonlocal black_circle_count, blue_circles
        x = random.randint(SPECIAL_FRUIT_SIZE, width - SPECIAL_FRUIT_SIZE)
        y = -SPECIAL_FRUIT_SIZE  # Start fruits at the top of the screen
    
        if circle_count % SPECIAL_FRUIT_INTERVAL_CIRCLES == 0:
            if circle_count % SPECIAL_FRUIT_INTERVAL_SQUARE == 0:
                return x, y, 'square'
            else:
                return x, y, 'circle'
    
        if circle_count % SPECIAL_FRUIT_INTERVAL_RED_CIRCLE == 0:
            return x, y, 'red_circle'
    
        if circle_count % SPECIAL_FRUIT_INTERVAL_BLACK_CIRCLE == 0:
            black_circle_count += 1
            return x, y, 'black_circle'
    
        if circle_count % 5 == 0:
            blue_circles += 1
            return x, y, 'blue_circle'
    
        if circle_count % SPECIAL_FRUIT_INTERVAL_GOLD_SQUARE == 0:
            return x, y, 'gold_square'
    
        return x, y, 'circle'
    
    # Function to determine the player's color based on finger tip position
    def get_player_color(x, width):
        if x < width // 2:
            return (255, 0, 0)  # Player Blue
        else:
            return (0, 255, 0)  # Player Green
    
    # Create the window with resizable properties and set to fullscreen
    try:
        print("Creating window...")
        cv2.namedWindow('Shape Popper Game', cv2.WINDOW_NORMAL)
        # Set fullscreen
        cv2.setWindowProperty('Shape Popper Game', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        print("Window created successfully in fullscreen mode")
    except Exception as e:
        print(f"ERROR creating window: {e}")
        cap.release()
        return
    
    # Timer properties
    timer_font = cv2.FONT_HERSHEY_SIMPLEX
    timer_font_scale = 1.2  # INCREASED from 0.8 to 1.2
    timer_font_thickness = 3  # INCREASED from 2 to 3
    timer_text_color = (255, 255, 255)
    timer_border_color = (0, 0, 128)
    
    # Initialize pointer parameters
    pointer_color = (218, 247, 166)  # Cyan color for the pointer
    trail_length = 10  # Number of points in the trail
    trail_points = []
    
    print("Starting game loop...")
    # Game loop
    try:
        # Create initial fruits
        circle_count = 0
        for _ in range(5):
            fruits.append(create_fruit(circle_count, display_width, display_height))
            circle_count += 1
            
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to capture frame from camera")
                break
    
            # Flips the frame for the camera view
            frame = flip_frame(frame)
            
            # Get current frame dimensions (these will be our display dimensions)
            frame_height, frame_width = frame.shape[:2]
            
            # Calculate the remaining time on the countdown timer
            elapsed_time = time.time() - start_time
            remaining_time = max(countdown_seconds - int(elapsed_time), 0)
            
            # Check if the timer has reached 0
            if remaining_time <= 0:
                print("Game time elapsed, exiting")
                # Write the scores to a file for the launcher to read
                with open("game_scores.txt", "w") as f:
                    f.write(f"{score_blue},{score_green}")
                break  # End the game when timer reaches 0
    
            # Create a text box for the timer
            timer_text = f"Time: {remaining_time} seconds"
            timer_text_size, _ = cv2.getTextSize(timer_text, timer_font, timer_font_scale, timer_font_thickness)
            timer_box_width = timer_text_size[0] + 20
            timer_box_height = timer_text_size[1] + 10
            cv2.rectangle(frame, (frame_width - timer_box_width - 10, 10),
                          (frame_width - 10, 10 + timer_box_height), timer_border_color, -1)
            cv2.putText(frame, timer_text, (frame_width - timer_box_width + 10, 10 + timer_box_height - 10),
                        timer_font, timer_font_scale, timer_text_color, timer_font_thickness)
    
            # Add a vertical stationary line exactly down the middle of the screen
            middle_x = frame_width // 2
            cv2.line(frame, (middle_x, 0), (middle_x, frame_height), (139, 69, 19), 10)  # INCREASED thickness from 5 to 10
    
            # Process the frame to detect hand landmarks
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)
            except Exception as e:
                print(f"ERROR processing frame: {e}")
                continue
    
            if results.multi_hand_landmarks:
                for landmarks in results.multi_hand_landmarks:
                    try:
                        # Get the tip of the index finger (landmark 8)
                        index_finger_tip = landmarks.landmark[8]
                        x = int(index_finger_tip.x * frame_width)
                        y = int(index_finger_tip.y * frame_height)
    
                        # Add the finger tip position to the trail
                        trail_points.append((x, y))
    
                        # Keep the trail length limited
                        if len(trail_points) > trail_length:
                            trail_points.pop(0)
    
                        # Draw the trail - INCREASED radius
                        for i, point in enumerate(trail_points):
                            alpha = (i + 1) / float(len(trail_points))  # Vary alpha for fading effect
                            radius = int(16 * alpha)  # INCREASED from 8 to 16
                            cv2.circle(frame, point, radius, pointer_color, -1)
    
                        # Determine the player's color based on frame width
                        player_color = get_player_color(x, frame_width)
    
                        # Check for fruit slicing
                        scaled_fruit_size = int(SPECIAL_FRUIT_SIZE * frame_width / display_width)
                        for i, (fruit_x, fruit_y, fruit_type) in enumerate(fruits):
                            # Scale fruit position to current frame dimensions
                            scaled_x = int(fruit_x * frame_width / display_width)
                            scaled_y = int(fruit_y * frame_height / display_height)
                            
                            if abs(x - scaled_x) < scaled_fruit_size and abs(y - scaled_y) < scaled_fruit_size:
                                # Remove sliced fruit, update the player's score, and create a new one
                                fruits[i] = create_fruit(circle_count, display_width, display_height)
                                circle_count += 1
    
                                if player_color == (255, 0, 0):  # Player Blue
                                    if fruit_type == 'circle' or fruit_type == 'blue_circle':
                                        score_blue += 1
                                    elif fruit_type == 'square' or fruit_type == 'gold_square':
                                        score_blue += 4  # Special square gives 4 points
                                    elif fruit_type == 'black_circle':
                                        score_blue -= 2  # Black circle subtracts 2 points
                                else:  # Player Green
                                    if fruit_type == 'circle' or fruit_type == 'blue_circle':
                                        score_green += 1
                                    elif fruit_type == 'square' or fruit_type == 'gold_square':
                                        score_green += 4  # Special square gives 4 points
                                    elif fruit_type == 'black_circle':
                                        score_green -= 2  # Black circle subtracts 2 points
                    except Exception as e:
                        print(f"ERROR processing hand landmarks: {e}")
                        continue
    
            # Spawn new fruits at intervals
            current_time = time.time()
            if current_time - last_fruit_spawn_time >= 1:
                fruits.append(create_fruit(circle_count, display_width, display_height))
                last_fruit_spawn_time = current_time
    
            # Update fruit positions
            circle_count += 1
            if circle_count >= MAX_CIRCLE_COUNT:
                circle_count = 0  # Reset circle_count to avoid overflow
            
            new_fruits = []
            fruit_speed_adjusted = SPECIAL_FRUIT_SPEED * frame_height / display_height
            for fruit_x, fruit_y, fruit_type in fruits:
                fruit_y += fruit_speed_adjusted  # Make fruits move downwards
                if fruit_y <= display_height + SPECIAL_FRUIT_SIZE:
                    # Keep fruits that are still on screen
                    new_fruits.append((fruit_x, fruit_y, fruit_type))
                    
                    # Scale fruit position to current frame dimensions
                    scaled_x = int(fruit_x * frame_width / display_width)
                    scaled_y = int(fruit_y * frame_height / display_height)
                    scaled_size = int(SPECIAL_FRUIT_SIZE * frame_width / display_width)
                    
                    # Draw fruits
                    if fruit_type == 'circle' or fruit_type == 'blue_circle':
                        cv2.circle(frame, (scaled_x, scaled_y), scaled_size, (0, 0, 255), -1)
                    elif fruit_type == 'red_circle':
                        cv2.circle(frame, (scaled_x, scaled_y), scaled_size, (0, 0, 255), -1)
                    elif fruit_type == 'square' or fruit_type == 'gold_square':
                        cv2.rectangle(frame, (scaled_x - scaled_size, scaled_y - scaled_size),
                                    (scaled_x + scaled_size, scaled_y + scaled_size), (0, 223, 255), -1)
                    elif fruit_type == 'black_circle':
                        cv2.circle(frame, (scaled_x, scaled_y), scaled_size, (0, 0, 0), -1)
            
            # Add new fruits to replace those that went off screen
            while len(new_fruits) < len(fruits):
                new_fruits.append(create_fruit(circle_count, display_width, display_height))
                circle_count += 1
                
            fruits = new_fruits
    
            # Display the scores for Player Blue and Player Green - INCREASED font size
            blue_text = f'Blue: {score_blue}'
            # INCREASED font scale and thickness for player names
            cv2.putText(frame, blue_text, (20, 60), timer_font, 1.6, (255, 0, 0), 3)
            
            green_text = f'Green: {score_green}'
            green_x = middle_x + 20
            # INCREASED font scale and thickness for player names
            cv2.putText(frame, green_text, (green_x, 60), timer_font, 1.6, (0, 255, 0), 3)
    
            # Display the frame
            cv2.imshow('Shape Popper Game', frame)
    
            # Check for keyboard input to exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # Exit on ESC or 'q'
                print("User requested exit")
                # Write the scores to a file for the launcher to read
                with open("game_scores.txt", "w") as f:
                    f.write(f"{score_blue},{score_green}")
                break
    
    except Exception as e:
        print(f"ERROR in game loop: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Write the scores to a file for the launcher to read, even if there's an error
        with open("game_scores.txt", "w") as f:
            f.write(f"{score_blue},{score_green}")
    
    # Clean up
    print("Cleaning up resources...")
    cap.release()
    cv2.destroyAllWindows()
    print("Game ended")

if __name__ == "__main__":
    print("Starting Shape Popper Game...")
    # Initialize global score variables
    score_blue = 0
    score_green = 0
    main()
    print("Program exited")
"""
    with open("shape_popper_game.py", "w") as f:
        f.write(game_code)

# Game launcher using tkinter
class ShapePopperLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Shape Popper Launcher")
        
        # Set launcher to fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#F5F5DC")  # Beige background
        
        # Save the game code first
        save_game_code()
        
        # Display the start screen
        self.show_start_screen()
        
    def show_start_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create the title label
        title_font = tkfont.Font(family="Arial", size=32, weight="bold")  # INCREASED from 20 to 32
        title_label = tk.Label(
            self.root, 
            text="Welcome to Shape Poppers, click start to play!",
            font=title_font,
            fg="#800080",  # Purple
            bg="#F5F5DC"   # Beige
        )
        title_label.pack(pady=100)  # INCREASED from 50 to 100
        
        # Create a frame for the button to add beveled effect
        button_frame = tk.Frame(
            self.root,
            bg="#32CD32",  # Green
            bd=8,  # INCREASED from 5 to 8
            relief=tk.RAISED
        )
        button_frame.pack(pady=50)  # INCREASED from 30 to 50
        
        # Create start button
        start_button = tk.Button(
            button_frame,
            text="Start",
            font=("Arial", 24, "bold"),  # INCREASED from 16 to 24
            fg="#FFD700",  # Gold
            bg="#32CD32",  # Green
            width=20,  # INCREASED from 15 to 20
            command=self.start_game
        )
        start_button.pack(padx=15, pady=15)  # INCREASED from 10 to 15
        
        # Add an exit button
        exit_button = tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="red",
            width=10,
            command=self.root.destroy
        )
        exit_button.pack(pady=30)
        
    def start_game(self):
        # Hide the root window while the game runs
        self.root.withdraw()
        
        # Run the game script using sys.executable to ensure correct Python interpreter is used
        subprocess.run([sys.executable, "shape_popper_game.py"])
        
        # Read scores from the file
        try:
            with open("game_scores.txt", "r") as f:
                scores = f.read().strip().split(",")
                self.score_blue = int(scores[0])
                self.score_green = int(scores[1])
            
            # Delete the scores file
            os.remove("game_scores.txt")
        except FileNotFoundError:
            # If file doesn't exist, set default scores
            self.score_blue = 0
            self.score_green = 0
        except Exception as e:
            print(f"Error reading scores: {e}")
            self.score_blue = 0
            self.score_green = 0
        
        # Show the end screen
        self.show_end_screen()
        
    def show_end_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show the root window again
        self.root.deiconify()
        
        # Determine the winner
        if self.score_blue > self.score_green:
            winner = "Blue"
        elif self.score_green > self.score_blue:
            winner = "Green"
        else:
            winner = "No one! It's a tie"
        
        # Create the winner label
        winner_font = tkfont.Font(family="Arial", size=36, weight="bold")  # INCREASED from 22 to 36
        winner_label = tk.Label(
            self.root, 
            text=f"Player {winner} has won!",
            font=winner_font,
            fg="#FFD700",  # Gold
            bg="#F5F5DC"   # Beige
        )
        winner_label.pack(pady=80)  # INCREASED from 50 to 80
        
        # Display scores
        scores_font = tkfont.Font(family="Arial", size=24)  # INCREASED from 16 to 24
        scores_label = tk.Label(
            self.root, 
            text=f"Blue: {self.score_blue}  |  Green: {self.score_green}",
            font=scores_font,
            fg="#000000",  # Black
            bg="#F5F5DC"   # Beige
        )
        scores_label.pack(pady=30)  # INCREASED from 20 to 30
        
        # Create a frame for the play again button
        button_frame = tk.Frame(
            self.root,
            bg="#000000",  # Black
            bd=8,  # INCREASED from 5 to 8
            relief=tk.RAISED
        )
        button_frame.pack(pady=40)  # INCREASED from 30 to 40
        
        # Create return button
        return_button = tk.Button(
            button_frame,
            text="Play Again",
            font=("Arial", 20, "bold"),  # INCREASED from 14 to 20
            fg="#32CD32",  # Green text
            bg="#000000",  # Black background
            width=25,
            command=self.show_start_screen
        )
        return_button.pack(padx=15, pady=15)  # INCREASED from 10 to 15
        
        # Add an exit button
        exit_button = tk.Button(
            self.root,
            text="Exit Game",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="red",
            width=15,
            command=self.root.destroy
        )
        exit_button.pack(pady=20)

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    app = ShapePopperLauncher(root)
    
    # Start the application
    root.mainloop()