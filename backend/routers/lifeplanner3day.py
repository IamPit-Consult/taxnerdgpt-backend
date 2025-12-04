import os
from dotenv import load_dotenv
import google.generativeai as genai
from localization import translations

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# ------------------------------------------------------------------------------
# Gemini / 3-Day Planner Core Logic
# ------------------------------------------------------------------------------

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
    user_data["Main Goal"] = input(
        "¿Cuál es tu objetivo principal para los próximos tres días? " if language == "es"
        else "What is your main goal for the next three days? "
    )
    user_data["Obstacles"] = input(
        "¿Qué obstáculos podrías enfrentar? " if language == "es"
        else "What obstacles might you face? "
    )
    user_data["Support"] = input(
        "¿Quién o qué puede apoyarte? " if language == "es"
        else "Who or what can support you? "
    )
    user_data["Other Notes"] = input(
        "¿Algo más que quieras compartir? " if language == "es"
        else "Anything else you'd like to share? "
    )
    return user_data


def gemini_3day_roadmap(user_data: Dict[str, Any], t=None, language: str = "en") -> str:
    """
    Core 3-day roadmap generator used by both CLI and API.

    - user_data: dict of user fields (Name, Main Goal, Obstacles, Support, Other Notes, etc.)
    - t: optional translation dict; if None, it will use translations[language]
    - language: "en" or "es"
    """
    if t is None:
        t = translations.get(language, translations["en"])

    prompt = (
        ("Eres un asistente de planificación de vida. "
         "Con el siguiente perfil de usuario, genera una hoja de ruta detallada y accionable para los próximos tres días. "
         "Desglosa el objetivo principal en pasos diarios, incluye consejos para superar obstáculos y sugiere cómo usar el apoyo disponible. "
         "Sé específico y motivador.\n\n"
         "Perfil del usuario:\n")
        if language == "es"
        else
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

    model = genai.GenerativeModel("models/gemini-2.5-flash-preview-05-20")
    response = model.generate_content(prompt)

    # Format the roadmap for better readability
    formatted_roadmap = format_roadmap(response.text.strip())
    return formatted_roadmap


def format_roadmap(roadmap_text: str) -> str:
    """
    Take a raw roadmap text and format it into sections with bullets.
    """
    sections = roadmap_text.split("---")
    formatted_sections = []

    for section in sections:
        lines = section.strip().split("\n")
        if lines:
            heading = lines[0].strip()
            content = "\n".join(f"• {line.strip()}" for line in lines[1:] if line.strip())
            formatted_sections.append(f"{heading}\n{content}")

    return "\n".join(formatted_sections)


def main():
    # CLI usage if you run this file directly
    print("Select your language / Seleccione su idioma:")
    print("1. English")
    print("2. Español")
    lang_choice = input("Enter your choice (1-2): ").strip()
    language = "es" if lang_choice == "2" else "en"
    t = translations[language]

    user_data = get_user_input(t, language)
    roadmap = gemini_3day_roadmap(user_data, t, language)
    formatted_roadmap = format_roadmap(roadmap)
    print("\n" + (t.get("planner_3day_title", "Your 3-Day Personalized Roadmap:")) + "\n")
    print(formatted_roadmap)

    # Optionally offer to save as PDF
    create_pdf = input(t["save_pdf_prompt"]).strip().lower()
    if create_pdf in [t["yes"], "si", "sí", "yes"]:
        from fpdf import FPDF

        def save_roadmap_to_pdf(roadmap_text, filename="3day_roadmap.pdf"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in roadmap_text.split("\n"):
                pdf.multi_cell(0, 10, line)
            pdf.output(filename)
            print(t["pdf_saved"].format(filename=filename))

        save_roadmap_to_pdf(formatted_roadmap)


if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------
# FastAPI Router Section (used by your backend on Render)
# ------------------------------------------------------------------------------

router = APIRouter()


@router.post("/planner/3day")
async def generate_3day_plan(user_data: Dict[str, Any]):
    """
    FastAPI endpoint used by the React frontend.

    Expects a JSON object from the chat (whatever fields you collected).
    Returns: { "roadmap": "<formatted roadmap text>" }
    """
    try:
        # Call the same core function used by CLI
        roadmap_text = gemini_3day_roadmap(user_data)
        return {"roadmap": roadmap_text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating 3-day roadmap: {e}",
        )
