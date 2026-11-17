import time
from collections import deque
from typing import Dict, List, Any

def run_bfs(
    graph: Dict[str, List[Dict[str, Any]]], 
    start: str, 
    goal: str
) -> Dict[str, Any]:
    """
    Executes Breadth-First Search on an adjacency list graph.
    graph format: { "A": [{"target": "B", "weight": 1}, ...], ... }
    """
    start_time = time.perf_counter()
    
    if start not in graph:
        return {
            "algorithm": "BFS",
            "found": False,
            "error": f"Start node '{start}' not found in graph.",
            "path": [],
            "visited_order": [],
            "steps": [],
            "nodes_expanded": 0,
            "execution_time_ms": 0.0,
            "explanation": "Start node does not exist in the graph."
        }
    
    # Queue stores (current_node, path_so_far, cost_so_far)
    queue = deque([(start, [start], 0.0)])
    visited = {start}
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
        "frontier": [q[0] for q in queue],
        "visited": list(visited),
        "description": f"Initialized BFS queue with start node '{start}'."
    })
    
    while queue:
        current, path, cost = queue.popleft() # FIFO behavior for BFS
        visited_order.append(current)
        nodes_expanded += 1
        step_num += 1
        
        steps.append({
            "step": step_num,
            "current": current,
            "action": "dequeue",
            "frontier": [q[0] for q in queue],
            "visited": list(visited),
            "description": f"Dequeued '{current}' from frontier."
        })
        
        if current == goal:
            found = True
            final_path = path
            final_cost = cost
            steps.append({
                "step": step_num + 1,
                "current": current,
                "action": "goal_reached",
                "frontier": [q[0] for q in queue],
                "visited": list(visited),
                "description": f"Goal '{goal}' reached! Optimal unweighted path found: {' -> '.join(path)}."
            })
            break
            
        neighbors = graph.get(current, [])
        new_enqueued = []
        for neighbor_info in neighbors:
            neighbor = neighbor_info["target"]
            edge_weight = neighbor_info.get("weight", 1.0)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], cost + edge_weight))
                new_enqueued.append(neighbor)
                
        steps.append({
            "step": step_num,
            "current": current,
            "action": "expand",
            "frontier": [q[0] for q in queue],
            "visited": list(visited),
            "description": f"Expanded '{current}', added new neighbors to FIFO queue: {new_enqueued}."
        })
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"BFS {'successfully found' if found else 'did not find'} the goal '{goal}' "
        f"from '{start}'. It expanded {nodes_expanded} nodes in {execution_time_ms:.2f} ms. "
        f"BFS explores level by level using a FIFO queue, guaranteeing the fewest number of edges / steps "
        f"to reach the goal in unweighted graphs. Time & space complexity are O(b^d)."
    )
    
    return {
        "algorithm": "BFS",
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
