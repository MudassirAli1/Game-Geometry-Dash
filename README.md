# 🎮 NEON DASH - Geometry Dash Clone

A smooth, neon-themed Geometry Dash inspired platformer game built with Python and Pygame.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### Core Gameplay
- **Auto-scrolling platformer** with smooth camera follow
- **Single jump mechanic** with realistic gravity physics
- **Frame-rate independent movement** using delta time
- **Increasing difficulty** as you progress through the level

### Obstacles
- 🔺 **Spikes** - Ground and ceiling spikes with forgiving hitboxes
- 🟧 **Blocks** - Static and moving blocks with neon grid textures
- 🟩 **Jump Pads** - Auto-launch pads that boost you into the air
- **Randomized generation** - Different experience every playthrough

### Visual Effects
- ✨ **Neon dark theme** inspired by Geometry Dash
- 🌟 **Parallax background** with twinkling stars and clouds
- 💥 **Particle effects** on jump, death, and player trail
- 🔴 **Red flash screen** on death
- 🌈 **Color-changing background** based on progress
- 🔄 **Rotating player cube** with trail effect

### UI/UX
- **Main Menu** with animated title and buttons
- **In-game HUD** showing score, progress bar, and best score
- **Pause menu** (ESC key)
- **Game Over screen** with retry and score display
- **Settings screen** with player skin selector

### Special Features
1. **Slow-motion mode** - Automatically activates when near obstacles
2. **Player skin selector** - 5 neon colors to choose from
3. **Color-changing background** - Progress-based theme shifts
4. **Level editor** - Basic grid-based obstacle placer (coming soon)

### Sound System
- 🎵 Procedurally generated sound effects (no external files needed)
- Jump, death, and jump pad sounds
- Easy to replace with custom audio files

### Data Persistence
- 💾 Local JSON save system
- Stores best score, last score, and skin preference
- Automatically saves on game over

## 🚀 Installation & Running

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Navigate to the game directory:**
   ```bash
   cd geometry_dash_clone
   ```

2. **Install dependencies (if not already installed):**
   ```bash
   uv sync
   ```

3. **Run the game:**
   ```bash
   uv run python main.py
   ```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` / `UP` | Jump |
| `ESC` | Pause / Resume |
| `R` | Restart game |
| `Mouse` | Click buttons |

## 🏗️ Project Structure

```
geometry_dash_clone/
│
├── main.py                 # Main game loop and entry point
├── game/
│   ├── __init__.py
│   ├── settings.py         # Game constants and configuration
│   ├── player.py           # Player physics and rendering
│   ├── obstacles.py        # Obstacle types and level generation
│   └── ui.py               # UI elements, particles, background
│
├── assets/
│   ├── sounds/             # Optional sound files
│   └── images/             # Optional image assets
│
├── data/
│   └── save.json           # Local save data
│
├── pyproject.toml          # uv project configuration
└── README.md               # This file
```

## 🎯 Game Design

### Physics
- **Gravity:** 1800 pixels/s²
- **Jump Force:** -650 pixels/s
- **Scroll Speed:** 400 pixels/s
- **Single jump only** - no double jumping!

### Scoring
- Score based on distance traveled (10 points per % progress)
- 1000 points for completing the level
- Best score saved locally

### Difficulty Progression
- **0-30%:** Mostly spikes, gentle spacing
- **30-60%:** Mix of spikes and blocks, moving obstacles appear
- **60-100%:** All obstacle types, tighter spacing, more moving blocks

## 🎨 Customization

### Adding Custom Sounds
Place `.wav` files in `assets/sounds/`:
- `jump.wav` - Jump sound
- `death.wav` - Death sound
- `jump_pad.wav` - Jump pad sound

### Adding Custom Skins
Edit `PLAYER_SKINS` in `game/settings.py` to add more colors:
```python
PLAYER_SKINS = [
    (0, 255, 255),    # Blue
    (255, 0, 255),    # Pink
    # Add more RGB tuples here
]
```

### Adjusting Difficulty
Modify these constants in `game/settings.py`:
- `GRAVITY` - Higher = faster fall
- `JUMP_FORCE` - More negative = higher jump
- `MOVE_SPEED` - Faster = harder
- `OBSTACLE_SPACING_MIN/MAX` - Tighter = harder

## 🔧 Technical Details

### Frame-Rate Independence
All movement uses delta time to ensure consistent gameplay across different frame rates:
```python
position += velocity * dt
```

### Collision Detection
- **AABB (Axis-Aligned Bounding Box)** collision
- Smaller hitboxes for spikes (more forgiving)
- Player collision box slightly smaller than visual

### Performance
- Obstacles behind player are culled
- Level generates ahead of player in chunks
- Particle system with automatic cleanup

## 🐛 Troubleshooting

**Game won't start:**
- Ensure Python 3.10+ is installed
- Run `uv sync` to install dependencies

**No sound:**
- Game works without sound files (uses generated placeholders)
- Check pygame mixer initialization

**Performance issues:**
- Lower `MAX_PARTICLES` in settings.py
- Reduce background star count

## 📝 Future Enhancements

- [ ] Complete level editor with save/load
- [ ] Multiple levels
- [ ] Online leaderboard
- [ ] Music sync system (BPM-based obstacle timing)
- [ ] More player customization options
- [ ] Practice mode with checkpoints
- [ ] Achievement system

## 📄 License

MIT License - Feel free to modify and distribute!

## 🙏 Credits

- **Inspired by:** Geometry Dash by RobTop Games
- **Built with:** Python + Pygame
- **Package Manager:** uv

---

**Enjoy the dash! 🎮✨**
