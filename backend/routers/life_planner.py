from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from services.gemini import gemini_full_life_roadmap

router = APIRouter()

class PlannerRequest(BaseModel):
    name: str
    age: int
    career: str
    desired_location: str
    house_goal_age: int
    retirement_age: int
    savings_goal: float
    goals: str
    challenges: str
    support: str

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

CATEGORIES = {
    "Education/Career Path": {},
    "Tax Planning": {},
    "Business Development": {},
    "Money Management": {},
    "Investment": {},
    "Individual Life Goals": {},
    "Health and Wellness": {},
    "Homeownership": {},
    "Asset and Property Acquisition": {},
    "Family Planning": {},
    "Philanthropy & Missionary": {},
    "Retirement Path": {}
}

LIFE_PLANNER_QUESTIONS = [
    ("Current Age", "What is your current age?"),
    ("Desired Location", "What is your desired location?"),
    ("Career", "What is your career or dream job?"),
    ("House Goal", "How many years until you want to buy a house?"),
    ("Retirement Age", "At what age do you want to retire?"),
    ("Savings Goal", "What is your savings goal?"),
    ("Education/Career Path Insight", "What are your thoughts or plans about your education/career path?"),
    ("Education/Career Path Foresight", "What is your long-term vision for your education/career?"),
    ("Tax Planning Insight", "How do you currently handle taxes? Any long-term tax planning goals?"),
    ("Tax Planning Foresight", "What is your ideal tax situation in the future?"),
    ("Business Development Insight", "Are you interested in starting or growing a business?"),
    ("Business Development Foresight", "What is your dream business outcome?"),
    ("Money Management Insight", "How do you manage your money? Any financial habits or goals?"),
    ("Money Management Foresight", "What is your ideal money management scenario?"),
    ("Investment Insight", "Are you investing? What are your investment interests and goals?"),
    ("Investment Foresight", "What is your investment vision for the future?"),
    ("Individual Life Goals Insight", "What are your most important personal life goals?"),
    ("Individual Life Goals Foresight", "How do you see yourself achieving your personal goals?"),
    ("Health and Wellness Insight", "How do you approach your health and wellness? Any goals or routines?"),
    ("Health and Wellness Foresight", "What is your ideal health and wellness state?"),
    ("Homeownership Insight", "What are your thoughts or plans about owning a home?"),
    ("Homeownership Foresight", "What is your long-term homeownership vision?"),
    ("Asset and Property Acquisition Insight", "Are you interested in acquiring assets or property? What kind?"),
    ("Asset and Property Acquisition Foresight", "What is your asset/property acquisition goal?"),
    ("Family Planning Insight", "What are your plans or hopes for your family?"),
    ("Family Planning Foresight", "What is your ideal family scenario?"),
    ("Philanthropy & Missionary Insight", "Are you interested in philanthropy or giving back? Any causes you care about?"),
    ("Philanthropy & Missionary Foresight", "What is your long-term vision for giving back?"),
    ("Retirement Path Insight", "What does your ideal retirement look like? Any dreams or plans?"),
    ("Retirement Path Foresight", "What is your retirement vision?"),
]

def google_custom_search(query, api_key=None, cse_id=None, num_results=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key or GOOGLE_API_KEY,
        "cx": cse_id or GOOGLE_CSE_ID,
        "num": num_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link")
        })
    combined_snippets = " ".join([r["snippet"] for r in results])
    if combined_snippets:
        summary = gemini_summarize(combined_snippets)
    else:
        summary = "No insights available to summarize."
    return {"results": results, "summary": summary}

def scrape_web(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for g in soup.find_all("div", class_="BNeawe vvjwJb AP7Wnd"):
            title = g.get_text()
            parent = g.find_parent("a")
            link = parent["href"] if parent else None
            snippet = g.find_next_sibling("div", class_="BNeawe s3v9rd AP7Wnd").get_text() if g.find_next_sibling("div", class_="BNeawe s3v9rd AP7Wnd") else None
            if title and snippet:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": f"https://www.google.com{link}" if link else "No link available"
                })
                if len(results) >= 3:
                    break
        combined_snippets = " ".join([result["snippet"] for result in results])
        if combined_snippets:
            summarized_text = gemini_summarize(combined_snippets)
        else:
            summarized_text = "No insights available to summarize."
        return {
            "results": results,
            "summary": summarized_text
        }
    except requests.exceptions.RequestException as e:
        print(f"Error during web scraping: {e}")
        return {
            "results": [{"title": "Error", "snippet": "No insights available from web scraping.", "link": ""}],
            "summary": "No insights available to summarize."
        }

