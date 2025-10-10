# ============================================================
# IMPORTS
# ============================================================
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utils modules
from utils.weather import get_weather # Make sure to have your OpenWeatherMap API key set in the .env file
from utils.eventbrite import get_events # Make sure to have your Eventbrite API key set in the .env file

# Optional calendar import
calendar_enabled = (
    os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
    and os.path.exists(os.getenv("GOOGLE_CLIENT_SECRETS_FILE")) # Check if the file exists
)
if calendar_enabled:
    from utils.calendar import get_calendar_events


# Import langchain modules
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)


# ============================================================
# USER SETUP & MEMORY (store name/age/preferences)
# ============================================================
import json

USER_FILE = "user_profile.json"

# Load existing user data if available
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

# Ask only for missing info
if "name" not in user_data:
    user_data["name"] = input("Come ti chiami? ").strip()
if "age" not in user_data:
    user_data["age"] = input("Quanti anni hai? ").strip()
if "preferences" not in user_data:
    user_data["preferences"] = input("Quali generi di attività ricerchi solitamente (es. concerti, mostre, sport, ecc.)? ").strip()

# Save automatically
with open(USER_FILE, "w") as f:
    json.dump(user_data, f)

# Assign variables
name = user_data["name"]
age = user_data["age"]
preferences = user_data["preferences"]


# ============================================================
# CICERONE MAIN SCRIPT
# ============================================================
# System Message (CO-STAR + few-shot prompting)
system_message = SystemMessagePromptTemplate.from_template("""
# CONTEXT
Sei Cicerone, un esperto consigliere locale a Milano. Il tuo compito è aiutare l’utente a scoprire attività e eventi in città, in modo naturale, amichevole e contestuale.

# OBSERVATION
In base ai seguenti fattori:
- Gli eventi disponibili: {events}
- Il meteo: {weather}
- Le preferenze generali dell’utente: {preferences}
- L'attività che l'utente sta cercando, incluso il giorno e l'orario per la quale la sta cercando, se specificato: {query}
- L'età dell'utente: {age}
- Eventi personali già in programma nel calendario dell'utente: {calendar}

# SITUATION
L’utente si trova a Milano o nei dintorni e sta cercando suggerimenti su cosa fare, considerando meteo, preferenze personali e disponibilità.

# TASK
Suggerisci e guida l'utente: {name} nella scelta di attività a Milano.  
Se ci sono eventi disponibili e potenzialmente compatibili con i fattori indicati, presentali in modo strutturato con bullet point ed emoji.  
In caso contrario, se è la tua prima risposta che dai all'utente, scrivi immediatamente che non ci sono eventi disponibili, e procedi ad elencare altre attività che potrebbero comunque interessare all'utente, ma evitando cose troppo generiche da turista (esempio Duomo, Castello Sforzesco... ecc.).  
Nei messaggi successivi, aiuta l'utente a trovare l'attività migliore per lui, dando per scontato che se ti chiede un'attività, la sta cercando a Milano.

# ACTION
Scrivi direttamente i consigli:
- In stile WhatsApp tra amici, giovane, amichevole, frasi brevi. Evita frasi troppo formali.
- Con tono naturale, evitando di sembrare un assistente AI, rispondendo in modo conciso e agile come fossi in una chat WhatsApp tra amici dell'età dell'utente: {age}
- Scrivendo in un italiano corretto, naturale e scorrevole, evitando errori grammaticali o di concordanza.
- Usando al massimo 2–3 espressioni leggere (tipo “ape” anziché "aperitivo", “qualcosa di chill” ecc.), MA niente dialetto, niente cringe.
- Senza usare emoji a raffica: max 2–3 per messaggio. Niente liste lunghissime.

# RESULT
Fornisci direttamente la risposta per {name}, con i suggerimenti di attività o eventi più adatti alla situazione e alle preferenze.
""")

# --- FEW-SHOT EXAMPLES (diversi casi, incluso edge case) ---
few_shots = [
    # Case 1: generic
    HumanMessagePromptTemplate.from_template("Non so cosa fare ma ho voglia di uscire"),
    AIMessagePromptTemplate.from_template("Dai dai è pieno di roba da fare! Potresti farti un’ape in Darsena che stasera c'è un evento con musica lì in zona, se no ci starebbe anche passare in Piazza Leo che c'è il Botellon stase. Però dimmi te se vuoi una cosa più chill o no"),

    # Case 2: specific
    HumanMessagePromptTemplate.from_template("Un mercatino vintage, qualchhe posto dove comprare roba"),
    AIMessagePromptTemplate.from_template("Ci sta, di solito in autunno e primavera tipo ce ne sono tanti in generale. Domani ce ne uno che sembra figo che si chiama East Market. Se ti interessa ti do più info :) "),

    # Case 3: edge case (no relevant event)
    HumanMessagePromptTemplate.from_template("Cerco una mostra a Milano oggi."),
    AIMessagePromptTemplate.from_template("😬😬 Oggi non ci sono mostre che io sappia purtroppo. Però puoi sempre andare alla Pinacoteca che è sempre bella! Se no se vuoi ti dico anche altri musei 🤓")
]

# User Message Template
user_message = HumanMessagePromptTemplate.from_template("""
Meteo: {weather}
Eventi: {events}
Calendario: {calendar}
Preferenze: {preferences}
Età: {age}
Richiesta utente: {query}
""")

# Complete Prompt Construction
prompt = ChatPromptTemplate.from_messages(
    [system_message] + few_shots + [user_message]
)



chain = LLMChain(llm=llm, prompt=prompt)


# Get weather and events
weather = get_weather("Milano") 
events = get_events("Milano")


# User query
query = input("Cosa stai cercando in questo momento? Dimmi in cosa posso darti qualche suggerimento! ").strip()


# Calendar (optional)
if calendar_enabled:
    calendar = get_calendar_events(days_ahead=14, max_results=5)
else:
    calendar = "Funzionalità Google Calendar non attiva."


# START CHAT
print("\nChat avviata! Scrivi 'exit' per uscire.\n")
# First output
output = chain.invoke({
    "weather": weather,
    "events": events,
    "calendar": calendar,
    "preferences": preferences,
    "query": query,
    "name": name,
    "age": age
})

print(f"{name}: {query}\n")
print(f"Cicerone:\n{output['text']}")

# Chat loop
while True:
    query = input(f"{name}: ").strip()
    if query.lower() in ["exit", "quit", "esci"]:
        print("Ciao! Alla prossima!")
        break

    result = chain.invoke({
        "weather": weather,
        "events": events,
        "calendar": calendar,
        "preferences": preferences,
        "name": name,
        "age": age,
        "query": query
    })

    print(f"Cicerone:\n{result['text']}\n")