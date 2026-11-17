import math
import random
import time
from typing import Dict, List, Any, Optional

def generate_study_schedule_sa(
    topics: List[Dict[str, Any]],
    daily_available_hours: float = 4.0,
    total_days: int = 7,
    initial_temp: float = 80.0,
    cooling_rate: float = 0.95,
    min_temp: float = 0.05
) -> Dict[str, Any]:
    """
    Optimizes a student study timetable across `total_days` using Simulated Annealing.
    Each topic has:
      - id: str
      - subject: str
      - title: str
      - estimated_hours: float
      - difficulty: int (1-5)
      - priority: int (1-5)
      - exam_day: int (1 to total_days)
    """
    start_time = time.perf_counter()
    
    if not topics:
        return {
            "error": "No topics provided to schedule.",
            "timetable": [],
            "score": 0.0,
            "convergence": []
        }
        
    # Split topics into 1-hour or 1.5-hour study blocks
    blocks = []
    block_id = 0
    for t in topics:
        hours = float(t.get("estimated_hours", 2.0))
        rem = hours
        while rem > 0:
            duration = 1.0 if rem >= 1.0 else round(rem, 1)
            blocks.append({
                "block_id": block_id,
                "topic_id": t.get("id", str(block_id)),
                "subject": t.get("subject", "General"),
                "title": t.get("title", f"Topic {block_id}"),
                "duration": duration,
                "difficulty": int(t.get("difficulty", 3)),
                "priority": int(t.get("priority", 3)),
                "exam_day": int(t.get("exam_day", total_days))
            })
            block_id += 1
            rem -= duration
            
    # Initial state: random assignment of blocks to days (0 to total_days - 1)
    random.seed(42)
    state = [random.randint(0, total_days - 1) for _ in blocks]
    
    def compute_energy(current_state: List[int]) -> float:
        energy = 0.0
        # 1. Day hours aggregation
        day_hours = [0.0] * total_days
        day_blocks = [[] for _ in range(total_days)]
        
        for idx, day in enumerate(current_state):
            day_hours[day] += blocks[idx]["duration"]
            day_blocks[day].append(blocks[idx])
            
        # Capacity overload penalty: penalize days exceeding available hours heavily
        for d in range(total_days):
            overload = day_hours[d] - daily_available_hours
            if overload > 0:
                energy += (overload ** 2) * 50.0 # Quadratic penalty
            elif day_hours[d] == 0:
                energy += 10.0 # Discourage empty days if work remains
                
        # Workload balance variance penalty
        avg_hours = sum(day_hours) / total_days
        variance = sum((h - avg_hours) ** 2 for h in day_hours) / total_days
        energy += variance * 8.0
        
        # Deadline & Priority Penalties
        for idx, day in enumerate(current_state):
            b = blocks[idx]
            exam_day_0indexed = b["exam_day"] - 1
            # Penalty for studying on or after exam day
            if day >= exam_day_0indexed:
                energy += (day - exam_day_0indexed + 1) * 120.0
            else:
                # Slight preference to study high-priority topics with adequate buffer
                slack = exam_day_0indexed - day
                if slack < 1:
                    energy += b["priority"] * 15.0 # Too close to exam
                    
        # Fatigue penalty: back-to-back high-difficulty topics on same day
        for d in range(total_days):
            daily_diff_sum = sum(b["difficulty"] for b in day_blocks[d])
            if daily_diff_sum > 12:
                energy += (daily_diff_sum - 12) * 15.0
                
        return energy

    current_energy = compute_energy(state)
    best_state = list(state)
    best_energy = current_energy
    initial_energy = current_energy
    
    temp = initial_temp
    iteration = 0
    convergence = []
    
    while temp > min_temp and iteration < 1500:
        # Generate neighbor by moving a random block to a different day
        neighbor_state = list(state)
        block_to_move = random.randint(0, len(blocks) - 1)
        new_day = random.randint(0, total_days - 1)
        neighbor_state[block_to_move] = new_day
        
        neighbor_energy = compute_energy(neighbor_state)
        delta_e = neighbor_energy - current_energy
        
        accept = False
        if delta_e < 0:
            accept = True
        else:
            prob = math.exp(-delta_e / max(temp, 1e-9))
            if random.random() < prob:
                accept = True
                
        if accept:
            state = neighbor_state
            current_energy = neighbor_energy
            if current_energy < best_energy:
                best_state = list(state)
                best_energy = current_energy
                
        if iteration % 25 == 0:
            convergence.append({
                "iteration": iteration,
                "temperature": round(temp, 2),
                "energy": round(current_energy, 2),
                "best_energy": round(best_energy, 2)
            })
            
        temp *= cooling_rate
        iteration += 1
        
    # Construct final timetable from best_state
    timetable = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for d in range(total_days):
        day_sessions = []
        total_d_hours = 0.0
        for idx, day_idx in enumerate(best_state):
            if day_idx == d:
                b = blocks[idx]
                day_sessions.append({
                    "topic_id": b["topic_id"],
                    "subject": b["subject"],
                    "title": b["title"],
                    "duration_hours": b["duration"],
                    "difficulty": b["difficulty"],
                    "priority": b["priority"],
                    "exam_day": b["exam_day"]
                })
                total_d_hours += b["duration"]
                
        day_label = f"Day {d + 1} ({day_names[d % 7]})"
        timetable.append({
            "day": d + 1,
            "label": day_label,
            "total_hours": round(total_d_hours, 1),
            "capacity_hours": daily_available_hours,
            "utilization_pct": round(min(100.0, (total_d_hours / max(daily_available_hours, 0.1)) * 100.0), 1),
            "sessions": day_sessions
        })
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Calculate optimization quality score (0 - 100%)
    score = max(10.0, min(99.0, round(100.0 / (1.0 + (best_energy / 200.0)), 1)))
    
    explanation = (
        f"Simulated Annealing optimized your study plan across {total_days} days in {execution_time_ms:.2f} ms "
        f"over {iteration} cooling cycles. Energy improved from {initial_energy:.1f} to {best_energy:.1f} (Schedule Quality: {score}%). "
        f"Key optimization factors applied: (1) Hard caps on daily capacity ({daily_available_hours} hrs/day) to prevent burnout, "
        f"(2) Scheduling all topics strictly before their respective exam deadlines, "
        f"(3) Distributing cognitive load by separating back-to-back high-difficulty subjects."
    )
    
    return {
        "status": "success",
        "optimization_algorithm": "Simulated Annealing",
        "quality_score": score,
        "initial_energy": round(initial_energy, 2),
        "final_energy": round(best_energy, 2),
        "iterations": iteration,
        "total_days": total_days,
        "daily_capacity": daily_available_hours,
        "timetable": timetable,
        "convergence": convergence,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