def get_user_input(t, language="en"):
    print(t["welcome"])
    user_data = {}

    # Step 1: Basic Info
    while True:
        user_input = input(t["options"] + " " + t["enter_age"])
        entities = extract_entities(user_input)
        if "AGE" in entities:
            user_data["Current Age"] = int(entities["AGE"])
        if "GPE" in entities:
            user_data["Desired Location"] = entities["GPE"]
        if "ORG" in entities or "WORK_OF_ART" in entities or "PERSON" in entities:
            user_data["Career"] = entities.get("ORG") or entities.get("WORK_OF_ART") or entities.get("PERSON")
        if "Current Age" not in user_data:
            try:
                user_data["Current Age"] = int(input(t["enter_age"]))
            except ValueError:
                continue
        if "Career" not in user_data:
            user_data["Career"] = input(t["enter_career"])
        if "Desired Location" not in user_data:
            user_data["Desired Location"] = input(t["desired_location"])
        break

    user_data["House Goal"] = int(input(t["enter_house_goal"]))
    user_data["Retirement Age"] = int(input(t["enter_retirement_age"]))
    user_data["Savings Goal"] = float(input(t["enter_savings_goal"]))

    print("\n" + t["options"])

    # Step 3: NLP-style open-ended questions for each category
    categories = [
        ("Education/Career Path", t["enter_career"]),
        ("Tax Planning", "¿Cómo maneja actualmente los impuestos? ¿Alguna meta de planificación fiscal a largo plazo?" if language == "es" else "How do you currently handle taxes? Any long-term tax planning goals?"),
        ("Business Development", "¿Está interesado en iniciar o hacer crecer un negocio? ¿Cuáles son sus sueños empresariales?" if language == "es" else "Are you interested in starting or growing a business? What are your business dreams?"),
        ("Money Management", "¿Cómo administra su dinero? ¿Algún hábito o meta financiera?" if language == "es" else "How do you manage your money? Any financial habits or goals?"),
        ("Investment", "¿Está invirtiendo? ¿Cuáles son sus intereses y metas de inversión?" if language == "es" else "Are you investing? What are your investment interests and goals?"),
        ("Individual Life Goals", "¿Cuáles son sus metas personales más importantes?" if language == "es" else "What are your most important personal life goals?"),
        ("Health and Wellness", "¿Cómo aborda su salud y bienestar? ¿Alguna meta o rutina?" if language == "es" else "How do you approach your health and wellness? Any goals or routines?"),
        ("Homeownership", "¿Qué piensa o planea sobre ser propietario de una vivienda?" if language == "es" else "What are your thoughts or plans about owning a home?"),
        ("Asset and Property Acquisition", "¿Está interesado en adquirir activos o propiedades? ¿Qué tipo?" if language == "es" else "Are you interested in acquiring assets or property? What kind?"),
        ("Family Planning", "¿Cuáles son sus planes o esperanzas para su familia?" if language == "es" else "What are your plans or hopes for your family?"),
        ("Philanthropy & Missionary", "¿Está interesado en la filantropía o en retribuir? ¿Alguna causa que le importe?" if language == "es" else "Are you interested in philanthropy or giving back? Any causes you care about?"),
        ("Retirement Path", "¿Cómo sería su jubilación ideal? ¿Algún sueño o plan?" if language == "es" else "What does your ideal retirement look like? Any dreams or plans?")
    ]
    for cat, prompt in categories:
        insight = input(f"{prompt}\n{t['insights_title'].format(category=cat)} ")
        foresight = input(f"{t['summary_title'].format(category=cat)} ")
        user_data[f"{cat} Insight"] = insight
        user_data[f"{cat} Foresight"] = foresight

    # Step 4: Fetch and summarize location insights
    location_query = f"{'Costo de vida en' if language == 'es' else 'Cost of living in'} {user_data['Desired Location']}"
    location_data = scrape_web(location_query)
    print(f"\n{t['summary_title'].format(category='Ubicación' if language == 'es' else 'Location')}")
    print(location_data["summary"])
    user_data["Location Summary"] = location_data["summary"]

    # Step 5: Confirm and summarize
    print("\n¡Gracias! Aquí tienes un resumen de lo que has compartido:" if language == "es" else "\nThanks! Here's a summary of what you've shared:")
    for k, v in user_data.items():
        print(f"- {k}: {v}")

    confirm = input("\n¿Es correcta esta información? (sí/no): " if language == "es" else "\nIs this information correct? (yes/no): ").strip().lower()
    if confirm not in [t["yes"], "si", "sí", "yes"]:
        print("Vamos a empezar de nuevo." if language == "es" else "Let's start over.")
        return get_user_input(t, language)

    return user_data

