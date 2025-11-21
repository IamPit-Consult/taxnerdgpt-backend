from pydantic import BaseModel
from typing import Optional

class PlannerRequest(BaseModel):
    name: str
    age: int
    career: str
    desired_location: str
    house_goal_age: int
    retirement_age: int
    savings_goal: float
    goals: Optional[str] = None
    challenges: Optional[str] = None
    support: Optional[str] = None

class PlannerResponse(BaseModel):
    roadmap: str
