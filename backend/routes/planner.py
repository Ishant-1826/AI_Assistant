from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..services.study_planner import generate_study_schedule_sa
from ..database import save_study_plan, get_study_plans

router = APIRouter(prefix="/api/planner", tags=["Study Planner"])

class TopicModel(BaseModel):
    id: str
    subject: str
    title: str
    estimated_hours: float
    difficulty: int
    priority: int
    exam_day: int

class PlannerRequest(BaseModel):
    topics: List[TopicModel]
    daily_available_hours: Optional[float] = 4.0
    total_days: Optional[int] = 7

class SavePlanRequest(BaseModel):
    title: str
    plan_data: Dict[str, Any]

@router.post("/optimize")
def optimize_schedule(req: PlannerRequest):
    topics_dicts = [t.model_dump() for t in req.topics]
    return generate_study_schedule_sa(
        topics=topics_dicts,
        daily_available_hours=req.daily_available_hours or 4.0,
        total_days=req.total_days or 7
    )

@router.post("/save")
def save_plan(req: SavePlanRequest):
    plan_id = save_study_plan(req.title, req.plan_data)
    return {"status": "success", "id": plan_id}

@router.get("/list")
def list_plans():
    return get_study_plans()
