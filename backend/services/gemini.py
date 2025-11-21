import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_life_roadmap(request):
    prompt = (
        "You are a life planning assistant. "
        "Given the following user profile, generate a detailed, actionable roadmap for success. "
        "Include milestones, recommended actions, and tips for each phase of life.\n\n"
        f"- Name: {request.name}\n"
        f"- Age: {request.age}\n"
        f"- Career: {request.career}\n"
        f"- Desired Location: {request.desired_location}\n"
        f"- House Goal Age: {request.house_goal_age}\n"
        f"- Retirement Age: {request.retirement_age}\n"
        f"- Savings Goal: {request.savings_goal}\n"
        f"- Main Goals: {request.goals or 'Not specified'}\n"
        f"- Challenges: {request.challenges or 'Not specified'}\n"
        f"- Support System: {request.support or 'Not specified'}\n"
        "\nPresent the roadmap in a clear, year-by-year or phase-by-phase format with bullet points."
    )

    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)
    return response.text.strip()

def gemini_3day_roadmap(user_data, t, language):
    prompt = f"""
You are a motivational short-term life planner. Using the following data, generate a focused 3-day roadmap.

- Name: {user_data.get('Name')}
- Goal: {user_data.get('Main Goal')}
- Obstacles: {user_data.get('Obstacles')}
- Support: {user_data.get('Support')}
- Notes: {user_data.get('Other Notes')}
- Language: {language}

Present a step-by-step, daily plan for 3 days using short motivational and encouraging language.
"""
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)
    return response.text.strip()


def gemini_21day_roadmap(user_data, t, language):
    prompt = f"""
You are a 21-day transformation life coach. Based on the following client data, generate a personalized 21-day plan with motivation and clarity.

Name: {user_data.get('Name')}
Main Goal: {user_data.get('Main Goal')}
Obstacles: {user_data.get('Obstacles')}
Support: {user_data.get('Support')}
Relationship: {user_data.get('Relationship')}
Wellness: {user_data.get('Health and Wellness')}
Personal Life: {user_data.get('Personal Life')}
Notes: {user_data.get('Other Notes')}
Language: {language}

Respond in {language}. Structure the plan by week:
- Week 1: Preparation and mindset
- Week 2: Execution
- Week 3: Reflection and momentum

Use an uplifting and motivating tone.
"""
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)
    return response.text.strip()