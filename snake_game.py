#!/usr/bin/env python3
"""
Terminal Snake Game - Updated Version
A classic Snake game implementation for the terminal using Python's curses library.
Features: Super food that gives +5 length and +50 points
"""

import curses
import random
import time
from collections import deque

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_screen()
        self.setup_game()
        
    def setup_screen(self):
        """Initialize the game screen and colors"""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Make getch() non-blocking
        self.normal_speed = 100  # Normal speed (100ms)
        self.boost_speed = 50   # Boost speed (50ms = 2x faster)
        self.stdscr.timeout(self.normal_speed)  # Set initial refresh rate
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Score & Super food
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Border
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Super food alternative
        
        # Get screen dimensions
        self.height, self.width = self.stdscr.getmaxyx()
        
    def setup_game(self):
        """Initialize game state"""
        # Game boundaries (leave space for border and score)
        self.game_height = self.height - 4
        self.game_width = self.width - 2
        
        # Snake starting position (center of screen)
        start_y = self.game_height // 2
        start_x = self.game_width // 2
        
        # Snake represented as deque of (y, x) coordinates
        self.snake = deque([(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)])
        
        # Initial direction (moving right)
        self.direction = (0, 1)
        
        # Score
        self.score = 0
        
        # Super food system
        self.super_food = None
        self.super_food_timer = 0
        
        # Generate first food
        self.generate_food()
        
    def generate_food(self):
        """Generate food at random location not occupied by snake"""
        while True:
            food_y = random.randint(1, self.game_height - 1)
            food_x = random.randint(1, self.game_width - 1)
            if (food_y, food_x) not in self.snake:
                # Make sure super food doesn't overlap
                if not self.super_food or (food_y, food_x) != self.super_food:
                    self.food = (food_y, food_x)
                    break
                    
    def generate_super_food(self):
        """Generate super food occasionally"""
        if random.randint(1, 8) == 1:  # 12.5% chance (1 in 8)
            attempts = 0
            while attempts < 10:  # Prevent infinite loop
                food_y = random.randint(1, self.game_height - 1)
                food_x = random.randint(1, self.game_width - 1)
                if ((food_y, food_x) not in self.snake and 
                    (food_y, food_x) != self.food):
                    self.super_food = (food_y, food_x)
                    self.super_food_timer = 150  # Disappears after 150 moves
                    break
                attempts += 1
                
    def draw_border(self):
        """Draw game border"""
        try:
            # Top and bottom borders
            for x in range(self.width - 1):
                self.stdscr.addch(0, x, '-', curses.color_pair(4))
                if self.game_height + 1 < self.height - 1:
                    self.stdscr.addch(self.game_height + 1, x, '-', curses.color_pair(4))
            
            # Left and right borders
            for y in range(self.height - 1):
                self.stdscr.addch(y, 0, '|', curses.color_pair(4))
                if self.width > 1:
                    self.stdscr.addch(y, self.width - 2, '|', curses.color_pair(4))
        except curses.error:
            pass  # Ignore cursor position errors at screen edges
                
    def draw_score(self):
        """Draw score and instructions"""
        score_text = f"Score: {self.score}"
        instructions = "WASD/Arrows to move, Hold same key for speed boost, Q to quit"
        
        # Draw score at bottom
        if self.height > 2:
            self.stdscr.addstr(self.height - 2, 2, score_text, curses.color_pair(3))
            
        # Draw instructions (truncate if too long for screen)
        if self.height > 1:
            max_instruction_length = self.width - 4
            if len(instructions) > max_instruction_length:
                instructions = instructions[:max_instruction_length-3] + "..."
            self.stdscr.addstr(self.height - 1, 2, instructions)
            
    def draw_snake(self):
        """Draw the snake"""
        for i, (y, x) in enumerate(self.snake):
            if 0 < y < self.game_height and 0 < x < self.game_width:
                try:
                    if i == 0:  # Snake head
                        self.stdscr.addch(y, x, 'O', curses.color_pair(1) | curses.A_BOLD)
                    else:  # Snake body
                        self.stdscr.addch(y, x, 'o', curses.color_pair(1))
                except curses.error:
                    pass
                    
    def draw_food(self):
        """Draw the regular food"""
        y, x = self.food
        if 0 < y < self.game_height and 0 < x < self.game_width:
            try:
                # Changed from '*' to '@' for better visibility
                self.stdscr.addch(y, x, 'ø', curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass
                
    def draw_super_food(self):
        """Draw the super food"""
        if self.super_food:
            y, x = self.super_food
            if 0 < y < self.game_height and 0 < x < self.game_width:
                try:
                    # Super food is a yellow '%' symbol
                    self.stdscr.addch(y, x, 'π', curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
            
    def handle_input(self):
        """Handle keyboard input and manage speed boost"""
        key = self.stdscr.getch()
        
        # Map keys to directions (y, x)
        key_directions = {
            ord('w'): (-1, 0),  # Up
            ord('W'): (-1, 0),
            curses.KEY_UP: (-1, 0),
            ord('s'): (1, 0),   # Down
            ord('S'): (1, 0),
            curses.KEY_DOWN: (1, 0),
            ord('a'): (0, -1),  # Left
            ord('A'): (0, -1),
            curses.KEY_LEFT: (0, -1),
            ord('d'): (0, 1),   # Right
            ord('D'): (0, 1),
            curses.KEY_RIGHT: (0, 1),
        }
        
        # Check if a direction key was pressed
        if key in key_directions:
            new_direction = key_directions[key]
            
            # Check if pressing same direction as current movement (speed boost)
            if new_direction == self.direction:
                # Activate speed boost
                self.stdscr.timeout(self.boost_speed)
            else:
                # Reset to normal speed
                self.stdscr.timeout(self.normal_speed)
                # Prevent snake from going backwards into itself
                if new_direction != (-self.direction[0], -self.direction[1]):
                    self.direction = new_direction
        else:
            # No direction key pressed, reset to normal speed
            self.stdscr.timeout(self.normal_speed)
                
        return key != ord('q') and key != ord('Q')
        
    def move_snake(self):
        """Move snake and check for collisions"""
        head_y, head_x = self.snake[0]
        new_head = (head_y + self.direction[0], head_x + self.direction[1])
        
        # Check wall collision
        if (new_head[0] <= 0 or new_head[0] >= self.game_height or
            new_head[1] <= 0 or new_head[1] >= self.game_width):
            return False
            
        # Check self collision
        if new_head in self.snake:
            return False
            
        # Add new head
        self.snake.appendleft(new_head)
        
        # Check if super food eaten
        if self.super_food and new_head == self.super_food:
            self.score += 50  # 50 points for super food
            # Grow snake by 5 segments (don't remove tail for next 4 moves)
            for _ in range(4):  # Already added 1 head, add 4 more body segments
                self.snake.append(self.snake[-1])
            self.super_food = None
            self.super_food_timer = 0
            self.generate_super_food()  # Chance for new super food
            return True
            
        # Check if regular food eaten
        if new_head == self.food:
            self.score += 10  # 10 points for regular food
            self.generate_food()
            self.generate_super_food()  # Chance for super food when eating regular food
        else:
            # Remove tail (snake doesn't grow)
            self.snake.pop()
            
        # Handle super food timer
        if self.super_food:
            self.super_food_timer -= 1
            if self.super_food_timer <= 0:
                self.super_food = None
            
        return True
        
    def game_over_screen(self):
        """Display game over screen"""
        self.stdscr.clear()
        
        # Center the game over message
        game_over_msg = "GAME OVER!"
        final_score_msg = f"Final Score: {self.score}"
        snake_length_msg = f"Snake Length: {len(self.snake)}"
        restart_msg = "Press R to restart or Q to quit"
        
        center_y = self.height // 2
        center_x = self.width // 2
        
        self.stdscr.addstr(center_y - 2, center_x - len(game_over_msg) // 2, 
                          game_over_msg, curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(center_y - 1, center_x - len(final_score_msg) // 2, 
                          final_score_msg, curses.color_pair(3))
        self.stdscr.addstr(center_y, center_x - len(snake_length_msg) // 2, 
                          snake_length_msg, curses.color_pair(3))
        self.stdscr.addstr(center_y + 2, center_x - len(restart_msg) // 2, 
                          restart_msg)
        
        self.stdscr.refresh()
        
        # Wait for user input
        while True:
            key = self.stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                return False
            elif key == ord('r') or key == ord('R'):
                return True
                
    def run(self):
        """Main game loop"""
        while True:
            # Clear screen
            self.stdscr.clear()
            
            # Draw game elements
            self.draw_border()
            self.draw_snake()
            self.draw_food()
            self.draw_super_food()  # Draw super food if it exists
            self.draw_score()
            
            # Refresh screen
            self.stdscr.refresh()
            
            # Handle input
            if not self.handle_input():
                break
                
            # Move snake
            if not self.move_snake():
                if self.game_over_screen():
                    # Restart game
                    self.setup_game()
                    continue
                else:
                    break

def main(stdscr):
    """Main function to initialize and run the game"""
    try:
        game = SnakeGame(stdscr)
        game.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Check terminal size
    try:
        # Initialize curses to get terminal size
        stdscr = curses.initscr()
        height, width = stdscr.getmaxyx()
        curses.endwin()
        
        if height < 10 or width < 30:
            print("Terminal too small! Please resize to at least 30x10 characters.")
            exit(1)
            
        # Run the game
        curses.wrapper(main)
        
    except Exception as e:
        print(f"Error running the game: {e}")
        print("Make sure your terminal supports curses and is properly configured.")
