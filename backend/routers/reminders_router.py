
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import json

router = APIRouter()

REMINDER_DIR = "reminder_logs"
os.makedirs(REMINDER_DIR, exist_ok=True)

class Reminder(BaseModel):
    timestamp: str
    message: str
    related_goal: str

class ReminderResponse(BaseModel):
    user_id: str
    reminders: List[Reminder]

class ReminderUpdateRequest(BaseModel):
    reminders: List[Reminder]

class ReminderDeleteRequest(BaseModel):
    index: int

@router.get("/reminders/{user_id}", response_model=ReminderResponse)
def get_reminders(user_id: str):
    file_path = os.path.join(REMINDER_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        return {"user_id": user_id, "reminders": []}
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"user_id": user_id, "reminders": data}

@router.post("/reminders/{user_id}/update")
def update_reminders(user_id: str, req: ReminderUpdateRequest):
    file_path = os.path.join(REMINDER_DIR, f"{user_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([r.dict() for r in req.reminders], f, indent=2)
    return {"message": "Reminders updated"}

@router.post("/reminders/{user_id}/delete")
def delete_reminder(user_id: str, req: ReminderDeleteRequest):
    file_path = os.path.join(REMINDER_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="No reminders found")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if req.index < 0 or req.index >= len(data):
        raise HTTPException(status_code=400, detail="Invalid index")
    removed = data.pop(req.index)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return {"message": "Reminder deleted", "removed": removed}
