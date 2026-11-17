import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.main import app

class CampusMindAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app"], "CampusMind AI")

    def test_chat_session_lifecycle(self):
        # 1. Create session
        create_res = self.client.post("/api/chat/sessions")
        self.assertEqual(create_res.status_code, 200)
        session_id = create_res.json()["id"]

        # 2. List sessions
        list_res = self.client.get("/api/chat/sessions")
        self.assertEqual(list_res.status_code, 200)
        ids = [s["id"] for s in list_res.json()]
        self.assertIn(session_id, ids)

        # 3. Rename session
        patch_res = self.client.patch(f"/api/chat/sessions/{session_id}", json={"title": "Midterm Prep"})
        self.assertEqual(patch_res.status_code, 200)

        # 4. Delete session
        del_res = self.client.delete(f"/api/chat/sessions/{session_id}")
        self.assertEqual(del_res.status_code, 200)

    def test_algorithms_endpoints(self):
        graph = {
            "A": [{"target": "B", "weight": 1}],
            "B": [{"target": "C", "weight": 2}],
            "C": []
        }
        res = self.client.post("/api/algorithms/compare_search", json={
            "graph": graph,
            "start": "A",
            "goal": "C"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["bfs"]["path"], ["A", "B", "C"])
        self.assertEqual(data["dfs"]["path"], ["A", "B", "C"])

    def test_puzzle_endpoints(self):
        # 8-Puzzle solve
        res = self.client.post("/api/puzzles/eight_puzzle/solve", json={
            "initial_state": [1, 2, 3, 4, 5, 6, 7, 0, 8],
            "algorithm": "astar"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["solvable"])
        self.assertTrue(data["found"])
        self.assertEqual(data["moves"], ["LEFT"])

        # Towers of Hanoi
        hanoi_res = self.client.post("/api/puzzles/towers_of_hanoi/solve", json={"num_disks": 3})
        self.assertEqual(hanoi_res.status_code, 200)
        self.assertEqual(hanoi_res.json()["total_moves"], 7)

        # Wumpus World
        wumpus_res = self.client.post("/api/puzzles/wumpus_world/simulate", json={"grid_size": 4, "max_steps": 10})
        self.assertEqual(wumpus_res.status_code, 200)
        self.assertIn("steps", wumpus_res.json())

    def test_probabilistic_endpoints(self):
        # Bayesian network
        bn_res = self.client.post("/api/probabilistic/bayesian_mastery", json={
            "evidence": {"q_pf": 1, "q_rec": 1, "q_ga": 1}
        })
        self.assertEqual(bn_res.status_code, 200)
        self.assertIn("posterior_probabilities", bn_res.json())

        # EM GMM
        em_res = self.client.post("/api/probabilistic/em_gmm", json={"k_clusters": 3, "max_iters": 15})
        self.assertEqual(em_res.status_code, 200)
        self.assertEqual(len(em_res.json()["clusters"]), 3)

        # HMM
        hmm_res = self.client.post("/api/probabilistic/hmm_tracker", json={"observations": [0, 1, 2]})
        self.assertEqual(hmm_res.status_code, 200)
        self.assertEqual(len(hmm_res.json()["viterbi_sequence"]), 3)

    def test_planner_endpoints(self):
        topics = [
            {"id": "1", "subject": "CS", "title": "AI", "estimated_hours": 3.0, "difficulty": 4, "priority": 5, "exam_day": 4}
        ]
        res = self.client.post("/api/planner/optimize", json={
            "topics": topics,
            "daily_available_hours": 4.0,
            "total_days": 5
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["timetable"]), 5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
