import unittest
import sys
import os

# Add root project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.algorithms.dfs import run_dfs
from backend.algorithms.bfs import run_bfs
from backend.algorithms.ids import run_ids
from backend.algorithms.astar import run_astar_grid
from backend.algorithms.dstar import run_dstar_demo
from backend.algorithms.hill_climbing import run_hill_climbing_grid
from backend.algorithms.simulated_annealing import run_simulated_annealing_generic

from backend.puzzles.eight_puzzle import (
    solve_8_puzzle, is_solvable, count_inversions, generate_random_solvable, DEFAULT_GOAL
)
from backend.puzzles.towers_of_hanoi import solve_hanoi_recursive, solve_hanoi_bfs
from backend.puzzles.wumpus_world import run_wumpus_simulation

from backend.probabilistic.bayesian_network import StudentConceptBayesianNetwork
from backend.probabilistic.em_algorithm import run_em_gmm
from backend.probabilistic.hmm import run_hmm_analysis
from backend.services.study_planner import generate_study_schedule_sa

class CampusMindBackendTests(unittest.TestCase):
    def test_graph_search(self):
        graph = {
            "A": [{"target": "B", "weight": 1}, {"target": "C", "weight": 2}],
            "B": [{"target": "D", "weight": 1}],
            "C": [{"target": "D", "weight": 1}],
            "D": []
        }
        bfs_res = run_bfs(graph, "A", "D")
        self.assertTrue(bfs_res["found"])
        self.assertIn(bfs_res["path"], [["A", "B", "D"], ["A", "C", "D"]])
        
        dfs_res = run_dfs(graph, "A", "D")
        self.assertTrue(dfs_res["found"])
        
        ids_res = run_ids(graph, "A", "D", max_depth=5)
        self.assertTrue(ids_res["found"])
        
    def test_astar_grid(self):
        grid = [
            [0, 0, 0, 0],
            [1, 1, 0, 1],
            [0, 0, 0, 0],
            [0, 1, 1, 0]
        ]
        res = run_astar_grid(grid, (0, 0), (2, 0))
        self.assertTrue(res["found"])
        self.assertEqual(res["path"][0], [0, 0])
        self.assertEqual(res["path"][-1], [2, 0])
        
    def test_dstar_replan(self):
        grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        res = run_dstar_demo(grid, (0, 0), (2, 2), dynamic_obstacles=[(1, 1)])
        self.assertGreater(len(res["initial_path"]), 0)
        self.assertGreater(len(res["replanned_path"]), 0)

    def test_hill_climbing(self):
        grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        res = run_hill_climbing_grid(grid, (0, 0), (2, 2))
        self.assertTrue(res["found"])
        self.assertEqual(res["path"][-1], [2, 2])
        
    def test_eight_puzzle(self):
        solvable_state = [1, 2, 3, 4, 5, 6, 7, 0, 8]
        self.assertTrue(is_solvable(solvable_state, DEFAULT_GOAL))
        res = solve_8_puzzle(solvable_state, algorithm="astar")
        self.assertTrue(res["solvable"])
        self.assertTrue(res["found"])
        
        unsolvable_state = [2, 1, 3, 4, 5, 6, 7, 8, 0]
        self.assertFalse(is_solvable(unsolvable_state, DEFAULT_GOAL))
        res_unsolvable = solve_8_puzzle(unsolvable_state, algorithm="astar")
        self.assertFalse(res_unsolvable["solvable"])
        
    def test_towers_of_hanoi(self):
        res = solve_hanoi_recursive(3)
        self.assertEqual(res["total_moves"], 7)
        self.assertEqual(res["min_moves_theoretical"], 7)

    def test_wumpus_world(self):
        res = run_wumpus_simulation(grid_size=4, max_steps=15)
        self.assertIn("steps", res)
        self.assertGreater(len(res["steps"]), 0)
        
    def test_bayesian_network(self):
        bn = StudentConceptBayesianNetwork()
        res = bn.infer_concept_mastery({"q_pf": 1, "q_rec": 1, "q_ga": 1})
        probs = res["posterior_probabilities"]
        self.assertGreater(probs["ProgrammingFundamentals"], 0.8)
        self.assertGreater(probs["Recursion"], 0.7)
        self.assertGreater(probs["GraphAlgorithms"], 0.6)
        
    def test_em_algorithm(self):
        res = run_em_gmm(k_clusters=3, max_iters=20)
        self.assertGreater(res["iterations_count"], 1)
        self.assertEqual(len(res["clusters"]), 3)
        
    def test_hmm_viterbi(self):
        obs = [0, 0, 1, 2, 2]
        res = run_hmm_analysis(obs)
        self.assertEqual(len(res["viterbi_sequence"]), 5)
        self.assertEqual(res["viterbi_sequence"][0], "Needs Practice")
        self.assertEqual(res["viterbi_sequence"][-1], "Confident")
        
    def test_study_planner(self):
        topics = [
            {"id": "1", "subject": "CS", "title": "Algorithms", "estimated_hours": 3.0, "difficulty": 4, "priority": 5, "exam_day": 3},
            {"id": "2", "subject": "Math", "title": "Calculus", "estimated_hours": 2.0, "difficulty": 3, "priority": 4, "exam_day": 5}
        ]
        res = generate_study_schedule_sa(topics, daily_available_hours=4.0, total_days=5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["timetable"]), 5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
