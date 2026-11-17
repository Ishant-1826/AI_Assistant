import re
from typing import Dict, Any, Optional, Tuple

from ..algorithms.dfs import run_dfs
from ..algorithms.bfs import run_bfs
from ..algorithms.ids import run_ids
from ..algorithms.astar import run_astar_grid
from ..algorithms.dstar import run_dstar_demo
from ..algorithms.hill_climbing import run_hill_climbing_grid
from ..puzzles.eight_puzzle import solve_8_puzzle, generate_random_solvable, is_solvable
from ..puzzles.towers_of_hanoi import solve_hanoi_recursive, solve_hanoi_bfs
from ..puzzles.wumpus_world import run_wumpus_simulation
from ..probabilistic.bayesian_network import run_bayesian_mastery_demo
from ..probabilistic.em_algorithm import run_em_gmm
from ..probabilistic.hmm import run_hmm_analysis
from ..services.study_planner import generate_study_schedule_sa

def route_and_execute_tool(message: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """
    Detects if the user prompt requests an algorithm or puzzle run.
    Returns: (tool_name, tool_result_data, tool_summary_for_llm)
    """
    msg_lower = message.lower()
    
    # 1. 8-Puzzle Intent
    if "8 puzzle" in msg_lower or "8-puzzle" in msg_lower or "eight puzzle" in msg_lower or "sliding puzzle" in msg_lower:
        # Check if algorithm is specified
        algo = "astar"
        if "bfs" in msg_lower:
            algo = "bfs"
        elif "dfs" in msg_lower:
            algo = "dfs"
        elif "ids" in msg_lower or "iterative deepening" in msg_lower:
            algo = "ids"
        elif "hill climbing" in msg_lower:
            algo = "hill_climbing"
        elif "simulated annealing" in msg_lower:
            algo = "simulated_annealing"
            
        # Check if initial state is in message, e.g. [1, 2, 3, 0, 4, 6, 7, 5, 8]
        # Ignore the '8' in '8-puzzle' when extracting tile digits
        clean_msg = re.sub(r'\b8\s*[- ]?\s*puzzle\b', '', message, flags=re.IGNORECASE)
        nums = re.findall(r'\b[0-8]\b', clean_msg)
        if len(nums) >= 9:
            initial_state = [int(x) for x in nums[:9]]
            if len(set(initial_state)) != 9:
                initial_state = generate_random_solvable(shuffle_moves=12)
        else:
            initial_state = generate_random_solvable(shuffle_moves=14)
            
        result = solve_8_puzzle(initial_state=initial_state, algorithm=algo)
        summary = (
            f"[ACTUAL 8-PUZZLE EXECUTION RESULT]:\n"
            f"Algorithm: {result.get('algorithm', algo)}\n"
            f"Solvable: {result.get('solvable')}\n"
            f"Initial State: {result.get('initial_state', initial_state)}\n"
            f"Goal State: {result.get('goal_state', [1,2,3,4,5,6,7,8,0])}\n"
            f"Moves Taken ({result.get('solution_cost', 0)}): {' -> '.join(result.get('moves', []))}\n"
            f"Nodes Expanded: {result.get('nodes_expanded', 0)}\n"
            f"Execution Time: {result.get('execution_time_ms', 0)} ms\n"
            f"Explanation: {result.get('explanation', '')}"
        )
        return "eight_puzzle", result, summary

    # 2. Towers of Hanoi Intent
    if "towers of hanoi" in msg_lower or "tower of hanoi" in msg_lower or "hanoi" in msg_lower:
        # Extract disk count if present
        disk_match = re.search(r'\b([1-7])\s*(?:disk|disks)\b', msg_lower)
        num_disks = int(disk_match.group(1)) if disk_match else 3
        
        if "bfs" in msg_lower and num_disks <= 4:
            result = solve_hanoi_bfs(num_disks)
        else:
            result = solve_hanoi_recursive(num_disks)
            
        summary = (
            f"[ACTUAL TOWERS OF HANOI EXECUTION RESULT]:\n"
            f"Algorithm: {result['algorithm']}\n"
            f"Disks: {result['num_disks']}\n"
            f"Total Moves: {result['total_moves']} (Theoretical Minimum: {result['min_moves_theoretical']})\n"
            f"Execution Time: {result['execution_time_ms']} ms\n"
            f"Explanation: {result['explanation']}"
        )
        return "towers_of_hanoi", result, summary

    # 3. Wumpus World Intent
    if "wumpus" in msg_lower or "wumpus world" in msg_lower:
        result = run_wumpus_simulation()
        summary = (
            f"[ACTUAL WUMPUS WORLD SIMULATION RESULT]:\n"
            f"Victory: {result['victory']}\n"
            f"Total Steps: {result['total_steps']}\n"
            f"Wumpus Position: {result['wumpus']}\n"
            f"Gold Position: {result['gold']}\n"
            f"Pits: {result['pits']}\n"
            f"Explanation: {result['explanation']}"
        )
        return "wumpus_world", result, summary

    # 4. Study Planner Intent
    if any(k in msg_lower for k in ["study plan", "study timetable", "timetable", "schedule my exam", "plan my revision", "study schedule"]):
        # Default student topics for planning
        sample_topics = [
            {"id": "1", "subject": "AI", "title": "A* & Heuristic Search", "estimated_hours": 3.0, "difficulty": 4, "priority": 5, "exam_day": 4},
            {"id": "2", "subject": "AI", "title": "Bayesian Networks & HMMs", "estimated_hours": 3.0, "difficulty": 5, "priority": 5, "exam_day": 4},
            {"id": "3", "subject": "Math", "title": "Linear Algebra & Matrices", "estimated_hours": 2.5, "difficulty": 3, "priority": 4, "exam_day": 6},
            {"id": "4", "subject": "CS", "title": "Operating Systems - Paging", "estimated_hours": 2.0, "difficulty": 3, "priority": 3, "exam_day": 7},
            {"id": "5", "subject": "CS", "title": "Database Normalization", "estimated_hours": 2.0, "difficulty": 2, "priority": 3, "exam_day": 7}
        ]
        result = generate_study_schedule_sa(sample_topics, daily_available_hours=4.0, total_days=7)
        summary = (
            f"[ACTUAL SIMULATED ANNEALING STUDY SCHEDULE RESULT]:\n"
            f"Optimization Score: {result['quality_score']}%\n"
            f"Cooling Iterations: {result['iterations']}\n"
            f"Total Days: {result['total_days']}\n"
            f"Daily Available Hours: {result['daily_capacity']}\n"
            f"Explanation: {result['explanation']}"
        )
        return "study_planner", result, summary

    # 5. Bayesian Network / Concept Mastery Intent
    if ("bayesian network" in msg_lower or "bayes net" in msg_lower or "concept mastery" in msg_lower) and ("solve" in msg_lower or "run" in msg_lower or "calculate" in msg_lower or "evidence" in msg_lower or "mastery" in msg_lower):
        result = run_bayesian_mastery_demo()
        summary = (
            f"[ACTUAL BAYESIAN NETWORK INFERENCE RESULT]:\n"
            f"Posteriors: {result['posterior_probabilities']}\n"
            f"Evidence Likelihood: {result['evidence_likelihood']}\n"
            f"Explanation: {result['explanation']}"
        )
        return "bayesian_network", result, summary

    # 6. Expectation Maximization (EM) Intent
    if "expectation maximization" in msg_lower or "em algorithm" in msg_lower or "gmm" in msg_lower:
        result = run_em_gmm(k_clusters=3, max_iters=25)
        summary = (
            f"[ACTUAL EM / GMM CLUSTERING RESULT]:\n"
            f"Converged Iterations: {result['iterations_count']}\n"
            f"Clusters: {[{c['name']: {'weight': c['weight'], 'mean_hrs': c['mean_study_hours'], 'accuracy': c['mean_quiz_accuracy']}} for c in result['clusters']]}\n"
            f"Explanation: {result['explanation']}"
        )
        return "em_algorithm", result, summary

    # 7. Hidden Markov Model (HMM) Intent
    if "hidden markov" in msg_lower or "hmm" in msg_lower or "viterbi" in msg_lower:
        result = run_hmm_analysis([0, 0, 1, 2, 2, 2])
        summary = (
            f"[ACTUAL HMM & VITERBI RESULT]:\n"
            f"Observations: {result['observations']}\n"
            f"Viterbi Optimal Hidden States: {' -> '.join(result['viterbi_sequence'])}\n"
            f"Observation Likelihood: {result['total_observation_likelihood']}\n"
            f"Explanation: {result['explanation']}"
        )
        return "hmm", result, summary

    # 8. Graph Search (BFS / DFS / IDS) Intent
    if any(k in msg_lower for k in ["find path using bfs", "run bfs", "run dfs", "iterative deepening", "graph search"]):
        sample_graph = {
            "A": [{"target": "B", "weight": 2}, {"target": "C", "weight": 5}],
            "B": [{"target": "D", "weight": 4}, {"target": "E", "weight": 1}],
            "C": [{"target": "F", "weight": 3}],
            "D": [{"target": "G", "weight": 2}],
            "E": [{"target": "G", "weight": 3}],
            "F": [{"target": "G", "weight": 6}],
            "G": []
        }
        if "dfs" in msg_lower:
            result = run_dfs(sample_graph, "A", "G")
            tool_name = "dfs"
        elif "ids" in msg_lower or "iterative" in msg_lower:
            result = run_ids(sample_graph, "A", "G", max_depth=5)
            tool_name = "ids"
        else:
            result = run_bfs(sample_graph, "A", "G")
            tool_name = "bfs"
            
        summary = (
            f"[ACTUAL GRAPH SEARCH {result['algorithm']} RESULT]:\n"
            f"Start: {result['start']} -> Goal: {result['goal']}\n"
            f"Path: {' -> '.join(result['path'])}\n"
            f"Nodes Expanded: {result['nodes_expanded']}\n"
            f"Execution Time: {result['execution_time_ms']} ms\n"
            f"Explanation: {result['explanation']}"
        )
        return tool_name, result, summary

    return None, None, None
