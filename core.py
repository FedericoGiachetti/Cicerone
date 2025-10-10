# ============================================================
# CORE MODULE
# ============================================================
import os
import json
from dotenv import load_dotenv

# Utils
from utils.weather import get_weather
from utils.eventbrite import get_events

# Load env
load_dotenv()

# ============================================================
# USER PROFILE MANAGEMENT
# ============================================================
USER_FILE = "user_profile.json"

def get_user_data():
    """Loads or asks user information, and saves them in JSON."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            user_data = json.load(f)
    else:
        user_data = {}

    if "name" not in user_data:
        user_data["name"] = input("Come ti chiami? ").strip()
    if "age" not in user_data:
        user_data["age"] = input("Quanti anni hai? ").strip()
    if "preferences" not in user_data:
        user_data["preferences"] = input(
            "Quali generi di attività ricerchi solitamente (es. concerti, mostre, sport, ecc.)? "
        ).strip()

    with open(USER_FILE, "w") as f:
        json.dump(user_data, f)

    return user_data["name"], user_data["age"], user_data["preferences"]

# ============================================================
# LLM SETUP
# ============================================================
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder


def setup_llm_chain():
    """Initializes the LLM, prompt and memory."""
    # Controllo calendario
    calendar_enabled = (
        os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
        and os.path.exists(os.getenv("GOOGLE_CLIENT_SECRETS_FILE"))
    )
    if calendar_enabled:
        from utils.calendar import get_calendar_events
    else:
        get_calendar_events = None

    # Prompt di sistema
    system_message = SystemMessagePromptTemplate.from_template("""
# CONTEXT
Sei Cicerone, un esperto consigliere locale a Milano. Il tuo compito è aiutare l’utente a scoprire attività e eventi in città, in modo naturale, amichevole e contestuale.

# OBSERVATION
In base ai seguenti fattori:
- Gli eventi disponibili: {events}
- Le preferenze generali dell’utente: {preferences}
- L'attività che l'utente sta cercando, incluso il giorno e l'orario per la quale la sta cercando, se specificato: {query}
- L'età dell'utente: {age}
- Eventi personali già in programma nel calendario dell'utente: {calendar}
- Il meteo: {weather}

# SITUATION
L’utente si trova a Milano o nei dintorni e sta cercando suggerimenti su cosa fare, considerando meteo, preferenze personali e disponibilità.

# TASK
Suggerisci e guida l'utente: {name} nella scelta di attività a Milano.  
Dai priorità afli eventi disponibili e potenzialmente compatibili con i fattori indicati. 
In caso non ci fossero eventi disponibili, evita di ripetere continuamente "Che peccato, oggi non ci sono eventi culinari in programma" o simili, smeplicemente, proponi altre attività che potrebbero comunque interessare all'utente, ma evitando cose troppo generiche da turista (esempio Duomo, Castello Sforzesco... ecc.).  
In ogni messaggio, aiuta l'utente a trovare l'attività migliore per lui, dando per scontato che se ti chiede un'attività, la sta cercando a Milano. Itera sulle tue proposte chiedendo all'utente se gli interessa sapere di più di quello che proponi, o se preferisce altro, in base alle sue risposte.
 

# ACTION
Scrivi direttamente i consigli:
- In stile WhatsApp tra amici, giovane, amichevole, frasi brevi. Evita frasi troppo formali. Prosegui la chat in base ai messaggi precedenti conitnuando la conversazione in modo scorrevole.
- Con tono naturale, evitando frasi ed espressioni da assistente AI, rispondendo in modo conciso e agile come fossi in una chat WhatsApp tra amici dell'età dell'utente: {age}
- Scrivendo in un italiano corretto, naturale e scorrevole, evitando errori grammaticali o di concordanza.
- Usando al massimo 2–3 espressioni leggere (tipo “ape” anziché "aperitivo", “qualcosa di chill” ecc.), MA niente dialetto, niente cringe.
- Senza usare emoji a raffica: max 2–3 per messaggio. Niente liste lunghissime.

# RESULT
Fornisci direttamente la risposta per {name}, con i suggerimenti di attività o eventi più adatti alla situazione e alle preferenze.
""")

    # Few-shot examples
    few_shots = [
        HumanMessagePromptTemplate.from_template("Non so cosa fare ma ho voglia di uscire"),
        AIMessagePromptTemplate.from_template("Dai dai è pieno di roba da fare! Potresti farti un’ape in Darsena che stasera c'è un evento con musica lì in zona, se no ci starebbe anche passare in Piazza Leo che c'è il Botellon stase. Però dimmi te se vuoi una cosa più chill o no"),
        HumanMessagePromptTemplate.from_template("Un mercatino vintage, qualchhe posto dove comprare roba"),
        AIMessagePromptTemplate.from_template("Ci sta, di solito in autunno e primavera tipo ce ne sono tanti in generale. Domani ce ne uno che sembra figo che si chiama East Market. Se ti interessa ti do più info :) "),
        HumanMessagePromptTemplate.from_template("Cerco una mostra a Milano oggi."),
        AIMessagePromptTemplate.from_template("Oggi non ci sono mostre che io sappia purtroppo. Però puoi sempre andare alla Pinacoteca che è sempre bella! Se no se vuoi ti dico anche altri musei.")
    ]

    # User message
    user_message = HumanMessagePromptTemplate.from_template("""
Meteo: {weather}
Eventi: {events}
Calendario: {calendar}
Preferenze: {preferences}
Età: {age}
Richiesta utente: {query}
""")

    # Prompt completo
    prompt = ChatPromptTemplate.from_messages(
        [system_message] + few_shots + [MessagesPlaceholder("chat_history"), user_message]
    )

    # LLM e catena
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.8,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    # Memoria
    history = ChatMessageHistory()
    def get_session_history(session_id: str):
        return history

    chain_with_memory = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    return chain_with_memory


# ============================================================
# CONTEXT DATA (Weather, Events, Calendar)
# ============================================================
def get_context_data():
    """Loads context data: weather, events, calendar (if active)."""
    weather = get_weather("Milano")
    events = get_events("Milano")

    calendar_enabled = (
        os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
        and os.path.exists(os.getenv("GOOGLE_CLIENT_SECRETS_FILE"))
    )
    if calendar_enabled:
        from utils.calendar import get_calendar_events
        calendar = get_calendar_events(days_ahead=14, max_results=5)
    else:
        calendar = "Funzionalità Google Calendar non attiva."

    return weather, events, calendar
