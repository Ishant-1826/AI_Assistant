import pytest
from backend.puzzles.eight_puzzle import (
    solve_8_puzzle, is_solvable, count_inversions, generate_random_solvable, DEFAULT_GOAL
)
from backend.puzzles.towers_of_hanoi import solve_hanoi_recursive, solve_hanoi_bfs
from backend.puzzles.wumpus_world import run_wumpus_simulation

def test_eight_puzzle_solvability():
    solvable_state = [1, 2, 3, 4, 5, 6, 7, 0, 8]
    assert is_solvable(solvable_state, DEFAULT_GOAL) is True
    
    # Invert two adjacent tiles to create an unsolvable state
    unsolvable_state = [2, 1, 3, 4, 5, 6, 7, 8, 0]
    assert is_solvable(unsolvable_state, DEFAULT_GOAL) is False
    
    res = solve_8_puzzle(unsolvable_state, algorithm="astar")
    assert res["solvable"] is False

def test_eight_puzzle_astar_solution():
    easy_state = [1, 2, 3, 4, 5, 6, 0, 7, 8]
    res = solve_8_puzzle(easy_state, algorithm="astar")
    assert res["solvable"] is True
    assert res["found"] is True
    assert len(res["moves"]) > 0

def test_towers_of_hanoi():
    res = solve_hanoi_recursive(3)
    assert res["total_moves"] == 7
    assert res["min_moves_theoretical"] == 7
    
    bfs_res = solve_hanoi_bfs(3)
    assert bfs_res["total_moves"] == 7

def test_wumpus_world():
    res = run_wumpus_simulation(grid_size=4, max_steps=15)
    assert "steps" in res
    assert len(res["steps"]) > 0
    assert "hazard_probabilities" in res["steps"][0]
