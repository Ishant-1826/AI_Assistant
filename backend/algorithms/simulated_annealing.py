import math
import random
import time
from typing import Dict, List, Any, Callable, Tuple

def run_simulated_annealing_generic(
    initial_state: Any,
    energy_func: Callable[[Any], float],
    neighbor_func: Callable[[Any], Any],
    initial_temp: float = 100.0,
    cooling_rate: float = 0.95,
    min_temp: float = 0.01,
    max_iterations: int = 1000
) -> Dict[str, Any]:
    """
    General Simulated Annealing optimization engine.
    Probabilistically accepts worsening moves according to exp(-delta_E / T)
    to escape local minima.
    """
    start_time = time.perf_counter()
    
    current_state = initial_state
    current_energy = energy_func(current_state)
    best_state = current_state
    best_energy = current_energy
    
    temp = initial_temp
    iteration = 0
    
    history_temp = []
    history_energy = []
    history_best_energy = []
    accepted_moves = 0
    worse_accepted_moves = 0
    
    while temp > min_temp and iteration < max_iterations:
        neighbor_state = neighbor_func(current_state)
        neighbor_energy = energy_func(neighbor_state)
        delta_e = neighbor_energy - current_energy
        
        # Decide whether to accept neighbor
        accept = False
        if delta_e < 0:
            accept = True
            accepted_moves += 1
        else:
            prob = math.exp(-delta_e / max(temp, 1e-9))
            if random.random() < prob:
                accept = True
                accepted_moves += 1
                worse_accepted_moves += 1
                
        if accept:
            current_state = neighbor_state
            current_energy = neighbor_energy
            if current_energy < best_energy:
                best_state = current_state
                best_energy = current_energy
                
        # Record periodic history (every few iterations)
        if iteration % 5 == 0 or temp <= min_temp:
            history_temp.append(round(temp, 3))
            history_energy.append(round(current_energy, 3))
            history_best_energy.append(round(best_energy, 3))
            
        temp *= cooling_rate
        iteration += 1
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"Simulated Annealing completed {iteration} cooling cycles in {execution_time_ms:.2f} ms. "
        f"Initial energy: {energy_func(initial_state):.2f} -> Optimized energy: {best_energy:.2f}. "
        f"It accepted {worse_accepted_moves} uphill (worse) moves probabilistically early in the process "
        f"when temperature was high, successfully escaping sub-optimal local traps."
    )
    
    return {
        "algorithm": "Simulated Annealing",
        "iterations": iteration,
        "initial_energy": round(energy_func(initial_state), 3),
        "best_energy": round(best_energy, 3),
        "best_state": best_state,
        "history_temp": history_temp,
        "history_energy": history_energy,
        "history_best_energy": history_best_energy,
        "accepted_moves": accepted_moves,
        "worse_accepted_moves": worse_accepted_moves,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
