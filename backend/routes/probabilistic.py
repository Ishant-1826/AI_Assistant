from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from ..probabilistic.bayesian_network import run_bayesian_mastery_demo, StudentConceptBayesianNetwork
from ..probabilistic.em_algorithm import run_em_gmm
from ..probabilistic.hmm import run_hmm_analysis
from ..services.learning_analytics import get_complete_student_analytics

router = APIRouter(prefix="/api/probabilistic", tags=["Probabilistic Intelligence"])

class BayesianEvidenceRequest(BaseModel):
    evidence: Dict[str, int] # e.g. {"q_pf": 1, "q_rec": 0, "q_ga": 1}

class EMRequest(BaseModel):
    k_clusters: Optional[int] = 3
    max_iters: Optional[int] = 35
    custom_data: Optional[List[List[float]]] = None

class HMMRequest(BaseModel):
    observations: List[int] # e.g. [0, 0, 1, 2, 2, 2]

@router.post("/bayesian_mastery")
def bayesian_mastery_endpoint(req: Optional[BayesianEvidenceRequest] = None):
    ev = req.evidence if req else None
    return run_bayesian_mastery_demo(ev)

@router.post("/em_gmm")
def em_gmm_endpoint(req: Optional[EMRequest] = None):
    k = req.k_clusters if req else 3
    max_it = req.max_iters if req else 35
    data = req.custom_data if req else None
    return run_em_gmm(k_clusters=k, max_iters=max_it, custom_data=data)

@router.post("/hmm_tracker")
def hmm_tracker_endpoint(req: Optional[HMMRequest] = None):
    obs = req.observations if req else [0, 0, 1, 2, 2, 2]
    return run_hmm_analysis(obs)

@router.get("/analytics")
def analytics_overview():
    return get_complete_student_analytics()
