from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Tuple

from ..algorithms.dfs import run_dfs
from ..algorithms.bfs import run_bfs
from ..algorithms.ids import run_ids
from ..algorithms.astar import run_astar_grid
from ..algorithms.dstar import run_dstar_demo
from ..algorithms.hill_climbing import run_hill_climbing_grid

router = APIRouter(prefix="/api/algorithms", tags=["Algorithms"])

class GraphSearchRequest(BaseModel):
    graph: Dict[str, List[Dict[str, Any]]]
    start: str
    goal: str
    max_depth: Optional[int] = 12

class GridPathRequest(BaseModel):
    grid: List[List[int]]
    start: List[int] # [row, col]
    goal: List[int]  # [row, col]
    heuristic: Optional[str] = "manhattan"
    allow_diagonal: Optional[bool] = False

class DStarRequest(BaseModel):
    grid: List[List[int]]
    start: List[int]
    goal: List[int]
    dynamic_obstacles: Optional[List[List[int]]] = None

@router.post("/dfs")
def dfs_endpoint(req: GraphSearchRequest):
    return run_dfs(req.graph, req.start, req.goal)

@router.post("/bfs")
def bfs_endpoint(req: GraphSearchRequest):
    return run_bfs(req.graph, req.start, req.goal)

@router.post("/ids")
def ids_endpoint(req: GraphSearchRequest):
    return run_ids(req.graph, req.start, req.goal, max_depth=req.max_depth or 12)

@router.post("/compare_search")
def compare_search_endpoint(req: GraphSearchRequest):
    dfs_res = run_dfs(req.graph, req.start, req.goal)
    bfs_res = run_bfs(req.graph, req.start, req.goal)
    ids_res = run_ids(req.graph, req.start, req.goal, max_depth=req.max_depth or 12)
    
    return {
        "start": req.start,
        "goal": req.goal,
        "dfs": {
            "path": dfs_res["path"],
            "path_length": dfs_res["path_length"],
            "nodes_expanded": dfs_res["nodes_expanded"],
            "time_ms": dfs_res["execution_time_ms"],
            "optimal": False,
            "memory_complexity": "O(bm)"
        },
        "bfs": {
            "path": bfs_res["path"],
            "path_length": bfs_res["path_length"],
            "nodes_expanded": bfs_res["nodes_expanded"],
            "time_ms": bfs_res["execution_time_ms"],
            "optimal": True,
            "memory_complexity": "O(b^d)"
        },
        "ids": {
            "path": ids_res["path"],
            "path_length": ids_res["path_length"],
            "nodes_expanded": ids_res["nodes_expanded"],
            "time_ms": ids_res["execution_time_ms"],
            "optimal": True,
            "memory_complexity": "O(bd)"
        },
        "comparison_summary": (
            f"Comparison on {req.start} -> {req.goal}: "
            f"BFS found optimal path length {bfs_res['path_length']} in {bfs_res['nodes_expanded']} expansions. "
            f"DFS expanded {dfs_res['nodes_expanded']} nodes but is not guaranteed optimal (length {dfs_res['path_length']}). "
            f"IDS combines DFS's small memory footprint with BFS optimality, expanding {ids_res['nodes_expanded']} nodes across depth iterations."
        )
    }

@router.post("/astar")
def astar_endpoint(req: GridPathRequest):
    start_tuple = (req.start[0], req.start[1])
    goal_tuple = (req.goal[0], req.goal[1])
    return run_astar_grid(
        grid=req.grid,
        start=start_tuple,
        goal=goal_tuple,
        heuristic_name=req.heuristic or "manhattan",
        allow_diagonal=req.allow_diagonal or False
    )

@router.post("/dstar")
def dstar_endpoint(req: DStarRequest):
    start_tuple = (req.start[0], req.start[1])
    goal_tuple = (req.goal[0], req.goal[1])
    dyn_obs = [(obs[0], obs[1]) for obs in req.dynamic_obstacles] if req.dynamic_obstacles else None
    return run_dstar_demo(
        grid=req.grid,
        start=start_tuple,
        goal=goal_tuple,
        dynamic_obstacles=dyn_obs
    )

@router.post("/hill_climbing")
def hill_climbing_endpoint(req: GridPathRequest):
    start_tuple = (req.start[0], req.start[1])
    goal_tuple = (req.goal[0], req.goal[1])
    return run_hill_climbing_grid(
        grid=req.grid,
        start=start_tuple,
        goal=goal_tuple
    )
