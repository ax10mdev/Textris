#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# TEXTRIS - A Tetris clone for the terminal
# Copyright (c) 2025 ax10mdev (https://github.com/ax10mdev)
# 
# This is an unofficial terminal-based implementation of Tetris
# for educational and entertainment purposes only.

import curses
import random
import time
import json
import os
import sys
from math import sin, cos, pi
from curses import wrapper

# Tetromino shapes (I, J, L, O, S, T, Z)
TETROMINOS = [
    [[1, 1, 1, 1]],  # I

    [[2, 0, 0],      # J
     [2, 2, 2]],

    [[0, 0, 3],      # L
     [3, 3, 3]],

    [[4, 4],         # O
     [4, 4]],

    [[0, 5, 5],      # S
     [5, 5, 0]],

    [[0, 6, 0],      # T
     [6, 6, 6]],

    [[7, 7, 0],      # Z
     [0, 7, 7]]
]

# Colors for each tetromino
COLORS = {
    1: curses.COLOR_CYAN,     # I - Cyan
    2: curses.COLOR_BLUE,     # J - Blue
    3: curses.COLOR_WHITE,    # L - White
    4: curses.COLOR_YELLOW,   # O - Yellow
    5: curses.COLOR_GREEN,    # S - Green
    6: curses.COLOR_MAGENTA,  # T - Magenta
    7: curses.COLOR_RED       # Z - Red
}

# Display characters
BLOCK = "█"
GHOST = "▒"
EMPTY = " "

# Game dimensions
WIDTH = 10
HEIGHT = 20

# Game logo
LOGO = [
    "████████╗███████╗██╗  ██╗████████╗██████╗ ██╗███████╗",
    "╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██║██╔════╝",
    "   ██║   █████╗   ╚███╔╝    ██║   ██████╔╝██║███████╗",
    "   ██║   ██╔══╝   ██╔██╗    ██║   ██╔══██╗██║╚════██║",
    "   ██║   ███████╗██╔╝ ██╗   ██║   ██║  ██║██║███████║",
    "   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝"
]

