# 🎮 NEON DASH - A Simple Game!

## What Is This?

This is a **game** where you control a little square box. The box moves forward all by itself. Your job? **Don't hit the spikes!**

Think of it like this:
- You have a little cube 🟦
- It runs forward automatically 🏃
- You see spikes 🔺 and blocks 🟧 on the ground
- You press SPACE to jump over them ⬆️
- If you hit a spike - **GAME OVER** 💥
- If you reach the end - **YOU WIN!** 🎉

That's it! Simple!

---

## How To Start The Game

### Step 1: Make Sure You Have Python

Python is a programming language. This game is made with Python.

**Do you have Python?** Open your terminal (or command prompt) and type:
```
python --version
```

If it says something like `Python 3.12.0` - you're good! If not, download Python from [python.org](https://www.python.org/downloads/)

### Step 2: Open The Game Folder

Find this folder on your computer. It's called `geometry_dash_clone`.

### Step 3: Install The Game's Tools

This game needs one tool called `pygame` (it draws things on screen).

Open your terminal in this folder and type:
```
uv sync
```

This downloads and installs everything the game needs. **You only do this once!**

### Step 4: Play!

Type:
```
uv run python main.py
```

**A window will pop up. You're playing!** 🎮

---

## How To Play

| What You Press | What Happens |
|----------------|--------------|
| **SPACE** or **UP arrow** | Jump! |
| **ESC** | Pause the game |
| **R** | Start over |

### The Rules:

1. **You move forward automatically** - you can't stop!
2. **Press SPACE to jump** - jump over spikes and blocks
3. **You can jump TWICE in the air** - this is called "double jump"
4. **Hit a spike?** - You die 💀
5. **Reach the green flag?** - You win! 🏆

---

## What's In The Game?

### Obstacles (Things That Can Kill You):

🔺 **Spikes** - Red triangles. Don't touch them!
🟧 **Blocks** - Orange rectangles. Jump over them!
🟩 **Jump Pads** - Green pads. They launch you high! (These help you!)

### The Game Screens:

1. **Main Menu** - Where you start. Click "START GAME"
2. **Playing** - The actual game! Jump over stuff!
3. **Pause** - Press ESC to take a break
4. **Game Over** - You died or won. Click "RETRY" to try again
5. **Settings** - Change your cube's color!

---

## What Do All The Files Do?

Don't care about code? **Skip this section!**

But if you're curious:

```
main.py              ← The boss. Makes everything run together.
game/
  settings.py        ← All the numbers (how fast, how high, colors)
  player.py          ← Your cube (jumps, spins, falls)
  obstacles.py       ← Spikes, blocks, jump pads
  ui.py              ← Buttons, menus, spark effects
```

**That's it!** Only 4 files with code. Very simple!

---

## I Want To Change Things!

### Make The Game Easier?

Open `game/settings.py` and change:
- `GRAVITY = 1800` → Make it **smaller** (like 1500) = You fall slower
- `JUMP_FORCE = -650` → Make it **more negative** (like -750) = You jump higher
- `MOVE_SPEED = 400` → Make it **smaller** (like 300) = You move slower

### Change Colors?

In `game/settings.py`, find `PLAYER_SKINS`. Change the numbers:
```python
PLAYER_SKINS = [
    (0, 255, 255),    # Blue
    (255, 0, 255),    # Pink
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
]
```

Each number is (Red, Green, Blue). From 0 to 255!

---

## Troubleshooting

**Game won't start?**
- Make sure you ran `uv sync` first
- Make sure you have Python 3.12 or newer

**No sound?**
- That's okay! The game works without sound
- The sounds are just simple beeps anyway

**Game too hard?**
- Change the settings (see above)
- Practice makes perfect!

---

## That's It!

**Have fun!** 🎮✨

The game is simple:
1. Start it
2. Press SPACE to jump
3. Don't hit spikes
4. Reach the end

Good luck! 🍀
