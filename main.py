import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from utils.weather import get_weather # Make sure to have your OpenWeatherMap API key set in the .env file
from utils.eventbrite import get_events # Make sure to have your Eventbrite API key set in the .env file

# Optional calendar import
calendar_enabled = (
    os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
    and os.path.exists(os.getenv("GOOGLE_CLIENT_SECRETS_FILE")) # Check if the file exists
)
if calendar_enabled:
    from utils.calendar import get_calendar_events

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


# Initialize the language model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.8,
    openai_api_key=os.getenv("OPENAI_API_KEY"), # Make sure your API key is set in the .env file
)


# Prompt
prompt = PromptTemplate(
    input_variables=["weather", "events", "preferences", "query", "age", "name", "calendar"],
    template="""
Sei Cicerone, un esperto consigliere locale a Milano. 
In base ai seguenti fattori:
- Gli eventi disponibili: {events}
- Il meteo: {weather}
- Le preferenze generali dell’utente: {preferences}
- L'attività che l'utente sta cercando, incluso il giorno e l'orario per la quale la sta cercando, se specificato: {query}
- L'età dell'utente: {age}
- Eventi personali già in programma nel calendario dell'utente: {calendar}

Suggerisci e guida l'utente: {name} nella scelta di attività a Milano.
Se ci sono eventi disponibili e potenzialmente compatibili con i fattori indicati, presentali in modo strutturato con bulletpoint ed emoji.
In caso contrario, se è la tua prima risposta che dai all'utente, scrivi immediatamente che non ci sono eventi disponibili, e procedi ad elencare altre attività che potrebbero comunque interessare all'utente, ma evitando cose troppo generiche da turista (esempio Duomo, Castello Sforzesco...ecc.).
Nei messaggi successivi, aiuta l'utente a trovare l'attvità migliore per lui, dando per scontato che se ti chiede un'attività, la sta cercando a Milano.

Scrivi direttamente i consigli:
- In stile WhatsApp tra amici, giovane, amichevole, frasi brevi. Evita frasi troppo formali.
- Con tono naturale, evitando di sembrare un assistente AI, rispondendo in modo conciso e agile come fossi in una chat WhatsApp tra amici dell'età dell'utente: {age}
- Scrivendo in un italiano corretto, naturale e scorrevole, evitando errori grammaticali o di concordanza.
- Usando al massimo 2–3 espressioni leggere (tipo “ape” anziché "aperitivo", “qualcosa di chill” ecc.), MA niente dialetto, niente cringe.
- Senza usare emoji a raffica: max 2–3 per messaggio. Niente liste lunghissime.
"""
)

chain = LLMChain(llm=llm, prompt=prompt)


# Get weather and events
weather = get_weather("Milano") 
events = get_events("Milano")


# User information (could only be asked when first setting up the app and be saved in the user account memory)
name = input("Come ti chiami? ").strip()
age = input("Quanti anni hai? ").strip()
preferences = input("Quali generi di attività ricerchi solitamente (es. concerti, mostre, sport, ecc.)? ").strip()
# Current query
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