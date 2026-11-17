import pytest
from backend.algorithms.dfs import run_dfs
from backend.algorithms.bfs import run_bfs
from backend.algorithms.ids import run_ids
from backend.algorithms.astar import run_astar_grid
from backend.algorithms.dstar import run_dstar_demo
from backend.algorithms.hill_climbing import run_hill_climbing_grid
from backend.algorithms.simulated_annealing import run_simulated_annealing_generic

def test_graph_search_dfs_bfs_ids():
    graph = {
        "A": [{"target": "B", "weight": 1}, {"target": "C", "weight": 2}],
        "B": [{"target": "D", "weight": 1}],
        "C": [{"target": "D", "weight": 1}],
        "D": []
    }
    
    # Test BFS
    bfs_res = run_bfs(graph, "A", "D")
    assert bfs_res["found"] is True
    assert bfs_res["path"] in (["A", "B", "D"], ["A", "C", "D"])
    assert bfs_res["nodes_expanded"] > 0
    
    # Test DFS
    dfs_res = run_dfs(graph, "A", "D")
    assert dfs_res["found"] is True
    assert dfs_res["path"] in (["A", "B", "D"], ["A", "C", "D"])
    
    # Test IDS
    ids_res = run_ids(graph, "A", "D", max_depth=5)
    assert ids_res["found"] is True
    assert ids_res["path"] in (["A", "B", "D"], ["A", "C", "D"])

def test_astar_grid():
    grid = [
        [0, 0, 0, 0],
        [1, 1, 0, 1],
        [0, 0, 0, 0],
        [0, 1, 1, 0]
    ]
    res = run_astar_grid(grid, (0, 0), (2, 0))
    assert res["found"] is True
    assert res["path"][0] == [0, 0]
    assert res["path"][-1] == [2, 0]
    assert res["path_cost"] > 0

def test_dstar_dynamic_replan():
    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    res = run_dstar_demo(grid, (0, 0), (2, 3), dynamic_obstacles=[(1, 1)])
    assert len(res["initial_path"]) > 0
    assert len(res["replanned_path"]) > 0

def test_hill_climbing():
    grid = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    res = run_hill_climbing_grid(grid, (0, 0), (2, 2))
    assert res["found"] is True
    assert res["path"][-1] == [2, 2]

def test_simulated_annealing():
    # Minimize f(x) = (x - 7)^2
    res = run_simulated_annealing_generic(
        initial_state=0.0,
        energy_func=lambda x: (x - 7.0) ** 2,
        neighbor_func=lambda x: x + (0.5 if x < 7 else -0.5),
        initial_temp=50.0,
        cooling_rate=0.9
    )
    assert res["best_energy"] < 1.0
