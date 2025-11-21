from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

router = APIRouter()

HISTORY_DIR = "history_logs"
os.makedirs(HISTORY_DIR, exist_ok=True)

class HistoryEntry(BaseModel):
    user_id: str
    plan_type: str
    entries: list  # Each entry should be a dict with timestamp, question, answer, bot_reply
    final_roadmap: str

@router.post("/history/save")
def save_history(data: HistoryEntry):
    file_path = os.path.join(HISTORY_DIR, f"{data.user_id}.json")
    with open(file_path, "w") as f:
        json.dump(data.dict(), f, indent=2)
    return {"message": "History saved successfully"}

@router.get("/history/{user_id}")
def get_history(user_id: str):
    file_path = os.path.join(HISTORY_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="History not found")
    with open(file_path, "r") as f:
        return json.load(f)
