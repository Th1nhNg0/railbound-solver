# Track Puzzle Solver: TODO List

This README contains a list of tasks and improvements for our Track Puzzle Solver, based on recent discussions and insights.

## Current Status

- Can solve all of level 1, except for level 1-13A
- Current implementation is too slow due to excessive possibilities

## TODO List

1. Optimize Track Placement Algorithm

   - [ ] Reduce the number of possible tracks to consider
   - [ ] Implement a smarter track placement strategy

2. Implement 3-Way Track Generation Rules

   - [ ] Only generate 3-way tracks when:
     - [ ] A car intersects with a track
     - [ ] A car rides a track for the 2nd time

3. Optimize Performance

   - [ ] Implement the new 3-way generation rules to reduce possibilities
   - [ ] Re-evaluate performance after implementing new rules

4. Code Refactoring

   - [ ] Review and refactor code for better readability and maintainability
   - [ ] Ensure proper commenting and documentation

5. Testing

   - [ ] Develop comprehensive test cases
   - [ ] Ensure all levels, including 1-13A, can be solved efficiently

6. Performance Benchmarking

   - [ ] Compare performance before and after optimizations
   - [ ] Set performance targets for solving different levels

7. User Interface Improvements
   - [ ] Consider adding user controls for visualization speed
   - [ ] Implement pause/resume functionality for the solver

## Notes

- The key insight is to limit 3-way track generation to specific scenarios, which should significantly reduce the number of possibilities to check.
- Remember that for a 3-way to be useful, it needs to be accessed from all 3 directions.
- The visualization doesn't need to be overly complex; focus on functionality first.
