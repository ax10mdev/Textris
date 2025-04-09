# TEXTRIS 🕹️

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Terminal-based Tetris implementation with modern features

![Gameplay Demo](assets/screenshots/gameplay.gif)

## ✨ Features
- Full-color terminal UI using curses
- Adaptive difficulty levels
- Score system with local leaderboard
- Ghost piece visualization
- Hold piece functionality
- Configurable controls
- Cross-platform support (Linux/macOS/WSL)

## 🚀 Installation
```bash
git clone https://github.com/ax10mdev/textris.git
cd textris
python3 textris.py
```

## 🎮 Controls
| Key          | Action               |
|--------------|----------------------|
| ←/→ or A/D   | Move piece           |
| ↑/W          | Rotate clockwise     |
| Z            | Rotate counter-clock |
| Space        | Hard drop            |
| C            | Hold piece           |
| P            | Pause                |
| Q/ESC        | Quit                 |

## 🛠 Development
```bash
# Run tests (add basic tests to your file)
python3 -m pytest -v

# Check code style
python3 -m pylint textris.py
```

## ⚖️ Legal Disclaimer
This is an **unofficial implementation** for educational purposes. Tetris® is a registered trademark of Tetris Holding. This project is not affiliated with or endorsed by Tetris Holding LLC.

## 📄 License
MIT - See [LICENSE](LICENSE) for details