def get_category_insights(user_data, api_key=None, cse_id=None):
    insights = {}
    user_career = user_data.get("Career", "")
    user_location = user_data.get("Desired Location", "")
    user_age = user_data.get("Current Age", "")

    for cat in CATEGORIES.keys():
        insight_base = user_data.get(f"{cat} Insight", "").strip() or cat
        foresight_base = user_data.get(f"{cat} Foresight", "").strip() or cat

        insight_query = f"{insight_base} for {user_career} in {user_location} at age {user_age}"
        foresight_query = f"{foresight_base} for {user_career} in {user_location} at age {user_age}"

        insight_data = google_custom_search(insight_query, api_key, cse_id)
        foresight_data = google_custom_search(foresight_query, api_key, cse_id)

        insight_reply = conversational_life_plan_reply(user_data, insight_data["summary"], cat + " (Insight)")
        foresight_reply = conversational_life_plan_reply(user_data, foresight_data["summary"], cat + " (Foresight)")

        insights[cat] = {
            "insight": insight_reply,
            "foresight": foresight_reply
        }
    return insights

def conversational_life_plan_reply(user_data, web_summary, topic):
    user_facts = []
    for k, v in user_data.items():
        if isinstance(v, str) and v.strip() and k.lower() not in ["location summary"]:
            user_facts.append(f"{k}: {v}")
    combined = (
        f"Based on what you've shared about your {topic}, here's a personalized summary:\n"
        + "\n".join(user_facts)
        + f"\n\nHere's what I found from my research: {web_summary}"
    )
    import re
    combined = re.sub(r'http\S+', '', combined)
    summary = gemini_summarize(combined)
    return f"Here's my advice for you: {summary}"

def gemini_summarize(prompt):
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)
    return response.text.strip()

def gemini_generate_roadmap(user_data, category_insights):
    prompt = (
        "You are a life planning assistant. "
        "Given the following user profile and research insights, generate a step-by-step roadmap for the user's success. "
        "The roadmap should be actionable, personalized, and cover all major life categories. "
        "Include milestones, recommended actions, and tips for each phase of life.\n\n"
        "User Profile:\n"
    )
    for k, v in user_data.items():
        prompt += f"- {k}: {v}\n"
    prompt += "\nWeb Insights by Category:\n"
    for cat, insight in category_insights.items():
        prompt += f"{cat} Insight: {insight['insight']}\n"
        prompt += f"{cat} Foresight: {insight['foresight']}\n"
    prompt += (
        "\nPlease present the roadmap in a clear, year-by-year or phase-by-phase format, "
        "with bullet points for each recommended action."
    )

    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-05-20')
    response = model.generate_content(prompt)
    return response.text.strip()

# Add this function to match what main.py expects:
def generate_life_roadmap(user_data, category_insights):
    """Wrapper function to match the expected name in main.py"""
    return gemini_generate_roadmap(user_data, category_insights)

@router.post("/generate")
def generate_full_roadmap(request: PlannerRequest) -> Dict[str, Any]:
    try:
        user_data = request.dict()
        insights = get_category_insights(user_data, GOOGLE_API_KEY, GOOGLE_CSE_ID)
        # Use the consistent function name
        roadmap = generate_life_roadmap(user_data, insights)
        return {"roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
