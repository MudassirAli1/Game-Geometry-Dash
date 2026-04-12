# Game Settings and Constants

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "NEON DASH"

# Colors (Neon theme)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_YELLOW = (255, 255, 0)
NEON_RED = (255, 50, 50)
NEON_ORANGE = (255, 165, 0)
DARK_BG = (10, 10, 30)
GRID_COLOR = (30, 30, 60)

# Player settings
PLAYER_SIZE = 40
PLAYER_X = 200
GRAVITY = 1800  # pixels per second squared
JUMP_FORCE = -650  # pixels per second
MOVE_SPEED = 400  # pixels per second (horizontal scroll speed)
GROUND_Y = SCREEN_HEIGHT - 100  # Ground level

# Physics
MIN_DELTA = 1/120  # Minimum delta time to prevent physics explosions
MAX_DELTA = 1/30   # Maximum delta time to prevent spiral of death

# Level settings
LEVEL_LENGTH = 10000  # Total level length in pixels (increased for free flight)
OBSTACLE_SPACING_MIN = 300  # Minimum space between obstacles
OBSTACLE_SPACING_MAX = 600  # Maximum space between obstacles

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_SETTINGS = "settings"
STATE_LEVEL_EDITOR = "level_editor"

# Particle settings
MAX_PARTICLES = 100
PARTICLE_LIFETIME = 0.5  # seconds

# UI settings
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 60
FONT_SIZE_LARGE = 72
FONT_SIZE_MEDIUM = 36
FONT_SIZE_SMALL = 24

# Slow motion settings
SLOW_MOTION_FACTOR = 0.4
SLOW_MOTION_THRESHOLD = 150  # pixels from nearest obstacle
SLOW_MOTION_DURATION = 1.5  # seconds

# Skin colors
PLAYER_SKINS = [
    NEON_BLUE,
    NEON_PINK,
    NEON_GREEN,
    NEON_YELLOW,
    NEON_ORANGE,
]

# File paths
SAVE_FILE = "data/save.json"
