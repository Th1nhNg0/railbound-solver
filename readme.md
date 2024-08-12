# Railbound Puzzle Solver

Railbound Puzzle Solver is a Python-based tool designed to solve puzzles from the game Railbound, a comfy, track-bending puzzle game developed by Afterburn. This solver features a graphical editor for recreating Railbound puzzles and an automated solver that can find solutions to complex track layouts.

## About Railbound

Railbound is a puzzle game about a pair of dogs on a train journey around the world. Players connect and sever railways across different landscapes to help everyone reach their homes. The game features:

- 240+ puzzles across different parts of the world
- Various train-inspired mechanics including tunnels and semaphores
- Comic-book-esque visuals and a relaxing original soundtrack

For more information about the original game, visit [the official Railbound website](https://afterburn.games/railbound).

## Solver Features

- **Puzzle Editor**: A graphical user interface for recreating Railbound puzzles.
- **Automated Solver**: An algorithm that can find solutions to the recreated puzzles.
- **Customizable Grid**: Adjustable grid size to accommodate various puzzle complexities.
- **Multiple Tile Types**: Support for different track types, including straight tracks, curves, and T-junctions.
- **Cart Placement**: Ability to place and rotate carts on the grid.
- **Save/Load Functionality**: Save your recreated puzzles and load them later for solving or further editing.

## Requirements

- Python 3.7+
- Tkinter
- Pillow (PIL)
- NumPy
- OpenCV-Python

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/railbound-puzzle-solver.git
   cd railbound-puzzle-solver
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Puzzle Editor

To launch the puzzle editor:

```
python editor.py
```

- Use the grid size controls to set up your puzzle board.
- Select tiles from the dropdown menu and click on the grid to place them.
- Use the "Set Destination" button to mark the goal location.
- Toggle "Cart Place Mode" to add carts to your puzzle.
- Save your created puzzle using the "Save Grid" button.

### Puzzle Solver

To solve a puzzle:

```
python solve.py path/to/your/puzzle.json
```

Replace `path/to/your/puzzle.json` with the path to the JSON file of the puzzle you want to solve.

## How It Works

The solver uses a breadth-first search algorithm to explore possible track configurations. It places tracks, moves carts, and backtracks when necessary to find a valid solution that allows all carts to reach the destination.

## Current Status and TODO List

### Current Status

- Can solve all of level 1, except for level 1-13A
- Current implementation is too slow due to excessive possibilities

### TODO List

1. Optimize Track Placement Algorithm

   - [x] Reduce the number of possible tracks to consider
   - [x] Implement a smarter track placement strategy

2. Implement 3-Way Track Generation Rules

   - [x] Only generate 3-way tracks when:
     - [x] A car intersects with a track

3. Code Refactoring

   - [ ] Review and refactor code for better readability and maintainability
   - [ ] Ensure proper commenting and documentation

4. Testing

   - [ ] Develop comprehensive test cases
   - [ ] Ensure all levels, including 1-13A, can be solved efficiently

### Notes

- The key insight is to limit 3-way track generation to specific scenarios, which should significantly reduce the number of possibilities to check.
- Remember that for a 3-way to be useful, it needs to be accessed from all 3 directions.
- The visualization doesn't need to be overly complex; focus on functionality first.

## Contributing

Contributions to the Railbound Puzzle Solver are welcome! Please feel free to submit pull requests, create issues or suggest improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project was inspired by Railbound, a puzzle game developed by Afterburn.
- Special thanks to the Python community for the excellent libraries that made this project possible.

## Disclaimer

This solver is a fan-made project and is not affiliated with, endorsed, sponsored, or specifically approved by Afterburn or any of its subsidiaries or its affiliates. The official Railbound game is available on [Steam](https://store.steampowered.com/app/1967510/Railbound/), [App Store](https://apps.apple.com/us/app/railbound/id1619014876), [Google Play](https://play.google.com/store/apps/details?id=games.afterburn.railbound), [GOG](https://www.gog.com/game/railbound), and [Humble Store](https://www.humblebundle.com/store/railbound).
