import heapq
import random
import time
import math
from collections import deque
from typing import Dict, List, Tuple, Any, Optional

DEFAULT_GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]

def count_inversions(state: List[int]) -> int:
    """Calculates number of inversions excluding the blank tile 0."""
    tiles = [x for x in state if x != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions

def is_solvable(initial: List[int], goal: List[int] = DEFAULT_GOAL) -> bool:
    """
    In an odd grid width (3x3), a state is solvable if and only if
    initial inversion count has the same parity (even/odd) as the goal state.
    """
    return (count_inversions(initial) % 2) == (count_inversions(goal) % 2)

def generate_random_solvable(goal: List[int] = DEFAULT_GOAL, shuffle_moves: int = 25) -> List[int]:
    """Generates a guaranteed solvable puzzle by randomly walking from the goal state."""
    state = list(goal)
    blank_idx = state.index(0)
    for _ in range(shuffle_moves):
        r, c = divmod(blank_idx, 3)
        valid_moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                valid_moves.append(nr * 3 + nc)
        target_idx = random.choice(valid_moves)
        state[blank_idx], state[target_idx] = state[target_idx], state[blank_idx]
        blank_idx = target_idx
    return state

def get_neighbors(state: Tuple[int, ...]) -> List[Tuple[Tuple[int, ...], str]]:
    """Returns valid neighbors and the move label ('UP', 'DOWN', 'LEFT', 'RIGHT')."""
    blank = state.index(0)
    r, c = divmod(blank, 3)
    neighbors = []
    
    # Moves represent moving a tile INTO the blank space
    moves = [
        ((-1, 0), "DOWN"),  # Tile above moves down into blank
        ((1, 0), "UP"),     # Tile below moves up into blank
        ((0, -1), "RIGHT"), # Tile on left moves right into blank
        ((0, 1), "LEFT")    # Tile on right moves left into blank
    ]
    
    for (dr, dc), move_name in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            target = nr * 3 + nc
            new_state = list(state)
            new_state[blank], new_state[target] = new_state[target], new_state[blank]
            neighbors.append((tuple(new_state), move_name))
            
    return neighbors

def manhattan_distance_8puzzle(state: Tuple[int, ...], goal_positions: Dict[int, Tuple[int, int]]) -> int:
    """Heuristic: sum of Manhattan distances of all tiles from their goal positions."""
    dist = 0
    for idx, val in enumerate(state):
        if val != 0:
            cr, cc = divmod(idx, 3)
            gr, gc = goal_positions[val]
            dist += abs(cr - gr) + abs(cc - gc)
    return dist

def solve_8_puzzle(
    initial_state: List[int],
    algorithm: str = "astar", # astar, bfs, dfs, ids, hill_climbing, simulated_annealing
    goal_state: Optional[List[int]] = None,
    max_nodes: int = 15000,
    depth_limit: int = 25
) -> Dict[str, Any]:
    """
    Solves 8-Puzzle using the chosen algorithm.
    """
    start_time = time.perf_counter()
    goal = goal_state or DEFAULT_GOAL
    
    initial_tuple = tuple(initial_state)
    goal_tuple = tuple(goal)
    
    # 1. Solvability Check
    solvable = is_solvable(initial_state, goal)
    if not solvable:
        return {
            "algorithm": algorithm,
            "solvable": False,
            "error": "The given puzzle configuration is mathematically unsolvable. Inversion parity differs from the goal.",
            "inversion_count": count_inversions(initial_state),
            "goal_inversion_count": count_inversions(goal),
            "initial_state": initial_state,
            "goal_state": goal,
            "moves": [],
            "path": [initial_state],
            "nodes_expanded": 0,
            "execution_time_ms": 0.0,
            "explanation": "This puzzle state is not solvable because tile inversions cannot change parity through legal moves on an odd-width board."
        }
        
    goal_positions = {val: divmod(idx, 3) for idx, val in enumerate(goal)}
    
    nodes_expanded = 0
    found = False
    solution_moves = []
    solution_states = [list(initial_tuple)]
    
    # Choose Algorithm
    algo_lower = algorithm.lower().replace(" ", "_").replace("-", "_")
    
    if algo_lower in ("astar", "a*"):
        # A* Search with Manhattan Heuristic
        counter = 0
        h_start = manhattan_distance_8puzzle(initial_tuple, goal_positions)
        # Heap item: (f_score, counter, g_score, state, path_states, moves)
        heap = [(h_start, counter, 0, initial_tuple, [initial_tuple], [])]
        visited_costs = {initial_tuple: 0}
        
        while heap and nodes_expanded < max_nodes:
            f, _, g, current, path_states, moves = heapq.heappop(heap)
            nodes_expanded += 1
            
            if current == goal_tuple:
                found = True
                solution_moves = moves
                solution_states = [list(s) for s in path_states]
                break
                
            for neighbor, move_name in get_neighbors(current):
                tentative_g = g + 1
                if tentative_g < visited_costs.get(neighbor, float('inf')):
                    visited_costs[neighbor] = tentative_g
                    h_val = manhattan_distance_8puzzle(neighbor, goal_positions)
                    counter += 1
                    heapq.heappush(heap, (
                        tentative_g + h_val,
                        counter,
                        tentative_g,
                        neighbor,
                        path_states + [neighbor],
                        moves + [move_name]
                    ))
                    
    elif algo_lower == "bfs":
        # BFS (optimal in move count)
        queue = deque([(initial_tuple, [initial_tuple], [])])
        visited = {initial_tuple}
        
        while queue and nodes_expanded < max_nodes:
            current, path_states, moves = queue.popleft()
            nodes_expanded += 1
            
            if current == goal_tuple:
                found = True
                solution_moves = moves
                solution_states = [list(s) for s in path_states]
                break
                
            for neighbor, move_name in get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path_states + [neighbor], moves + [move_name]))
                    
    elif algo_lower == "dfs":
        # Depth-Limited DFS
        stack = [(initial_tuple, [initial_tuple], [], 0)]
        visited_at_depth = {}
        
        while stack and nodes_expanded < max_nodes:
            current, path_states, moves, depth = stack.pop()
            nodes_expanded += 1
            
            if current == goal_tuple:
                found = True
                solution_moves = moves
                solution_states = [list(s) for s in path_states]
                break
                
            if depth < depth_limit:
                for neighbor, move_name in reversed(get_neighbors(current)):
                    if neighbor not in path_states: # avoid cycles in current branch
                        stack.append((neighbor, path_states + [neighbor], moves + [move_name], depth + 1))
                        
    elif algo_lower == "ids":
        # Iterative Deepening Search
        for limit in range(1, depth_limit + 1):
            stack = [(initial_tuple, [initial_tuple], [], 0)]
            limit_found = False
            
            while stack and nodes_expanded < max_nodes:
                current, path_states, moves, depth = stack.pop()
                nodes_expanded += 1
                
                if current == goal_tuple:
                    found = True
                    limit_found = True
                    solution_moves = moves
                    solution_states = [list(s) for s in path_states]
                    break
                    
                if depth < limit:
                    for neighbor, move_name in reversed(get_neighbors(current)):
                        if neighbor not in path_states:
                            stack.append((neighbor, path_states + [neighbor], moves + [move_name], depth + 1))
                            
            if limit_found or nodes_expanded >= max_nodes:
                break
                
    elif algo_lower in ("hill_climbing", "hillclimbing"):
        # Greedy Hill Climbing based on Manhattan heuristic
        current = initial_tuple
        path_states = [current]
        moves = []
        visited = {current}
        
        for _ in range(max_nodes):
            nodes_expanded += 1
            if current == goal_tuple:
                found = True
                solution_moves = moves
                solution_states = [list(s) for s in path_states]
                break
                
            current_h = manhattan_distance_8puzzle(current, goal_positions)
            neighbors = get_neighbors(current)
            
            # Find neighbor with strictly lower heuristic
            scored_neighbors = []
            for n_state, m_name in neighbors:
                if n_state not in visited:
                    h_val = manhattan_distance_8puzzle(n_state, goal_positions)
                    scored_neighbors.append((h_val, n_state, m_name))
                    
            if not scored_neighbors:
                break
                
            scored_neighbors.sort(key=lambda x: x[0])
            best_h, best_state, best_move = scored_neighbors[0]
            
            if best_h < current_h:
                current = best_state
                visited.add(current)
                path_states.append(current)
                moves.append(best_move)
            else:
                # Local minimum reached! Hill climbing cannot proceed further.
                break
                
        solution_moves = moves
        solution_states = [list(s) for s in path_states]
        
    elif algo_lower in ("simulated_annealing", "annealing"):
        # Simulated Annealing for 8-Puzzle
        current = initial_tuple
        path_states = [current]
        moves = []
        temp = 100.0
        cooling_rate = 0.96
        
        for _ in range(max_nodes):
            nodes_expanded += 1
            if current == goal_tuple:
                found = True
                solution_moves = moves
                solution_states = [list(s) for s in path_states]
                break
                
            current_h = manhattan_distance_8puzzle(current, goal_positions)
            neighbors = get_neighbors(current)
            if not neighbors or temp < 0.05:
                break
                
            cand_state, cand_move = random.choice(neighbors)
            cand_h = manhattan_distance_8puzzle(cand_state, goal_positions)
            delta_e = cand_h - current_h
            
            accept = False
            if delta_e < 0:
                accept = True
            else:
                prob = math.exp(-delta_e / temp)
                if random.random() < prob:
                    accept = True
                    
            if accept:
                current = cand_state
                path_states.append(current)
                moves.append(cand_move)
                
            temp *= cooling_rate
            
        solution_moves = moves
        solution_states = [list(s) for s in path_states]
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Educational explanation
    if found:
        explanation = (
            f"Successfully solved the 8-Puzzle in {len(solution_moves)} moves using {algorithm.upper()}! "
            f"Expanded {nodes_expanded} nodes in {execution_time_ms:.2f} ms. "
            f"{'A* with Manhattan Distance provides an admissible and consistent heuristic, guaranteeing the minimal path length.' if 'astar' in algo_lower else ''}"
            f"{'BFS explores level-by-level and guarantees the shortest solution in move count.' if algo_lower == 'bfs' else ''}"
        )
    else:
        explanation = (
            f"{algorithm.upper()} did not reach the goal within the limit (expanded {nodes_expanded} nodes). "
            f"{'Notice: Local search algorithms like Hill Climbing and Simulated Annealing make greedy/probabilistic moves and do NOT guarantee finding an optimal solution or even reaching the goal when local minima exist.' if algo_lower in ('hill_climbing', 'simulated_annealing') else 'The depth or expansion limit was reached before the goal state was reached.'}"
        )
        
    return {
        "algorithm": algorithm,
        "solvable": True,
        "found": found,
        "initial_state": initial_state,
        "goal_state": goal,
        "solution_cost": len(solution_moves),
        "moves": solution_moves,
        "path": solution_states,
        "nodes_expanded": nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
