<p align="center">
  <img src="https://raw.githubusercontent.com/ax10mdev/Textris/main/assets/textris_ascii.png" width="400" alt="Textris ASCII Art">
  
  **A terminal-based Tetris tribute for old-school enthusiasts**  
  _Because sometimes you just need falling blocks in your life_ 💾
</p>

## 🕹 What's This?

A minimalist terminal implementation of the classic block-stacking game, made by a Linux enthusiast for:
- Quick nostalgia hits during coffee breaks ☕️
- Testing terminal color schemes 🌈
- Pretending to work while actually gaming 😎
- Remembering why we loved simple games

> **Note**: This is an **unofficial fan project** - not affiliated with Tetris rights holders

## 🚀 Quick Start

**For Linux/macOS/WSL warriors:**

```bash
# 1. Clone and enter
git clone https://github.com/ax10mdev/Textris.git
cd Textris

# 2. Run! (Python 3.6+ required)
python3 textris.py
```
**First-time controls cheat sheet:**
```
← → : Move      ↑ : Rotate  
↓   : Speed up  Space : SMASH DOWN  
P   : Pause    Q/ESC : Quit (when boss approaches)
```


## 🎮 Classic Features

- Pure terminal magic ✨ (no GUI dependencies)
- CRT-style color effects 📺
- Authentic 1984 feel (but actually works in modern terminals)
- Basic score tracking 📝
- Config file for keybind tweaks ⚙️

## 📸 Retro Preview

```
    ┌───────────────────────┐
    │                       │
    │  ██  ██      ██████   │ LEVEL: 3  
    │    ██████    ██  ██   │ SCORE: 1250
    │███████████████████████│ LINES: 15
    └───────────────────────┘
    NEXT: ⎔⎔      HOLD: ████
           ⎔⎔           ████
```
## 🤷 Why Exists?

- **2015 You:** "I should learn Python properly"  
- **2023 You:** *[still writing terminal games]*  
- **Reality:** It's just fun to make blocks fit ⎔

## ⚙️ Config Tweaks (Optional)

Create `~/.textris/config.json` for:
```json
{
  "colors": "retro",    // try "matrix" or "monochrome"
  "ghost": true,        // show where pieces land
  "sound": false,       // (coming never™)
  "start_level": 2      // 1-5 recommended
}
```


## 🚨 Disclaimer

- Not optimized for actual productivity  
- May cause sudden 1990s flashbacks  
- Zero warranty - it's free code ¯\_(ツ)_/¯

## 👾 Want More?

Found a bug? Got a wild idea?  
[Open an issue](https://github.com/ax10mdev/Textris/issues) - I make no promises but love weird suggestions!

---

_Made with ❤️, curses, and too much coffee_  
_© 2023 ax10mdev | Not your lawyer's problem™_
