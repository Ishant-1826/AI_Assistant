import math
import time
from typing import Dict, List, Tuple, Any

def manhattan(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def run_hill_climbing_grid(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    goal: Tuple[int, int],
    max_steps: int = 200
) -> Dict[str, Any]:
    """
    Executes Hill Climbing (Greedy Local Search) for pathfinding on a grid.
    Moves greedily to the neighbor with the lowest heuristic value (distance to goal).
    Demonstrates getting trapped in local minima or plateaus.
    """
    start_time = time.perf_counter()
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    current = start
    current_h = manhattan(current, goal)
    
    path = [list(current)]
    steps = []
    visited = {current}
    stuck_in_local_optimum = False
    reached_goal = False
    
    steps.append({
        "step": 0,
        "current": list(current),
        "heuristic": round(current_h, 2),
        "action": "start",
        "description": f"Started at {current} with h = {current_h:.1f}"
    })
    
    step_num = 1
    while step_num <= max_steps:
        if current == goal:
            reached_goal = True
            steps.append({
                "step": step_num,
                "current": list(current),
                "heuristic": 0.0,
                "action": "goal_reached",
                "description": f"Goal {goal} reached successfully!"
            })
            break
            
        # Inspect 4-connected neighbors
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                h_val = manhattan((nr, nc), goal)
                neighbors.append(((nr, nc), h_val))
                
        if not neighbors:
            stuck_in_local_optimum = True
            steps.append({
                "step": step_num,
                "current": list(current),
                "heuristic": round(current_h, 2),
                "action": "dead_end",
                "description": f"Dead end reached at {current} with no valid free neighbors."
            })
            break
            
        # Find neighbor with minimum heuristic
        neighbors.sort(key=lambda x: x[1])
        best_neighbor, best_h = neighbors[0]
        
        # In steepest-ascent / greedy hill climbing, we only move if neighbor is strictly better
        if best_h < current_h and best_neighbor not in visited:
            current = best_neighbor
            current_h = best_h
            visited.add(current)
            path.append(list(current))
            steps.append({
                "step": step_num,
                "current": list(current),
                "heuristic": round(current_h, 2),
                "action": "climb_step",
                "description": f"Moved to better neighbor {current} with lower h = {current_h:.1f}"
            })
            step_num += 1
        else:
            # Trapped in local minimum or plateau (no neighbor improves the score)
            stuck_in_local_optimum = True
            steps.append({
                "step": step_num,
                "current": list(current),
                "heuristic": round(current_h, 2),
                "action": "local_optimum_trapped",
                "description": f"Trapped in local optimum at {current}! All available neighbors have h >= {current_h:.1f}."
            })
            break
            
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"Hill Climbing {'successfully reached the goal' if reached_goal else 'became trapped in a local minimum'}. "
        f"Total steps taken: {len(path)}. "
        f"{'It found a direct path.' if reached_goal else 'Because Hill Climbing only makes greedy local improvements and lacks backtracking or exploration of higher-cost states, it stopped when no immediate neighbor had a lower heuristic than the current position.'}"
    )
    
    return {
        "algorithm": "Hill Climbing",
        "found": reached_goal,
        "stuck_in_local_optimum": stuck_in_local_optimum,
        "start": list(start),
        "goal": list(goal),
        "path": path,
        "path_length": len(path),
        "steps": steps,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
