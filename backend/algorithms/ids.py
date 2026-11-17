import time
from typing import Dict, List, Any

def run_ids(
    graph: Dict[str, List[Dict[str, Any]]], 
    start: str, 
    goal: str,
    max_depth: int = 15
) -> Dict[str, Any]:
    """
    Executes Iterative Deepening Search (IDS) on an adjacency list graph.
    Runs Depth-Limited Search (DLS) repeatedly for depth = 0, 1, ..., max_depth.
    """
    start_time = time.perf_counter()
    
    if start not in graph:
        return {
            "algorithm": "IDS",
            "found": False,
            "error": f"Start node '{start}' not found in graph.",
            "path": [],
            "visited_order": [],
            "steps": [],
            "iterations": [],
            "nodes_expanded": 0,
            "execution_time_ms": 0.0,
            "explanation": "Start node does not exist in the graph."
        }
    
    total_nodes_expanded = 0
    all_steps = []
    iterations_info = []
    found = False
    final_path = []
    final_cost = 0.0
    overall_visited_order = []
    
    step_num = 0
    
    for limit in range(max_depth + 1):
        depth_visited = []
        # Stack items: (node, path, cost, current_depth)
        stack = [(start, [start], 0.0, 0)]
        limit_found = False
        iteration_steps = []
        
        all_steps.append({
            "step": step_num,
            "action": "start_iteration",
            "current": start,
            "depth_limit": limit,
            "description": f"=== Starting Depth-Limited Search iteration with Depth Limit = {limit} ==="
        })
        step_num += 1
        
        # In DLS with graph cycles, keep track of nodes on current path to prevent loops
        while stack:
            current, path, cost, depth = stack.pop()
            depth_visited.append(current)
            if current not in overall_visited_order:
                overall_visited_order.append(current)
            total_nodes_expanded += 1
            step_num += 1
            
            all_steps.append({
                "step": step_num,
                "action": "visit",
                "current": current,
                "depth": depth,
                "depth_limit": limit,
                "path": path,
                "description": f"Iteration limit={limit}: Visited '{current}' at depth {depth}."
            })
            
            if current == goal:
                found = True
                limit_found = True
                final_path = path
                final_cost = cost
                all_steps.append({
                    "step": step_num + 1,
                    "action": "goal_reached",
                    "current": current,
                    "depth_limit": limit,
                    "description": f"Goal '{goal}' discovered at depth limit {limit}! Path: {' -> '.join(path)}"
                })
                break
                
            if depth < limit:
                neighbors = graph.get(current, [])
                for neighbor_info in reversed(neighbors):
                    neighbor = neighbor_info["target"]
                    weight = neighbor_info.get("weight", 1.0)
                    # Avoid cyclic backtracks along the current branch
                    if neighbor not in path:
                        stack.append((neighbor, path + [neighbor], cost + weight, depth + 1))
                        
        iterations_info.append({
            "depth_limit": limit,
            "nodes_visited_count": len(depth_visited),
            "visited_sequence": depth_visited,
            "goal_found": limit_found
        })
        
        if found:
            break
            
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"IDS {'successfully found' if found else 'did not find'} the goal '{goal}' "
        f"within depth {len(iterations_info)-1}. Cumulative nodes expanded: {total_nodes_expanded} "
        f"across {len(iterations_info)} depth iterations in {execution_time_ms:.2f} ms. "
        f"IDS combines the minimal O(bd) memory complexity of DFS with the completeness and optimality "
        f"of BFS for unweighted graphs, as upper tree levels have negligible overhead compared to the deepest level."
    )
    
    return {
        "algorithm": "IDS",
        "found": found,
        "start": start,
        "goal": goal,
        "path": final_path,
        "path_length": len(final_path),
        "path_cost": final_cost,
        "depth_reached": len(iterations_info) - 1,
        "iterations": iterations_info,
        "visited_order": overall_visited_order,
        "steps": all_steps,
        "nodes_expanded": total_nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
