import heapq
import math
import time
from typing import Dict, List, Tuple, Any, Optional

class DStarLite:
    def __init__(self, grid: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int]):
        self.grid = [row[:] for row in grid]
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.start = start
        self.goal = goal
        self.k_m = 0.0
        
        self.rhs: Dict[Tuple[int, int], float] = {}
        self.g: Dict[Tuple[int, int], float] = {}
        self.u: List[Tuple[Tuple[float, float], int, Tuple[int, int]]] = []
        self.open_tracker = set()
        self.counter = 0
        
        # Initialize rhs & g
        for r in range(self.rows):
            for c in range(self.cols):
                self.rhs[(r, c)] = float('inf')
                self.g[(r, c)] = float('inf')
                
        self.rhs[self.goal] = 0.0
        self._push(self.goal, self._calculate_key(self.goal))
        
    def _h(self, s1: Tuple[int, int], s2: Tuple[int, int]) -> float:
        # Manhattan or Euclidean heuristic
        return abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])

    def _calculate_key(self, s: Tuple[int, int]) -> Tuple[float, float]:
        val = min(self.g.get(s, float('inf')), self.rhs.get(s, float('inf')))
        return (val + self._h(self.start, s) + self.k_m, val)

    def _push(self, s: Tuple[int, int], key: Tuple[float, float]):
        self.counter += 1
        heapq.heappush(self.u, (key, self.counter, s))
        self.open_tracker.add(s)

    def _neighbors(self, s: Tuple[int, int]) -> List[Tuple[int, int]]:
        res = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = s[0] + dr, s[1] + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                res.append((nr, nc))
        return res

    def _cost(self, u: Tuple[int, int], v: Tuple[int, int]) -> float:
        if self.grid[u[0]][u[1]] == 1 or self.grid[v[0]][v[1]] == 1:
            return float('inf')
        return 1.0

    def _update_vertex(self, u: Tuple[int, int]):
        if u != self.goal:
            min_rhs = float('inf')
            for s_prime in self._neighbors(u):
                c = self._cost(u, s_prime)
                val = c + self.g.get(s_prime, float('inf'))
                if val < min_rhs:
                    min_rhs = val
            self.rhs[u] = min_rhs
            
        # If in queue, note that lazy removal will happen or push with new key
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            self._push(u, self._calculate_key(u))

    def compute_shortest_path(self, max_expansions: int = 5000) -> int:
        expansions = 0
        while self.u and expansions < max_expansions:
            # Check top key
            k_old, _, u = self.u[0]
            k_new = self._calculate_key(u)
            
            if k_old < k_new:
                heapq.heappop(self.u)
                self._push(u, k_new)
                continue
                
            if k_old >= self._calculate_key(self.start) and self.rhs.get(self.start, float('inf')) == self.g.get(self.start, float('inf')):
                break
                
            heapq.heappop(self.u)
            expansions += 1
            
            if self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                self.g[u] = self.rhs[u]
                for s in self._neighbors(u):
                    self._update_vertex(s)
            else:
                self.g[u] = float('inf')
                self._update_vertex(u)
                for s in self._neighbors(u):
                    self._update_vertex(s)
                    
        return expansions

    def extract_path(self) -> List[List[int]]:
        if self.g.get(self.start, float('inf')) == float('inf'):
            return []
        path = [list(self.start)]
        curr = self.start
        visited = {curr}
        
        while curr != self.goal:
            min_cost = float('inf')
            next_step = None
            for s_prime in self._neighbors(curr):
                c = self._cost(curr, s_prime)
                val = c + self.g.get(s_prime, float('inf'))
                if val < min_cost:
                    min_cost = val
                    next_step = s_prime
            if not next_step or next_step in visited:
                break
            curr = next_step
            visited.add(curr)
            path.append(list(curr))
            
        return path

def run_dstar_demo(
    grid: List[List[int]], 
    start: Tuple[int, int], 
    goal: Tuple[int, int],
    dynamic_obstacles: Optional[List[Tuple[int, int]]] = None
) -> Dict[str, Any]:
    """
    Demonstrates D* Lite with initial search and dynamic obstacle insertion + replanning.
    """
    start_time = time.perf_counter()
    
    # Initial plan
    dstar = DStarLite(grid, start, goal)
    initial_expansions = dstar.compute_shortest_path()
    initial_path = dstar.extract_path()
    
    replan_events = []
    
    # If dynamic obstacles provided or default selected from middle of initial path
    obstacles_to_add = dynamic_obstacles
    if not obstacles_to_add and len(initial_path) > 3:
        mid_idx = len(initial_path) // 2
        obstacles_to_add = [(initial_path[mid_idx][0], initial_path[mid_idx][1])]
        
    if obstacles_to_add:
        for obs in obstacles_to_add:
            r, c = obs
            if 0 <= r < dstar.rows and 0 <= c < dstar.cols and (r, c) != start and (r, c) != goal:
                dstar.grid[r][c] = 1 # Added obstacle
                dstar.k_m += dstar._h(dstar.start, dstar.goal) # Key modifier
                dstar._update_vertex((r, c))
                for n in dstar._neighbors((r, c)):
                    dstar._update_vertex(n)
                    
        replan_expansions = dstar.compute_shortest_path()
        replanned_path = dstar.extract_path()
        replan_events.append({
            "new_obstacles": obstacles_to_add,
            "replan_expansions": replan_expansions,
            "replanned_path": replanned_path,
            "replan_nodes_count": len(replanned_path)
        })
    else:
        replanned_path = initial_path
        replan_expansions = 0
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"D* Lite first computed an optimal initial path with {initial_expansions} expansions. "
        f"When dynamic obstacles {obstacles_to_add} appeared on the terrain, D* Lite did NOT restart from scratch. "
        f"Instead, it propagated cost changes only through affected rhs and g values in {replan_expansions} expansions, "
        f"seamlessly replanning a safe path around the newly introduced obstacles."
    )
    
    return {
        "algorithm": "D* Lite (Dynamic Pathfinding)",
        "start": [start[0], start[1]],
        "goal": [goal[0], goal[1]],
        "initial_path": initial_path,
        "initial_path_length": len(initial_path),
        "initial_expansions": initial_expansions,
        "dynamic_obstacles_added": obstacles_to_add or [],
        "replanned_path": replanned_path,
        "replanned_path_length": len(replanned_path),
        "replan_expansions": replan_expansions,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