# Config and save file path
CONFIG_DIR = os.path.expanduser("~/.textris")
HIGH_SCORE_FILE = os.path.join(CONFIG_DIR, "high_scores.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class Animation:
    """Class to handle various animations in the game"""
    
    @staticmethod
    def flash(stdscr, y, x, height, width, frames=5, delay=0.05):
        """Create a flashing effect in the specified area"""
        for i in range(frames):
            color = 1 + (i % 7)
            for yy in range(height):
                for xx in range(width):
                    try:
                        stdscr.addstr(y + yy, x + xx, " ", curses.color_pair(color) | curses.A_REVERSE)
                    except curses.error:
                        pass
            stdscr.refresh()
            time.sleep(delay)
    
    @staticmethod
    def line_clear(stdscr, y, x, width, delay=0.01):
        """Create a line clear animation"""
        for i in range(width // 2):
            middle = width // 2
            left = middle - i - 1
            right = middle + i
            
            if left >= 0:
                try:
                    stdscr.addstr(y, x + left, "  ", curses.color_pair(8) | curses.A_REVERSE)
                except curses.error:
                    pass
            if right < width:
                try:
                    stdscr.addstr(y, x + right, "  ", curses.color_pair(8) | curses.A_REVERSE)
                except curses.error:
                    pass
            
            stdscr.refresh()
            time.sleep(delay)
    
    @staticmethod
    def game_over(stdscr, y, x, text, delay=0.1):
        """Create a game over animation"""
        for i in range(len(text) + 1):
            try:
                stdscr.addstr(y, x, text[:i], curses.color_pair(10) | curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            time.sleep(delay)
    
    @staticmethod
    def level_up(stdscr, y, x, level, delay=0.05):
        """Create a level up animation"""
        text = f"LEVEL UP! {level}"
        
        # First make it appear letter by letter
        for i in range(len(text) + 1):
            try:
                stdscr.addstr(y, x, text[:i], curses.color_pair(random.randint(1, 7)) | curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            time.sleep(delay)
            
        # Then flash colors
        for i in range(10):
            try:
                stdscr.addstr(y, x, text, curses.color_pair(random.randint(1, 7)) | curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            time.sleep(delay)

    @staticmethod
    def typing_effect(stdscr, y, x, text, delay=0.03, color_pair=0, attr=0):
        """Create a typing effect for text"""
        for i in range(len(text) + 1):
            try:
                stdscr.addstr(y, x, text[:i], color_pair | attr)
            except curses.error:
                pass
            stdscr.refresh()
            time.sleep(delay)

class Textris:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.next_piece = None
        self.hold_piece = None
        self.hold_used = False
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.combo = 0
        self.max_y, self.max_x = stdscr.getmaxyx()
        self.ghost_enabled = True
        self.start_time = time.time()
        self.game_mode = "normal"  # normal, marathon, sprint
        self.stats = {
            "pieces": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
            "lines": 0,
            "tetris": 0,
            "max_combo": 0,
            "total_pieces": 0
        }
        self.controls = self.load_controls()
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        
        # Regular tetromino colors
        for i in range(1, 8):
            curses.init_pair(i, COLORS[i], -1)
            # Ghost piece colors (8-14)
            curses.init_pair(i+7, COLORS[i], curses.COLOR_BLACK)
        
        # UI colors
        curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Border
        curses.init_pair(16, curses.COLOR_YELLOW, -1)                # Score
        curses.init_pair(17, curses.COLOR_RED, -1)                   # Game Over
        curses.init_pair(18, curses.COLOR_GREEN, -1)                 # Success
        curses.init_pair(19, curses.COLOR_CYAN, -1)                  # Info
        curses.init_pair(20, curses.COLOR_MAGENTA, -1)               # Title
        
        # Hide cursor
        curses.curs_set(0)
        # No delay on input
        self.stdscr.nodelay(True)
        
    def load_high_score(self):
        """Load high score from file"""
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
            
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except Exception:
            pass
            
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
                
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except Exception:
            pass
    
    def load_controls(self):
        """Load control settings"""
        default_controls = {
            "move_left": curses.KEY_LEFT,
            "move_right": curses.KEY_RIGHT,
            "rotate_cw": curses.KEY_UP,
            "rotate_ccw": ord('z'),
            "soft_drop": curses.KEY_DOWN,
            "hard_drop": ord(' '),
            "hold": ord('c'),
            "pause": ord('p'),
            "quit": ord('q'),
            "toggle_ghost": ord('g')
        }
        
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
                
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
            
        return default_controls
    
    def save_controls(self):
        """Save control settings"""
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
                
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.controls, f)
        except Exception:
            pass
    
    def show_main_menu(self):
        """Display the main menu"""
        menu_items = [
            "Start Game",
            "How to Play",
            "Settings",
            "High Scores",
            "Exit"
        ]
        
        selected = 0
        
        while True:
            self.stdscr.clear()
            
            # Display logo
            start_y = 2
            start_x = (self.max_x - len(LOGO[0])) // 2
            
            for i, line in enumerate(LOGO):
                try:
                    self.stdscr.addstr(start_y + i, start_x, line, curses.color_pair(random.randint(1, 7)))
                except curses.error:
                    pass
            
            # Display copyright
            copyright_text = "© 2025 ax10mdev (https://github.com/ax10mdev)"
            try:
                self.stdscr.addstr(start_y + len(LOGO) + 1, (self.max_x - len(copyright_text)) // 2, 
                               copyright_text, curses.color_pair(16))
            except curses.error:
                pass
            
            # Display menu items
            menu_y = start_y + len(LOGO) + 3
            menu_x = (self.max_x - 20) // 2
            
            try:
                self.stdscr.addstr(menu_y - 1, menu_x, "MAIN MENU", curses.color_pair(20) | curses.A_BOLD)
            except curses.error:
                pass
            
            for i, item in enumerate(menu_items):
                if i == selected:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, menu_x, f"> {item} <", 
                                      curses.color_pair(16) | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, menu_x, f"  {item}  ")
                    except curses.error:
                        pass
            
            # Instructions
            instructions_y = menu_y + len(menu_items) * 2 + 2
            try:
                self.stdscr.addstr(instructions_y, (self.max_x - len("Use ↑/↓ to navigate, Enter to select")) // 2,
                               "Use ↑/↓ to navigate, Enter to select", curses.color_pair(19))
            except curses.error:
                pass
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(menu_items) - 1:
                selected += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
                if selected == 0:  # Start Game
                    return True
                elif selected == 1:  # How to Play
                    self.show_help_screen()
                elif selected == 2:  # Settings
                    self.show_settings_menu()
                elif selected == 3:  # High Scores
                    self.show_high_scores()
                elif selected == 4:  # Exit
                    return False
            elif key == ord('q') or key == ord('Q'):
                return False
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)
    
    def show_help_screen(self):
        """Display help screen"""
        self.stdscr.clear()
        
        title = "HOW TO PLAY TEXTRIS"
        start_y = 2
        
        try:
            self.stdscr.addstr(start_y, (self.max_x - len(title)) // 2, title, 
                           curses.color_pair(20) | curses.A_BOLD)
        except curses.error:
            pass
        
        # Help content
        help_text = [
            "",
            "OBJECTIVE:",
            "- Arrange falling tetrominos to create complete horizontal lines",
            "- Completed lines will be cleared and points awarded",
            "- The game ends when tetrominos stack to the top of the board",
            "",
            "CONTROLS:",
            f"- {curses.keyname(self.controls['move_left']).decode()}: Move tetromino left",
            f"- {curses.keyname(self.controls['move_right']).decode()}: Move tetromino right",
            f"- {curses.keyname(self.controls['rotate_cw']).decode()}: Rotate tetromino clockwise",
            f"- {curses.keyname(self.controls['rotate_ccw']).decode()}: Rotate tetromino counter-clockwise",
            f"- {curses.keyname(self.controls['soft_drop']).decode()}: Soft drop (accelerate downward)",
            f"- {curses.keyname(self.controls['hard_drop']).decode()}: Hard drop (instant placement)",
            f"- {curses.keyname(self.controls['hold']).decode()}: Hold current tetromino for later use",
            f"- {curses.keyname(self.controls['pause']).decode()}: Pause/Resume game",
            f"- {curses.keyname(self.controls['quit']).decode()}: Quit game",
            f"- {curses.keyname(self.controls['toggle_ghost']).decode()}: Toggle ghost piece",
            "",
            "SCORING:",
            "- 1 Line:    100 × Level",
            "- 2 Lines:   300 × Level",
            "- 3 Lines:   500 × Level",
            "- 4 Lines:   800 × Level",
            "- Combos:    50 × Combo × Level",
            "",
            "LEVEL UP:",
            "- Every 10 lines cleared",
            "- Each level increases tetromino falling speed",
            "",
            "Press any key to return to the main menu..."
        ]
        
        for i, line in enumerate(help_text):
            try:
                if "OBJECTIVE:" in line or "CONTROLS:" in line or "SCORING:" in line or "LEVEL UP:" in line:
                    self.stdscr.addstr(start_y + i + 1, 5, line, curses.color_pair(16) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(start_y + i + 1, 5, line)
            except curses.error:
                pass
        
        self.stdscr.refresh()
        
        # Wait for any key
        self.stdscr.nodelay(False)
        self.stdscr.getch()
        self.stdscr.nodelay(True)
    
    def show_settings_menu(self):
        """Display settings menu"""
        settings_items = [
            "Game Mode",
            "Configure Controls",
            "Toggle Ghost Piece",
            "Back to Main Menu"
        ]
        
        selected = 0
        
        while True:
            self.stdscr.clear()
            
            title = "SETTINGS"
            start_y = 2
            
            try:
                self.stdscr.addstr(start_y, (self.max_x - len(title)) // 2, title, 
                               curses.color_pair(20) | curses.A_BOLD)
            except curses.error:
                pass
            
            # Display settings items
            menu_y = start_y + 3
            menu_x = (self.max_x - 30) // 2
            
            for i, item in enumerate(settings_items):
                if i == 0:  # Game Mode
                    item_text = f"{item}: {self.game_mode.capitalize()}"
                elif i == 2:  # Ghost Piece
                    item_text = f"{item}: {'Enabled' if self.ghost_enabled else 'Disabled'}"
                else:
                    item_text = item
                
                if i == selected:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, menu_x, f"> {item_text} <", 
                                      curses.color_pair(16) | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    try:
                        self.stdscr.addstr(menu_y + i * 2, menu_x, f"  {item_text}  ")
                    except curses.error:
                        pass
            
            # Instructions
            instructions_y = menu_y + len(settings_items) * 2 + 2
            try:
                self.stdscr.addstr(instructions_y, (self.max_x - len("Use ↑/↓ to navigate, ←/→ to change, Enter to select")) // 2,
                               "Use ↑/↓ to navigate, ←/→ to change, Enter to select", curses.color_pair(19))
            except curses.error:
                pass
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(settings_items) - 1:
                selected += 1
            elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                if selected == 0:  # Game Mode
                    modes = ["normal", "marathon", "sprint"]
                    current_index = modes.index(self.game_mode)
                    new_index = (current_index + (1 if key == curses.KEY_RIGHT else -1)) % len(modes)
                    self.game_mode = modes[new_index]
                elif selected == 2:  # Ghost Piece
                    self.ghost_enabled = not self.ghost_enabled
            elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
                if selected == 1:  # Configure Controls
                    self.configure_controls()
                elif selected == 3:  # Back to Main Menu
                    return
            elif key == ord('q') or key == ord('Q'):
                return
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)
    
    def configure_controls(self):
        """Allow user to configure game controls"""
        control_items = [
            ("Move Left", "move_left"),
            ("Move Right", "move_right"),
            ("Rotate Clockwise", "rotate_cw"),
            ("Rotate Counter-Clockwise", "rotate_ccw"),
            ("Soft Drop", "soft_drop"),
            ("Hard Drop", "hard_drop"),
            ("Hold Piece", "hold"),
            ("Pause Game", "pause"),
            ("Quit Game", "quit"),
            ("Toggle Ghost Piece", "toggle_ghost"),
            ("Back to Settings")
        ]
        
        selected = 0
        
        while True:
            self.stdscr.clear()
            
            title = "CONFIGURE CONTROLS"
            start_y = 2
            
            try:
                self.stdscr.addstr(start_y, (self.max_x - len(title)) // 2, title, 
                               curses.color_pair(20) | curses.A_BOLD)
            except curses.error:
                pass
            
            # Display control items
            menu_y = start_y + 3
            menu_x = (self.max_x - 50) // 2
            
            for i, (display_name, control_key) in enumerate(control_items):
                # Last item is "Back to Settings"
                if i == len(control_items) - 1:
                    if i == selected:
                        try:
                            self.stdscr.addstr(menu_y + i * 2, menu_x, f"> {display_name} <", 
                                          curses.color_pair(16) | curses.A_BOLD)
                        except curses.error:
                            pass
                    else:
                        try:
                            self.stdscr.addstr(menu_y + i * 2, menu_x, f"  {display_name}  ")
                        except curses.error:
                            pass
                else:
                    key_name = curses.keyname(self.controls[control_key]).decode()
                    
                    if i == selected:
                        try:
                            self.stdscr.addstr(menu_y + i * 2, menu_x, f"> {display_name}: ", 
                                          curses.color_pair(16) | curses.A_BOLD)
                            self.stdscr.addstr(f"{key_name} <", curses.color_pair(16) | curses.A_BOLD)
                        except curses.error:
                            pass
                    else:
                        try:
                            self.stdscr.addstr(menu_y + i * 2, menu_x, f"  {display_name}: {key_name}  ")
                        except curses.error:
                            pass
            
            # Instructions
            instructions_y = menu_y + len(control_items) * 2 + 2
            try:
                self.stdscr.addstr(instructions_y, (self.max_x - len("Use ↑/↓ to navigate, Enter to change a key, Esc to cancel")) // 2,
                               "Use ↑/↓ to navigate, Enter to change a key, Esc to cancel", curses.color_pair(19))
            except curses.error:
                pass
            
            self.stdscr.refresh()
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(control_items) - 1:
                selected += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter key
                if selected == len(control_items) - 1:  # Back to Settings
                    self.save_controls()
                    return
                else:
                    # Prompt for new key
                    control_name = control_items[selected][0]
                    control_key = control_items[selected][1]
                    
                    try:
                        self.stdscr.addstr(instructions_y, (self.max_x - len(f"Press new key for {control_name}...")) // 2,
                                      f"Press new key for {control_name}...", curses.color_pair(17) | curses.A_BOLD)
                    except curses.error:
                        pass
                    self.stdscr.refresh()
                    
                    # Wait for key input
                    self.stdscr.nodelay(False)
                    new_key = self.stdscr.getch()
                    self.stdscr.nodelay(True)
                    
                    # Escape key cancels
                    if new_key != 27:  # Not Escape
                        self.controls[control_key] = new_key
            elif key == 27:  # Escape key
                return
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)
    
    def show_high_scores(self):
        """Display high scores screen"""
        self.stdscr.clear()
        
        title = "HIGH SCORES"
        start_y = 2
        
        try:
            self.stdscr.addstr(start_y, (self.max_x - len(title)) // 2, title, 
                           curses.color_pair(20) | curses.A_BOLD)
        except curses.error:
            pass
        
        # Show high score
        high_score_text = f"All-Time High Score: {self.high_score}"
        try:
            self.stdscr.addstr(start_y + 3, (self.max_x - len(high_score_text)) // 2, 
                           high_score_text, curses.color_pair(16) | curses.A_BOLD)
        except curses.error:
            pass
        
        # Return prompt
        return_text = "Press any key to return to the main menu..."
        try:
            self.stdscr.addstr(start_y + 6, (self.max_x - len(return_text)) // 2, return_text)
        except curses.error:
            pass
        
        self.stdscr.refresh()
        
        # Wait for any key
        self.stdscr.nodelay(False)
        self.stdscr.getch()
        self.stdscr.nodelay(True)
    
    def show_loading_animation(self):
        """Display a loading animation"""
        self.stdscr.clear()
        
        # Display logo
        start_y = (self.max_y - len(LOGO)) // 2 - 5
        start_x = (self.max_x - len(LOGO[0])) // 2
        
        for i, line in enumerate(LOGO):
            try:
                self.stdscr.addstr(start_y + i, start_x, line, curses.color_pair(random.randint(1, 7)))
            except curses.error:
                pass
        
        # Display copyright
        copyright_text = "© 2025 ax10mdev (https://github.com/ax10mdev)"
        try:
            self.stdscr.addstr(start_y + len(LOGO) + 1, (self.max_x - len(copyright_text)) // 2, 
                           copyright_text, curses.color_pair(16))
        except curses.error:
            pass
        
        # Loading animation
        loading_y = start_y + len(LOGO) + 3
        loading_x = (self.max_x - 30) // 2
        
        try:
            Animation.typing_effect(self.stdscr, loading_y, loading_x, "Loading...", delay=0.05, 
                                   color_pair=curses.color_pair(19), attr=curses.A_BOLD)
        except curses.error:
            pass
        
        progress_bar = ["[" + " " * 30 + "]"]
        for i in range(31):
            progress_bar[0] = "[" + "█" * i + " " * (30 - i) + "]"
            try:
                self.stdscr.addstr(loading_y + 1, loading_x - 2, progress_bar[0], 
                               curses.color_pair(i % 7 + 1) | curses.A_BOLD)
            except curses.error:
                pass
            self.stdscr.refresh()
            time.sleep(0.03)
        
        # Prepare message
        try:
            self.stdscr.addstr(loading_y + 3, loading_x - 2, "Press any key to start...", 
                           curses.color_pair(18) | curses.A_BOLD)
        except curses.error:
            pass
        self.stdscr.refresh()
        
        # Wait for key press
        self.stdscr.nodelay(False)
        self.stdscr.getch()
        self.stdscr.nodelay(True)
    
    def new_piece(self):
        """Create a new tetromino"""
        if self.next_piece is None:
            self.next_piece = random.choice(TETROMINOS)
        
        self.current_piece = self.next_piece
        self.next_piece = random.choice(TETROMINOS)
        
        # Update statistics
        color_id = self.current_piece[0][0]
        if color_id == 0:
            # Find the non-zero value in the tetromino
            for row in self.current_piece:
                for cell in row:
                    if cell != 0:
                        color_id = cell
                        break
        
        self.stats["pieces"][color_id] += 1
        self.stats["total_pieces"] += 1
        
        # Set initial position
        self.current_y = 0
        self.current_x = WIDTH // 2 - len(self.current_piece[0]) // 2
        
        # Reset hold used flag
        self.hold_used = False
        
        # Check if new piece can be placed
        if not self.is_valid_position():
            self.game_over = True
    
    def hold_current_piece(self):
        """Store the current piece for later use"""
        if self.hold_used:
            return
            
        if self.hold_piece is None:
            # First hold
            self.hold_piece = self.current_piece
            self.new_piece()
        else:
            # Swap current and hold pieces
            self.current_piece, self.hold_piece = self.hold_piece, self.current_piece
            
            # Reset position
            self.current_y = 0
            self.current_x = WIDTH // 2 - len(self.current_piece[0]) // 2
            
        self.hold_used = True
    
    def rotate_piece(self, clockwise=True):
        """Rotate the current tetromino"""
        # Make a copy of the current piece
        original_piece = self.current_piece
        original_x, original_y = self.current_x, self.current_y
        
        # Rotate the piece
        rows = len(original_piece)
        cols = len(original_piece[0])
        
        if clockwise:
            # Clockwise rotation
            rotated = [[original_piece[rows-1-j][i] for j in range(rows)] for i in range(cols)]
        else:
            # Counter-clockwise rotation
            rotated = [[original_piece[j][cols-1-i] for j in range(rows)] for i in range(cols)]
        
        self.current_piece = rotated
        
        # Wall kick - if the rotated piece is invalid, try to adjust its position
        if not self.is_valid_position():
            # Try to move left
            self.current_x -= 1
            if not self.is_valid_position():
                # Try to move right
                self.current_x += 2
                if not self.is_valid_position():
                    # Try to move up (useful for I piece rotation near the floor)
                    self.current_x -= 1
                    self.current_y -= 1
                    if not self.is_valid_position():
                        # If all failed, revert to original
                        self.current_piece = original_piece
                        self.current_x = original_x
                        self.current_y = original_y
    
    def is_valid_position(self):
        """Check if the current tetromino's position is valid"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[0])):
                if self.current_piece[y][x] != 0:  # If this is a block
                    board_y, board_x = self.current_y + y, self.current_x + x
                    
                    # Check for boundaries
                    if (board_y < 0 or board_y >= HEIGHT or 
                        board_x < 0 or board_x >= WIDTH):
                        return False
                    
                    # Check for collision with other blocks
                    if board_y >= 0 and self.board[board_y][board_x] != 0:
                        return False
        return True
    
    def get_ghost_position(self):
        """Calculate the position where the piece would land"""
        if not self.ghost_enabled:
            return None
            
        original_y = self.current_y
        
        # Move down until collision
        while True:
            self.current_y += 1
            if not self.is_valid_position():
                self.current_y -= 1
                ghost_y = self.current_y
                self.current_y = original_y
                return ghost_y
    
    def merge_piece(self):
        """Add the current tetromino to the board"""
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[0])):
                if self.current_piece[y][x] != 0:
                    self.board[self.current_y + y][self.current_x + x] = self.current_piece[y][x]
    
    def clear_lines(self):
        """Clear completed lines and calculate score"""
        lines_cleared = 0
        lines_to_clear = []
        
        # Find completed lines
        for y in range(HEIGHT - 1, -1, -1):
            if all(self.board[y]):
                lines_to_clear.append(y)
                lines_cleared += 1
        
        # Animation for clearing lines
        if lines_cleared > 0:
            board_x = (self.max_x - (WIDTH * 2 + 2)) // 2
            board_y = (self.max_y - (HEIGHT + 2)) // 2
            
            # Flash the lines
            for line_y in lines_to_clear:
                Animation.line_clear(self.stdscr, board_y + 1 + line_y, board_x + 1, WIDTH * 2)
            
            # Clear the lines
            self.stdscr.refresh()
            time.sleep(0.1)
            
            # Remove the lines
            for line_y in sorted(lines_to_clear):
                # Shift all lines above down
                for y in range(line_y, 0, -1):
                    self.board[y] = self.board[y - 1][:]
                # Add empty line at the top
                self.board[0] = [0] * WIDTH
        
        # Update statistics
        self.stats["lines"] += lines_cleared
        if lines_cleared == 4:
            self.stats["tetris"] += 1
        
        # Calculate score
        if lines_cleared > 0:
            # Base points for cleared lines
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points.get(lines_cleared, 1000) * self.level
            
            # Combo bonus
            if lines_cleared > 0:
                self.combo += 1
                if self.combo > 1:
                    self.score += 50 * self.combo * self.level
                
                if self.combo > self.stats["max_combo"]:
                    self.stats["max_combo"] = self.combo
            else:
                self.combo = 0
            
            # Update lines cleared and check for level up
            old_level = self.level
            self.lines += lines_cleared
            self.level = self.lines // 10 + 1
            
            # Level up animation
            if self.level > old_level:
                level_x = (self.max_x - 15) // 2
                level_y = (self.max_y // 2)
                Animation.level_up(self.stdscr, level_y, level_x, self.level)
            
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def move_down(self):
        """Move the tetromino down"""
        self.current_y += 1
        if not self.is_valid_position():
            self.current_y -= 1
            self.merge_piece()
            self.clear_lines()
            self.new_piece()
            return False
        return True
    
    def move_left(self):
        """Move the tetromino left"""
        self.current_x -= 1
        if not self.is_valid_position():
            self.current_x += 1
            return False
        return True
    
    def move_right(self):
        """Move the tetromino right"""
        self.current_x += 1
        if not self.is_valid_position():
            self.current_x -= 1
            return False
        return True
    
    def hard_drop(self):
        """Instantly drop the tetromino to the bottom"""
        drop_points = 0
        while True:
            self.current_y += 1
            if not self.is_valid_position():
                self.current_y -= 1
                break
            drop_points += 2
        
        # Add drop points to score
        self.score += drop_points
        
        # Merge the piece and process
        self.merge_piece()
        self.clear_lines()
        self.new_piece()
    
    def draw_border(self, y, x, height, width, title=None):
        """Draw a border with optional title"""
        # Top and bottom borders
        for i in range(width):
            try:
                self.stdscr.addstr(y, x + i, "═", curses.color_pair(15))
                self.stdscr.addstr(y + height - 1, x + i, "═", curses.color_pair(15))
            except curses.error:
                pass
        
        # Left and right borders
        for i in range(height):
            try:
                self.stdscr.addstr(y + i, x, "║", curses.color_pair(15))
                self.stdscr.addstr(y + i, x + width - 1, "║", curses.color_pair(15))
            except curses.error:
                pass
        
        # Corners
        try:
            self.stdscr.addstr(y, x, "╔", curses.color_pair(15))
            self.stdscr.addstr(y, x + width - 1, "╗", curses.color_pair(15))
            self.stdscr.addstr(y + height - 1, x, "╚", curses.color_pair(15))
            self.stdscr.addstr(y + height - 1, x + width - 1, "╝", curses.color_pair(15))
        except curses.error:
            pass
            
        # Title
        if title:
            title_x = x + (width - len(title) - 2) // 2
            try:
                self.stdscr.addstr(y, title_x, f" {title} ", curses.color_pair(15))
            except curses.error:
                pass
    
    def draw_tetromino(self, tetromino, y, x, y_offset, x_offset, ghost=False):
        """Draw a tetromino on the screen"""
        color_offset = 7 if ghost else 0
        char = GHOST if ghost else BLOCK
        
        for ty in range(len(tetromino)):
            for tx in range(len(tetromino[0])):
                if tetromino[ty][tx] != 0:
                    color = tetromino[ty][tx]
                    try:
                        self.stdscr.addstr(y + y_offset + ty, x + x_offset + tx * 2, char * 2, 
                                      curses.color_pair(color + color_offset))
                    except curses.error:
                        pass
    
    def draw_board(self):
        """Draw the game board and UI elements"""
        # Calculate positions
        board_x = (self.max_x - (WIDTH * 2 + 2)) // 2
        board_y = (self.max_y - (HEIGHT + 2)) // 2
        
        # Draw game board
        self.draw_border(board_y, board_x, HEIGHT + 2, WIDTH * 2 + 2, "TEXTRIS")
        
        # Draw board content
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y][x] != 0:
                    try:
                        self.stdscr.addstr(board_y + 1 + y, board_x + 1 + x * 2, BLOCK * 2, 
                                      curses.color_pair(self.board[y][x]))
                    except curses.error:
                        pass
        
        # Draw ghost piece
        if self.ghost_enabled:
            ghost_y = self.get_ghost_position()
            if ghost_y is not None and ghost_y > self.current_y:
                for y in range(len(self.current_piece)):
                    for x in range(len(self.current_piece[0])):
                        if self.current_piece[y][x] != 0:
                            try:
                                self.stdscr.addstr(board_y + 1 + ghost_y + y, board_x + 1 + (self.current_x + x) * 2, 
                                               GHOST * 2, curses.color_pair(self.current_piece[y][x] + 7))
                            except curses.error:
                                pass
        
        # Draw current piece
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[0])):
                if self.current_piece[y][x] != 0:
                    try:
                        self.stdscr.addstr(board_y + 1 + self.current_y + y, board_x + 1 + (self.current_x + x) * 2, 
                                       BLOCK * 2, curses.color_pair(self.current_piece[y][x]))
                    except curses.error:
                        pass
        
        # Draw next piece panel
        next_x = board_x + WIDTH * 2 + 5
        next_y = board_y
        self.draw_border(next_y, next_x, 6, 10, "NEXT")
        
        if self.next_piece:
            self.draw_tetromino(self.next_piece, next_y, next_x, 2, 1, False)
        
        # Draw hold piece panel
        hold_x = board_x - 15
        hold_y = board_y
        self.draw_border(hold_y, hold_x, 6, 10, "HOLD")
        
        if self.hold_piece:
            self.draw_tetromino(self.hold_piece, hold_y, hold_x, 2, 1, False)
        
        # Draw score and info panel
        info_x = hold_x
        info_y = hold_y + 7
        self.draw_border(info_y, info_x, 12, 15, "STATS")
        
        try:
            self.stdscr.addstr(info_y + 1, info_x + 2, f"SCORE", curses.color_pair(16))
            self.stdscr.addstr(info_y + 2, info_x + 2, f"{self.score}")
            
            self.stdscr.addstr(info_y + 4, info_x + 2, f"HIGH", curses.color_pair(16))
            self.stdscr.addstr(info_y + 5, info_x + 2, f"{self.high_score}")
            
            self.stdscr.addstr(info_y + 7, info_x + 2, f"LEVEL", curses.color_pair(16))
            self.stdscr.addstr(info_y + 8, info_x + 2, f"{self.level}")
            
            self.stdscr.addstr(info_y + 10, info_x + 2, f"LINES", curses.color_pair(16))
            self.stdscr.addstr(info_y + 11, info_x + 2, f"{self.lines}")
        except curses.error:
            pass
            
        # Draw time panel
        time_x = next_x
        time_y = next_y + 7
        self.draw_border(time_y, time_x, 4, 15, "TIME")
        
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        try:
            self.stdscr.addstr(time_y + 2, time_x + 3, f"{minutes:02d}:{seconds:02d}")
        except curses.error:
            pass
            
        # Draw controls helper
        help_x = time_x
        help_y = time_y + 5
        self.draw_border(help_y, help_x, 8, 15, "CONTROLS")
        
        try:
            self.stdscr.addstr(help_y + 1, help_x + 2, f"↑: Rotate")
            self.stdscr.addstr(help_y + 2, help_x + 2, f"←/→: Move")
            self.stdscr.addstr(help_y + 3, help_x + 2, f"↓: Soft Drop")
            self.stdscr.addstr(help_y + 4, help_x + 2, f"Space: Drop")
            self.stdscr.addstr(help_y + 5, help_x + 2, f"C: Hold")
            self.stdscr.addstr(help_y + 6, help_x + 2, f"P: Pause")
        except curses.error:
            pass
            
        # Show copyright
        try:
            copyright_text = "© 2025 ax10mdev"
            self.stdscr.addstr(self.max_y - 1, (self.max_x - len(copyright_text)) // 2, 
                           copyright_text, curses.color_pair(16))
        except curses.error:
            pass
        
        # Draw game over message if needed
        if self.game_over:
            # Fade the board
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    try:
                        self.stdscr.addstr(board_y + 1 + y, board_x + 1 + x * 2, "  ", curses.A_DIM)
                    except curses.error:
                        pass
            
            # Game over box
            game_over_width = 26
            game_over_height = 8
            game_over_x = (self.max_x - game_over_width) // 2
            game_over_y = (self.max_y - game_over_height) // 2
            
            self.draw_border(game_over_y, game_over_x, game_over_height, game_over_width)
            
            try:
                self.stdscr.addstr(game_over_y + 2, game_over_x + 5, "GAME OVER!", 
                               curses.color_pair(17) | curses.A_BOLD)
                
                self.stdscr.addstr(game_over_y + 4, game_over_x + 3, f"Final Score: {self.score}")
                
                self.stdscr.addstr(game_over_y + 6, game_over_x + 2, "R: Restart  Q: Quit")
            except curses.error:
                pass
        
        # Draw pause screen if paused
        if self.paused:
            # Fade the board
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    try:
                        self.stdscr.addstr(board_y + 1 + y, board_x + 1 + x * 2, "  ", curses.A_DIM)
                    except curses.error:
                        pass
            
            # Pause box
            pause_width = 20
            pause_height = 7
            pause_x = (self.max_x - pause_width) // 2
            pause_y = (self.max_y - pause_height) // 2
            
            self.draw_border(pause_y, pause_x, pause_height, pause_width)
            
            try:
                self.stdscr.addstr(pause_y + 2, pause_x + 6, "PAUSED", 
                               curses.color_pair(16) | curses.A_BOLD)
                
                self.stdscr.addstr(pause_y + 4, pause_x + 2, "P: Resume  Q: Quit")
            except curses.error:
                pass
    
    def run(self):
        """Main game loop"""
        # Show main menu
        if not self.show_main_menu():
            return
        
        # Show loading animation
        self.show_loading_animation()
        
        # Initialize game
        self.new_piece()
        self.start_time = time.time()
        
        last_move_time = time.time()
        last_frame_time = time.time()
        frame_rate = 1/30  # 30 FPS
        
        while True:
            current_time = time.time()
            
            # Frame rate limiting
            if current_time - last_frame_time < frame_rate:
                time.sleep(max(0, frame_rate - (current_time - last_frame_time)))
                current_time = time.time()
            
            last_frame_time = current_time
            
            if self.game_over:
                self.stdscr.clear()
                self.draw_board()
                self.stdscr.refresh()
                
                key = self.stdscr.getch()
                if key == self.controls["quit"]:
                    break
                elif key == ord('r') or key == ord('R'):
                    self.__init__(self.stdscr)
                    if not self.show_main_menu():
                        break
                    self.new_piece()
                    self.start_time = time.time()
                    last_move_time = time.time()
                continue
            
            if self.paused:
                self.stdscr.clear()
                self.draw_board()
                self.stdscr.refresh()
                
                key = self.stdscr.getch()
                if key == self.controls["pause"]:
                    self.paused = False
                    last_move_time = time.time()
                elif key == self.controls["quit"]:
                    break
                continue
            
            # Handle input
            key = self.stdscr.getch()
            
            if key == self.controls["quit"]:
                break
            elif key == self.controls["pause"]:
                self.paused = True
                continue
            elif key == self.controls["move_left"]:
                self.move_left()
            elif key == self.controls["move_right"]:
                self.move_right()
            elif key == self.controls["rotate_cw"]:
                self.rotate_piece(clockwise=True)
            elif key == self.controls["rotate_ccw"]:
                self.rotate_piece(clockwise=False)
            elif key == self.controls["soft_drop"]:
                self.move_down()
            elif key == self.controls["hard_drop"]:
                self.hard_drop()
            elif key == self.controls["hold"]:
                self.hold_current_piece()
            elif key == self.controls["toggle_ghost"]:
                self.ghost_enabled = not self.ghost_enabled
            
            # Automatic piece falling
            fall_time = 0.5 * (0.8 ** (self.level - 1))  # Speed increases with level
            
            if current_time - last_move_time > fall_time:
                self.move_down()
                last_move_time = current_time
            
            # Draw everything
            self.stdscr.clear()
            self.draw_board()
            self.stdscr.refresh()

def main(stdscr):
    # Initialize the game
    game = Textris(stdscr)
    game.run()

if __name__ == "__main__":
    # Run the game wrapped in curses
    try:
        wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
