from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()
# NOTE: main.py should include this router with prefix="/planner"
# so the final path will be /planner/3day


def simple_3day_roadmap(user_data: Dict[str, Any]) -> str:
    """
    Simple non-AI 3-day roadmap generator.
    This avoids API key / Gemini errors so your demo always works.
    """

    # Accept both camelCase and Title Case keys (from different callers)
    name = (
        user_data.get("name")
        or user_data.get("Name")
        or "Friend"
    )

    main_goal = (
        user_data.get("main_goal")
        or user_data.get("Main Goal")
        or "No goal provided yet."
    )

    obstacles = (
        user_data.get("obstacles")
        or user_data.get("Obstacles")
        or "Not specified yet."
    )

    support = (
        user_data.get("support")
        or user_data.get("Support")
        or "Not specified yet."
    )

    notes = (
        user_data.get("notes")
        or user_data.get("Other Notes")
        or ""
    )

    roadmap = f"""
3-Day Roadmap for {name}

Day 1 – Clarify & Prepare
• Write your main goal clearly: {main_goal}
• List your main obstacles: {obstacles}
• Identify 1–2 key sources of support: {support}
• Add any extra context or notes: {notes}

Day 2 – Take Focused Action
• Choose 1–3 concrete actions that move you closer to your goal.
• Block out 30–60 minutes for focused work on the goal.
• Use your support (people, tools, systems) to remove at least 1 obstacle.
• Reflect at the end of the day: What worked? What was hard?

Day 3 – Review, Adjust & Commit
• Review what you accomplished in the last 2 days.
• Adjust your plan: What will you keep doing, stop doing, and start doing?
• Decide 1 habit or routine you’ll continue after these 3 days.
• Write a short commitment statement to yourself about your next 30 days.
"""
    return roadmap.strip()


@router.post("/3day")
async def generate_3day_plan(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a simple 3-day roadmap based on the chat answers.
    Final path (with main.py prefix) will be:  /planner/3day
    """
    try:
        roadmap_text = simple_3day_roadmap(user_data)
        return {"roadmap": roadmap_text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating 3-day roadmap: {e}",
        )
