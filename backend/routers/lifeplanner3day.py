import os
from dotenv import load_dotenv
import google.generativeai as genai
from localization import translations


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

def get_user_input(t, language="en"):
    print(t["planner_3day_title"])
    user_data = {}
    user_data["Name"] = input("¿Cuál es tu nombre? " if language == "es" else "What is your name? ")
    user_data["Main Goal"] = input("¿Cuál es tu objetivo principal para los próximos tres días? " if language == "es" else "What is your main goal for the next three days? ")
    user_data["Obstacles"] = input("¿Qué obstáculos podrías enfrentar? " if language == "es" else "What obstacles might you face? ")
    user_data["Support"] = input("¿Quién o qué puede apoyarte? " if language == "es" else "Who or what can support you? ")
    user_data["Other Notes"] = input("¿Algo más que quieras compartir? " if language == "es" else "Anything else you'd like to share? ")
    return user_data

def gemini_3day_roadmap(user_data, t, language="en"):
    prompt = (
        ("Eres un asistente de planificación de vida. "
         "Con el siguiente perfil de usuario, genera una hoja de ruta detallada y accionable para los próximos tres días. "
         "Desglosa el objetivo principal en pasos diarios, incluye consejos para superar obstáculos y sugiere cómo usar el apoyo disponible. "
         "Sé específico y motivador.\n\n"
         "Perfil del usuario:\n") if language == "es" else
        "You are a life planning assistant. "
        "Given the following user profile, generate a detailed, actionable roadmap for the next three days. "
        "Break down the main goal into daily steps, include tips for overcoming obstacles, and suggest how to use available support. "
        "Be specific and motivational.\n\n"
        "User Profile:\n"
    )
    for k, v in user_data.items():
        prompt += f"- {k}: {v}\n"
    prompt += (
        "\nPresenta la hoja de ruta como Día 1, Día 2 y Día 3, con viñetas para las acciones de cada día."
        if language == "es"
        else "\nPlease present the roadmap as Day 1, Day 2, and Day 3, with bullet points for each day's actions. "
             "Use clear headings for each day and ensure the content is concise and easy to read. "
             "Format the roadmap like a professional report, with sections for 'Goal', 'Action Steps', 'Tips for Obstacles', and 'Using Support'."
    )
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)

        # Format the roadmap for better readability
    formatted_roadmap = format_roadmap(response.text.strip())
    return formatted_roadmap

def format_roadmap(roadmap_text):
    # Split the roadmap into sections by days
    sections = roadmap_text.split("---")
    formatted_sections = []

    for section in sections:
        lines = section.strip().split("\n")
        if lines:
            # Add a heading for each section
            heading = lines[0].strip()
            content = "\n".join(f"• {line.strip()}" for line in lines[1:])
            formatted_sections.append(f"{heading}\n{content}")

    # Join the formatted sections with a separator
    return "\n".join(formatted_sections)

def main():
    # Language selection (if running standalone)
    print("Select your language / Seleccione su idioma:")
    print("1. English")
    print("2. Español")
    lang_choice = input("Enter your choice (1-2): ").strip()
    language = "es" if lang_choice == "2" else "en"
    t = translations[language]

    user_data = get_user_input(t, language)
    roadmap = gemini_3day_roadmap(user_data, t, language)
    formatted_roadmap = format_roadmap(roadmap)
    print("\n" + (t["planner_3day_title"] if "planner_3day_title" in t else "Your 3-Day Personalized Roadmap:") + "\n")
    print(formatted_roadmap)

    # Optionally offer to save as PDF
    create_pdf = input(t["save_pdf_prompt"]).strip().lower()
    if create_pdf in [t["yes"], "si", "sí", "yes"]:
        from fpdf import FPDF
        def save_roadmap_to_pdf(roadmap_text, filename="3day_roadmap.pdf"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in roadmap_text.split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf.output(filename)
            print(t["pdf_saved"].format(filename=filename))
        save_roadmap_to_pdf(formatted_roadmap)

if __name__ == "__main__":
    main()

# FastAPI router section
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Import your 3-day roadmap generator from the services layer.
# Make sure this import matches your actual services/gemini.py function.
from services.gemini import gemini_3day_roadmap

router = APIRouter()


@router.post("/planner/3day")
async def generate_3day_plan(user_data: Dict[str, Any]):
    """
    Generate a 3-day roadmap.

    Accepts a flexible JSON payload from the frontend and passes it to Gemini.
    Whatever the chat collected (name, main_goal, obstacles, etc.)
    will be in user_data.
    """
    try:
        roadmap_text = gemini_3day_roadmap(user_data)
        return {"roadmap": roadmap_text}
    except Exception as e:
        # Expose a clear error in the HTTP response instead of a silent 500
        raise HTTPException(
            status_code=500,
            detail=f"Error generating 3-day roadmap: {e}",
        )


@router.post("/3day")
def generate_3day_roadmap_api(request: Planner3Request) -> Dict[str, Any]:
    try:
        user_data = {
            "Name": request.name,
            "Main Goal": request.main_goal,
            "Obstacles": request.obstacles,
            "Support": request.support,
            "Other Notes": request.notes
        }
        t = translations.get(request.language, translations["en"])
        roadmap = gemini_3day_roadmap(user_data, t, request.language)
        formatted_roadmap = format_roadmap(roadmap)
        return {"roadmap": formatted_roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sample roadmap text for testing
sample_roadmap = """
Day 1: The Launchpad - Small Steps, Big Impact
  • Goal for Today: Create a positive, low-pressure start to reading and experience an initial success.
  • Define Your "Better Reader" (5 minutes): Quickly jot down what "a better reader" means to you.
  • Choose Your Weapon Wisely (10 minutes): Select a book or article that excites you.
  • Create Your Sanctuary (15 minutes): Find a quiet spot for reading.

Day 2: Building Momentum & Sharpening Focus
  • Goal for Today: Lengthen your reading time slightly and actively engage your focus.
  • Review and Recommit (5 minutes): Reflect on yesterday's success.
  • Your Scheduled Slot (10 minutes): Identify a specific 30-minute block for reading.

Day 3: Solidifying the Habit & Forward Planning
  • Goal for Today: Consolidate your new habit, reflect on your progress, and create a sustainable plan.
  • Morning Motivation (5 minutes): Recall your successes from Day 1 and 2.
  • Your Longest Session Yet (30-45 minutes): Commit to a longer reading session.
"""

# Uncomment the following lines to test the sample roadmap generation
# user_data = {
#     "Name": "Test User",
#     "Main Goal": "Improve reading habits",
#     "Obstacles": "Lack of time, distractions",
#     "Support": "Reading group, online resources",
#     "Other Notes": "Prefer fiction over non-fiction"
# }
# t = translations["en"]
# roadmap = gemini_3day_roadmap(user_data, t, "en")
# formatted_roadmap = format_roadmap(roadmap)
# print(formatted_roadmap)
