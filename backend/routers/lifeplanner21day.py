
import os
from dotenv import load_dotenv
import google.generativeai as genai
from localization import translations
from services.gemini import gemini_21day_roadmap

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

LIFE_PLANNER_21DAY_QUESTIONS = [
    ("Name", "What is your name?"),
    ("Main Goal", "What is your main goal for the next 21 days?"),
    ("Obstacles", "What obstacles might you face?"),
    ("Support", "Who or what can support you?"),
    ("Relationship", "How would you describe your current relationship or what would you like to improve in your relationships?"),
    ("Health and Wellness", "What are your health and wellness goals for these 21 days?"),
    ("Personal Life", "What personal aspect would you like to work on or improve during this period?"),
    ("Other Notes", "Anything else you'd like to share?"),
    # ...add more as needed...
]

def get_user_input(t, language="en"):
    print(t["planner_21day_title"])
    user_data = {}
    user_data["Name"] = input("¿Cuál es tu nombre? " if language == "es" else "What is your name? ")
    user_data["Main Goal"] = input("¿Cuál es tu objetivo principal para los próximos 21 días? " if language == "es" else "What is your main goal for the next 21 days? ")
    user_data["Obstacles"] = input("¿Qué obstáculos podrías enfrentar? " if language == "es" else "What obstacles might you face? ")
    user_data["Support"] = input("¿Quién o qué puede apoyarte? " if language == "es" else "Who or what can support you? ")
    user_data["Relationship"] = input("¿Cómo describirías tu relación actual o qué te gustaría mejorar en tus relaciones? " if language == "es" else "How would you describe your current relationship or what would you like to improve in your relationships? ")
    user_data["Health and Wellness"] = input("¿Qué metas tienes para tu salud y bienestar en estos 21 días? " if language == "es" else "What are your health and wellness goals for these 21 days? ")
    user_data["Personal Life"] = input("¿Qué aspecto personal te gustaría trabajar o mejorar en este periodo? " if language == "es" else "What personal aspect would you like to work on or improve during this period? ")
    user_data["Other Notes"] = input("¿Algo más que quieras compartir? " if language == "es" else "Anything else you'd like to share? ")
    return user_data

def gemini_21day_roadmap(user_data, category_insights, language="en"):
    """Generate 21-day roadmap using Gemini"""
    model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
    
    prompt = f"""
    Create a detailed 21-day personal development roadmap for {user_data.get('name', 'the user')}.
    
    User Goals and Information:
    - Main Goal: {user_data.get('main_goal', 'Not specified')}
    - Obstacles: {user_data.get('obstacles', 'Not specified')}
    - Support System: {user_data.get('support', 'Not specified')}
    - Relationship Goals: {user_data.get('relationship', 'Not specified')}
    - Wellness Goals: {user_data.get('wellness', 'Not specified')}
    - Personal Development: {user_data.get('personal_life', 'Not specified')}
    - Additional Notes: {user_data.get('notes', 'Not specified')}
    
    Create a comprehensive 21-day plan with:
    1. Week 1 (Days 1-7): Foundation Building
    2. Week 2 (Days 8-14): Momentum Building
    3. Week 3 (Days 15-21): Mastery and Integration
    
    For each week, provide:
    - Daily actionable tasks
    - Progress milestones
    - Reflection questions
    - Potential challenges and solutions
    
    Make it practical, achievable, and motivating.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def main():
    # Language selection (if running standalone)
    print("Select your language / Seleccione su idioma:")
    print("1. English")
    print("2. Español")
    lang_choice = input("Enter your choice (1-2): ").strip()
    language = "es" if lang_choice == "2" else "en"
    t = translations[language]

    user_data = get_user_input(t, language)
    roadmap = gemini_21day_roadmap(user_data, t, language)
    print("\n" + (t["planner_21day_title"] if "planner_21day_title" in t else "Your 21-Day Personalized Roadmap:") + "\n")
    print(roadmap)

    # Optionally offer to save as PDF
    create_pdf = input(t["save_pdf_prompt"]).strip().lower()
    if create_pdf in [t["yes"], "si", "sí", "yes"]:
        from fpdf import FPDF
        def save_roadmap_to_pdf(roadmap_text, filename="21day_roadmap.pdf"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in roadmap_text.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf.output(filename)
            print(t["pdf_saved"].format(filename=filename))
        save_roadmap_to_pdf(roadmap)

if __name__ == "__main__":
    main()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

router = APIRouter()

class Planner21Request(BaseModel):
    name: str
    main_goal: str
    obstacles: str
    support: str
    relationship: str
    wellness: str
    personal_life: str
    notes: str
    plan_type: str = "21day"

def gemini_21day_roadmap(user_data, category_insights=None, language="en"):
    """Generate 21-day roadmap using Gemini"""
    model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
    
    prompt = f"""
    Create a detailed 21-day personal development roadmap for {user_data.get('name', 'the user')}.
    
    User Goals and Information:
    - Main Goal: {user_data.get('main_goal', 'Not specified')}
    - Obstacles: {user_data.get('obstacles', 'Not specified')}
    - Support System: {user_data.get('support', 'Not specified')}
    - Relationship Goals: {user_data.get('relationship', 'Not specified')}
    - Wellness Goals: {user_data.get('wellness', 'Not specified')}
    - Personal Development: {user_data.get('personal_life', 'Not specified')}
    - Additional Notes: {user_data.get('notes', 'Not specified')}
    
    Create a comprehensive 21-day plan with:
    1. Week 1 (Days 1-7): Foundation Building
    2. Week 2 (Days 8-14): Momentum Building
    3. Week 3 (Days 15-21): Mastery and Integration
    
    For each week, provide:
    - Daily actionable tasks
    - Progress milestones
    - Reflection questions
    - Potential challenges and solutions
    
    Make it practical, achievable, and motivating.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

@router.post("/21day")
def generate_21day_roadmap_api(request: Planner21Request) -> Dict[str, Any]:
    try:
        user_data = {
            "name": request.name,
            "main_goal": request.main_goal,
            "obstacles": request.obstacles,
            "support": request.support,
            "relationship": request.relationship,
            "wellness": request.wellness,
            "personal_life": request.personal_life,
            "notes": request.notes
        }
        
        roadmap = gemini_21day_roadmap(user_data, {}, "en")
        return {"roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
