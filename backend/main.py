from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables FIRST, before importing other modules
load_dotenv()

from routers.life_planner import router as full_planner_router
from routers.lifeplanner21day import router as planner21day_router  # Make sure this import works
from routers.lifeplanner3day import router as planner3day_router
from routers import pdf
from routers import history_router 
from routers.reminders_router import router as reminders_router

from routers.email_roadmap_router import email_roadmap
from localization import translations
from tax_analysis import get_tax_analysis, display_tax_analysis
from routers.life_planner import get_user_input, get_category_insights, gemini_generate_roadmap
from routers.lifeplanner21day import get_user_input as get_21day_input, gemini_21day_roadmap
from routers.lifeplanner3day import get_user_input as get_3day_input, gemini_3day_roadmap
from fpdf import FPDF

# -------------------- FastAPI Setup -------------------- #
app = FastAPI(
    title="Perpetual Life Planner API",
    version="1.0.0",
    description="Supports Full, 21-Day, and 3-Day roadmap planners"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(full_planner_router, prefix="/planner")
app.include_router(planner21day_router, prefix="/planner")  # This should add /planner/21day
app.include_router(planner3day_router, prefix="/planner")
app.include_router(history_router.router, prefix="/history")
app.include_router(reminders_router)
app.include_router(pdf.router)

@app.get("/")
def root():
    return {"message": "Perpetual Life Planner API is running!"}

# -------------------- CLI Helper Logic (Optional) -------------------- #
def clean_text(text):
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    return text

def save_roadmap_to_pdf(roadmap_text, filename="roadmap.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in roadmap_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    print(f"PDF saved as {filename}")

# -------------------- CLI Launch -------------------- #
def main():
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

    print("Select your language / Seleccione su idioma:")
    print("1. English")
    print("2. Español")
    lang_choice = input("Enter your choice (1-2): ").strip()
    language = "es" if lang_choice == "2" else "en"
    t = translations[language]

    print("\n" + t["access_prompt"])
    print("1. " + t["access_full"])
    print("2. " + t["access_21day"])
    print("3. " + t["access_3day"])
    print(t["enter_numbers"])
    access_input = input().strip()
    access_map = {"1": "full", "2": "21day", "3": "3day"}
    user_access = [access_map[x.strip()] for x in access_input.split(",") if x.strip() in access_map]

    print("\n" + t["access_you_have"])
    if "full" in user_access: print("- " + t["access_full"])
    if "21day" in user_access: print("- " + t["access_21day"])
    if "3day" in user_access: print("- " + t["access_3day"])

    print(t["welcome"])
    print(t["options"])
    for option in t["menu_options"]: print(option)

    while True:
        choice = input("\n> ").strip()
        if choice == "1":
            print(t["tax_analysis_start"])
            customer_data = get_tax_analysis({})
            display_tax_analysis(customer_data)
            recipient_email = input("\n" + t["tax_analysis_email"]).strip()
            if recipient_email:
                send_email_with_pdf(customer_data, recipient_email)
                print(t["tax_analysis_sent"])

        elif choice == "2" and "full" in user_access:
            print(t["roadmap_title"])
            user_data = get_user_input(t, language)
            category_insights = get_category_insights(user_data, GOOGLE_API_KEY, GOOGLE_CSE_ID)
            for cat, replies in category_insights.items():
                print(f"\n{t['insights_title'].format(category=cat)}\n{replies['insight']}")
                print(f"{t['summary_title'].format(category=cat)}\n{replies['foresight']}")
            roadmap_text = gemini_generate_roadmap(user_data, category_insights)
            print("\n" + t["roadmap_title"])
            print(roadmap_text)
            if input(t["save_pdf_prompt"]).strip().lower() in [t["yes"], "si", "sí"]:
                save_roadmap_to_pdf(roadmap_text, "full_life_planner_roadmap.pdf")

        elif choice == "2" and "21day" in user_access:
            print(t["planner_21day_title"])
            user_data = get_21day_input(t, language)
            roadmap = gemini_21day_roadmap(user_data, t, language)
            print("\n" + t["planner_21day_title"] + "\n")
            print(roadmap)
            if input(t["save_pdf_prompt"]).strip().lower() in [t["yes"], "si", "sí"]:
                save_roadmap_to_pdf(roadmap, "21day_roadmap.pdf")

        elif choice == "2" and "3day" in user_access:
            print(t["planner_3day_title"])
            user_data = get_3day_input(t, language)
            roadmap = gemini_3day_roadmap(user_data, t, language)
            print("\n" + t["planner_3day_title"] + "\n")
            print(roadmap)
            if input(t["save_pdf_prompt"]).strip().lower() in [t["yes"], "si", "sí"]:
                save_roadmap_to_pdf(roadmap, "3day_roadmap.pdf")

        elif choice == "3":
            print(t["scripture_message"])
            display_random_scripture()

        elif choice == "4":
            print(t["exit_message"])
            break

        else:
            print(t["invalid_choice"])
            print(t["help_message"])
            for help_option in t["help_options"]: print(help_option)

if __name__ == "__main__":
    import sys
    if "runserver" in sys.argv:
        # Command: python main.py runserver
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    else:
        main()
