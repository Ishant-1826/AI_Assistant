import time
from collections import deque
from typing import Dict, List, Tuple, Any

def solve_hanoi_recursive(num_disks: int) -> Dict[str, Any]:
    """
    Solves Towers of Hanoi using recursive divide-and-conquer (DFS on the call stack).
    Optimal number of moves is 2^n - 1.
    """
    start_time = time.perf_counter()
    
    # Pegs: lists where larger disks have larger numbers; top of peg is last element
    pegs = {
        "A": list(range(num_disks, 0, -1)),
        "B": [],
        "C": []
    }
    
    steps = []
    step_count = 0
    
    steps.append({
        "step": 0,
        "disk": None,
        "from_peg": None,
        "to_peg": None,
        "pegs": {k: list(v) for k, v in pegs.items()},
        "description": f"Initial state with {num_disks} disks on Peg A."
    })
    
    def move_disks(n: int, source: str, target: str, auxiliary: str):
        nonlocal step_count
        if n == 1:
            disk = pegs[source].pop()
            pegs[target].append(disk)
            step_count += 1
            steps.append({
                "step": step_count,
                "disk": disk,
                "from_peg": source,
                "to_peg": target,
                "pegs": {k: list(v) for k, v in pegs.items()},
                "description": f"Move Disk {disk} from Peg {source} to Peg {target}."
            })
            return
            
        # 1. Move n-1 disks from source to auxiliary using target
        move_disks(n - 1, source, auxiliary, target)
        
        # 2. Move nth disk from source to target
        disk = pegs[source].pop()
        pegs[target].append(disk)
        step_count += 1
        steps.append({
            "step": step_count,
            "disk": disk,
            "from_peg": source,
            "to_peg": target,
            "pegs": {k: list(v) for k, v in pegs.items()},
            "description": f"Move Disk {disk} from Peg {source} to Peg {target}."
        })
        
        # 3. Move n-1 disks from auxiliary to target using source
        move_disks(n - 1, auxiliary, target, source)

    move_disks(num_disks, "A", "C", "B")
    
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    min_moves = (2 ** num_disks) - 1
    
    explanation = (
        f"Solved Towers of Hanoi for {num_disks} disks in {step_count} moves ({execution_time_ms:.2f} ms). "
        f"The mathematical lower bound is 2^{num_disks} - 1 = {min_moves} moves. "
        f"The recursive divide-and-conquer strategy decomposes moving n disks into moving n-1 disks twice plus 1 move, "
        f"producing the optimal move sequence with recurrence T(n) = 2T(n-1) + 1 = 2^n - 1."
    )
    
    return {
        "algorithm": "Recursive Divide-and-Conquer (DFS)",
        "num_disks": num_disks,
        "total_moves": step_count,
        "min_moves_theoretical": min_moves,
        "execution_time_ms": round(execution_time_ms, 3),
        "steps": steps,
        "explanation": explanation
    }

def solve_hanoi_bfs(num_disks: int) -> Dict[str, Any]:
    """
    Demonstrates state-space graph search using BFS for Towers of Hanoi (for smaller n <= 4).
    Explores all valid configurations to prove shortest path from (A->all) to (C->all).
    """
    start_time = time.perf_counter()
    
    initial_state = (tuple(range(num_disks, 0, -1)), (), ())
    goal_state = ((), (), tuple(range(num_disks, 0, -1)))
    
    # Queue: (state, path_states, moves)
    # Peg indices: 0: A, 1: B, 2: C
    peg_names = ["A", "B", "C"]
    queue = deque([(initial_state, [initial_state], [])])
    visited = {initial_state}
    nodes_expanded = 0
    found = False
    
    final_path = []
    final_moves = []
    
    while queue:
        state, path, moves = queue.popleft()
        nodes_expanded += 1
        
        if state == goal_state:
            found = True
            final_path = path
            final_moves = moves
            break
            
        # Generate legal transitions
        for from_p in range(3):
            if not state[from_p]:
                continue
            disk = state[from_p][-1]
            for to_p in range(3):
                if from_p == to_p:
                    continue
                # Legal move if target peg is empty or has a larger top disk
                if not state[to_p] or state[to_p][-1] > disk:
                    new_pegs = [list(p) for p in state]
                    moved_disk = new_pegs[from_p].pop()
                    new_pegs[to_p].append(moved_disk)
                    next_state = (tuple(new_pegs[0]), tuple(new_pegs[1]), tuple(new_pegs[2]))
                    
                    if next_state not in visited:
                        visited.add(next_state)
                        move_info = {
                            "disk": disk,
                            "from_peg": peg_names[from_p],
                            "to_peg": peg_names[to_p]
                        }
                        queue.append((next_state, path + [next_state], moves + [move_info]))
                        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    min_moves = (2 ** num_disks) - 1
    
    # Format steps
    steps = []
    for idx, s in enumerate(final_path):
        m = final_moves[idx - 1] if idx > 0 else None
        steps.append({
            "step": idx,
            "disk": m["disk"] if m else None,
            "from_peg": m["from_peg"] if m else None,
            "to_peg": m["to_peg"] if m else None,
            "pegs": {"A": list(s[0]), "B": list(s[1]), "C": list(s[2])},
            "description": f"Move Disk {m['disk']} from Peg {m['from_peg']} to Peg {m['to_peg']}." if m else f"Initial state with {num_disks} disks on Peg A."
        })
        
    explanation = (
        f"BFS State-Space Search found the optimal {len(final_moves)} moves solution for {num_disks} disks "
        f"after expanding {nodes_expanded} distinct board states in {execution_time_ms:.2f} ms. "
        f"In Hanoi's state space graph (which forms a Sierpiński triangle fractal), BFS guarantees finding "
        f"the shortest move sequence of 2^{num_disks} - 1 = {min_moves} moves."
    )
    
    return {
        "algorithm": "BFS State-Space Search",
        "num_disks": num_disks,
        "total_moves": len(final_moves),
        "min_moves_theoretical": min_moves,
        "nodes_expanded": nodes_expanded,
        "execution_time_ms": round(execution_time_ms, 3),
        "steps": steps,
        "explanation": explanation
    }
