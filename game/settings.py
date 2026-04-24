# Game Settings - All the numbers that control the game

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "NEON DASH"

# Colors (Neon theme)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_YELLOW = (255, 255, 0)
NEON_RED = (255, 50, 50)
NEON_ORANGE = (255, 165, 0)
DARK_BG = (10, 10, 30)

# Player
PLAYER_SIZE = 40
PLAYER_X = 200
GRAVITY = 1800  # How fast you fall
JUMP_FORCE = -650  # How high you jump
MOVE_SPEED = 400  # How fast you move right
GROUND_Y = SCREEN_HEIGHT - 100  # Where the ground is

# Physics (don't change these unless you know what you're doing)
MIN_DELTA = 1/120
MAX_DELTA = 1/30

# Level
LEVEL_LENGTH = 10000  # How long the level is (in pixels)

# Game screens
STATE_LOADING = "loading"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_SETTINGS = "settings"

# UI
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 60
FONT_SIZE_LARGE = 72
FONT_SIZE_MEDIUM = 36
FONT_SIZE_SMALL = 24

# Player colors (you can pick these in settings)
PLAYER_SKINS = [
    NEON_BLUE,
    NEON_PINK,
    NEON_GREEN,
    NEON_YELLOW,
    NEON_ORANGE,
]

# Save file location
SAVE_FILE = "data/save.json"
