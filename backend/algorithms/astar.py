import heapq
import math
import time
from typing import Dict, List, Tuple, Any, Optional

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def euclidean_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def run_astar_grid(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    goal: Tuple[int, int], 
    heuristic_name: str = "manhattan",
    allow_diagonal: bool = False
) -> Dict[str, Any]:
    """
    Runs A* pathfinding on a 2D grid where:
    0 = free cell, 1 = obstacle.
    start and goal are (row, col) tuples.
    """
    start_time = time.perf_counter()
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    heuristic = manhattan_distance if heuristic_name == "manhattan" else euclidean_distance
    
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return {"found": False, "error": "Start outside grid bounds."}
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return {"found": False, "error": "Goal outside grid bounds."}
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return {"found": False, "error": "Start or goal is an obstacle."}
        
    # Directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if allow_diagonal:
        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        
    # Priority Queue: (f_score, counter, current_node)
    counter = 0
    start_h = heuristic(start, goal)
    open_heap = [(start_h, counter, start)]
    open_set_tracker = {start}
    
    came_from = {}
    g_score = {start: 0.0}
    f_score = {start: start_h}
    closed_set = set()
    
    steps = []
    visited_order = []
    nodes_expanded = 0
    found = False
    
    steps.append({
        "step": 0,
        "current": [start[0], start[1]],
        "action": "initialize",
        "open_count": 1,
        "closed_count": 0,
        "g": 0.0,
        "h": round(start_h, 2),
        "f": round(start_h, 2),
        "description": f"Initialized A* with start cell {start} (h={start_h:.1f})."
    })
    
    step_num = 1
    while open_heap:
        current_f, _, current = heapq.heappop(open_heap)
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        visited_order.append([current[0], current[1]])
        nodes_expanded += 1
        
        steps.append({
            "step": step_num,
            "current": [current[0], current[1]],
            "action": "expand",
            "g": round(g_score[current], 2),
            "h": round(heuristic(current, goal), 2),
            "f": round(current_f, 2),
            "open_count": len(open_heap),
            "closed_count": len(closed_set),
            "description": f"Expanding cell {current} with f(n) = g({g_score[current]:.1f}) + h({heuristic(current, goal):.1f}) = {current_f:.1f}"
        })
        step_num += 1
        
        if current == goal:
            found = True
            break
            
        for dr, dc in directions:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 1:
                    continue # Obstacle
                if neighbor in closed_set:
                    continue
                    
                move_cost = math.hypot(dr, dc)
                tentative_g = g_score[current] + move_cost
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h_val = heuristic(neighbor, goal)
                    f_val = tentative_g + h_val
                    f_score[neighbor] = f_val
                    
                    counter += 1
                    heapq.heappush(open_heap, (f_val, counter, neighbor))
                    open_set_tracker.add(neighbor)
                    
    final_path = []
    if found:
        curr = goal
        while curr in came_from:
            final_path.append([curr[0], curr[1]])
            curr = came_from[curr]
        final_path.append([start[0], start[1]])
        final_path.reverse()
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"A* Search {'found an optimal path' if found else 'failed to find a path'} "
        f"of length {len(final_path)} steps with total cost {g_score.get(goal, 0):.2f}. "
        f"It expanded {nodes_expanded} grid cells in {execution_time_ms:.2f} ms using the {heuristic_name} heuristic. "
        f"Because the heuristic is admissible (never overestimates the true distance to the goal) and consistent, "
        f"A* guarantees the shortest path while exploring significantly fewer nodes than uninformed BFS or Dijkstra."
    )
    
    return {
        "algorithm": "A*",
        "found": found,
        "start": [start[0], start[1]],
        "goal": [goal[0], goal[1]],
        "heuristic": heuristic_name,
        "path": final_path,
        "path_length": len(final_path),
        "path_cost": round(g_score.get(goal, 0.0), 2),
        "nodes_expanded": nodes_expanded,
        "visited_order": visited_order,
        "steps": steps[:250], # Sample for smooth frontend playback
        "total_steps_count": len(steps),
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
