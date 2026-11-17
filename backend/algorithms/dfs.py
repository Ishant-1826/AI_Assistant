import time
from typing import Dict, List, Any, Optional

def run_dfs(
    graph: Dict[str, List[Dict[str, Any]]], 
    start: str, 
    goal: str
) -> Dict[str, Any]:
    """
    Executes Depth-First Search on an adjacency list graph.
    graph format: { "A": [{"target": "B", "weight": 1}, ...], ... }
    """
    start_time = time.perf_counter()
    
    if start not in graph:
        return {
            "found": False,
            "error": f"Start node '{start}' not found in graph.",
            "path": [],
            "visited_order": [],
            "steps": [],
            "nodes_expanded": 0,
            "execution_time_ms": 0.0,
            "explanation": "Start node does not exist in the graph."
        }
    
    # Stack stores (current_node, path_so_far, cost_so_far)
    stack = [(start, [start], 0.0)]
    visited = set()
    visited_order = []
    steps = []
    nodes_expanded = 0
    final_path = []
    final_cost = 0.0
    found = False
    
    step_num = 0
    steps.append({
        "step": step_num,
        "current": start,
        "action": "initialize",
        "frontier": [s[0] for s in stack],
        "visited": list(visited),
        "description": f"Initialized DFS with start node '{start}' on the stack."
    })
    
    while stack:
        current, path, cost = stack.pop() # LIFO behavior for DFS
        
        if current in visited:
            continue
            
        visited.add(current)
        visited_order.append(current)
        nodes_expanded += 1
        step_num += 1
        
        steps.append({
            "step": step_num,
            "current": current,
            "action": "visit",
            "frontier": [s[0] for s in stack],
            "visited": list(visited),
            "description": f"Popped '{current}' from stack and marked as visited."
        })
        
        if current == goal:
            found = True
            final_path = path
            final_cost = cost
            steps.append({
                "step": step_num + 1,
                "current": current,
                "action": "goal_reached",
                "frontier": [s[0] for s in stack],
                "visited": list(visited),
                "description": f"Goal node '{goal}' reached! Final path: {' -> '.join(path)}."
            })
            break
            
        # Get neighbors
        neighbors = graph.get(current, [])
        # In DFS, push in reverse order so the first listed neighbor is processed first
        for neighbor_info in reversed(neighbors):
            neighbor = neighbor_info["target"]
            edge_weight = neighbor_info.get("weight", 1.0)
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor], cost + edge_weight))
                
        steps.append({
            "step": step_num,
            "current": current,
            "action": "expand",
            "frontier": [s[0] for s in stack],
            "visited": list(visited),
            "description": f"Pushed unvisited neighbors of '{current}' onto the stack: {[n['target'] for n in neighbors if n['target'] not in visited]}."
        })
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"DFS {'successfully reached' if found else 'failed to find'} the goal '{goal}' "
        f"from '{start}'. It expanded {nodes_expanded} nodes in {execution_time_ms:.2f} ms. "
        f"Because DFS explores as deep as possible along each branch before backtracking using a LIFO stack, "
        f"it does not guarantee the shortest path in unweighted or weighted graphs, but has low memory complexity O(bm)."
    )
    
    return {
        "algorithm": "DFS",
        "found": found,
        "start": start,
        "goal": goal,
        "path": final_path,
        "path_length": len(final_path),
        "path_cost": final_cost,
        "visited_order": visited_order,
        "steps": steps,
        "nodes_expanded": nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
