from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any

from ..puzzles.eight_puzzle import (
    solve_8_puzzle, generate_random_solvable, is_solvable, count_inversions, DEFAULT_GOAL
)
from ..puzzles.towers_of_hanoi import solve_hanoi_recursive, solve_hanoi_bfs
from ..puzzles.wumpus_world import run_wumpus_simulation

router = APIRouter(prefix="/api/puzzles", tags=["Puzzles"])

class EightPuzzleSolveRequest(BaseModel):
    initial_state: List[int] = Field(..., min_length=9, max_length=9)
    algorithm: Optional[str] = "astar"
    goal_state: Optional[List[int]] = None
    depth_limit: Optional[int] = 25

class HanoiRequest(BaseModel):
    num_disks: int = Field(3, ge=1, le=7)
    use_bfs: Optional[bool] = False

class WumpusRequest(BaseModel):
    grid_size: Optional[int] = 4
    wumpus_pos: Optional[List[int]] = None
    gold_pos: Optional[List[int]] = None
    pit_positions: Optional[List[List[int]]] = None
    max_steps: Optional[int] = 25

@router.post("/eight_puzzle/solve")
def eight_puzzle_solve(req: EightPuzzleSolveRequest):
    return solve_8_puzzle(
        initial_state=req.initial_state,
        algorithm=req.algorithm or "astar",
        goal_state=req.goal_state,
        depth_limit=req.depth_limit or 25
    )

@router.get("/eight_puzzle/random")
def eight_puzzle_random(moves: int = 16):
    puzzle = generate_random_solvable(DEFAULT_GOAL, shuffle_moves=moves)
    return {
        "initial_state": puzzle,
        "goal_state": DEFAULT_GOAL,
        "inversions": count_inversions(puzzle),
        "solvable": True
    }

@router.post("/eight_puzzle/validate")
def eight_puzzle_validate(state: List[int]):
    if len(state) != 9 or set(state) != set(range(9)):
        return {"valid": False, "error": "State must be a permutation of digits 0 through 8."}
    inversions = count_inversions(state)
    solvable = is_solvable(state, DEFAULT_GOAL)
    return {
        "valid": True,
        "solvable": solvable,
        "inversions": inversions,
        "parity": "even" if inversions % 2 == 0 else "odd",
        "explanation": "Solvable because inversion parity matches goal (even)." if solvable else "Unsolvable because inversion parity differs from goal."
    }

@router.post("/towers_of_hanoi/solve")
def hanoi_solve(req: HanoiRequest):
    if req.use_bfs and req.num_disks <= 4:
        return solve_hanoi_bfs(req.num_disks)
    return solve_hanoi_recursive(req.num_disks)

@router.post("/wumpus_world/simulate")
def wumpus_simulate(req: WumpusRequest):
    wumpus = (req.wumpus_pos[0], req.wumpus_pos[1]) if req.wumpus_pos else None
    gold = (req.gold_pos[0], req.gold_pos[1]) if req.gold_pos else None
    pits = [(p[0], p[1]) for p in req.pit_positions] if req.pit_positions else None
    return run_wumpus_simulation(
        grid_size=req.grid_size or 4,
        wumpus_pos=wumpus,
        gold_pos=gold,
        pit_positions=pits,
        max_steps=req.max_steps or 25
    )
