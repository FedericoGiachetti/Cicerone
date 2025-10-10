# ============================================================
# IMPORTS
# ============================================================
from core import (
    get_user_data,
    setup_llm_chain,
    get_context_data,
)

# ============================================================
# MAIN PROGRAM
# ============================================================

# Load or Create User Profile
name, age, preferences = get_user_data()

# Initialize LLM and Memory Chain
chain_with_memory = setup_llm_chain()

# Get Context (weather, events, calendar)
weather, events, calendar = get_context_data()

# Starting Input
query = input("Cosa stai cercando in questo momento? Dimmi in cosa posso darti qualche suggerimento! ").strip()

# ============================================================
# START CHAT
# ============================================================
print("\nChat avviata! Scrivi 'exit' per uscire.\n")

output = chain_with_memory.invoke(
    {
        "input": query,
        "weather": weather,
        "events": events,
        "calendar": calendar,
        "preferences": preferences,
        "name": name,
        "age": age,
        "query": query
    },
    config={"configurable": {"session_id": "default"}}
)

print(f"{name}: {query}\n")
print(f"Cicerone:\n{output['text']}\n")

# Chat loop
while True:
    query = input(f"{name}: ").strip()
    if query.lower() == "reset":
        import os
        from core import USER_FILE
        if os.path.exists(USER_FILE):
            os.remove(USER_FILE)
            print("✅ Profile reset. Restart the program to enter new info.")
        else:
            print("No profile file found.")
        break
    if query.lower() in ["exit", "quit", "esci"]:
        print("Ciao! Alla prossima!")
        break

    result = chain_with_memory.invoke(
        {
            "input": query,
            "weather": weather,
            "events": events,
            "calendar": calendar,
            "preferences": preferences,
            "name": name,
            "age": age,
            "query": query
        },
        config={"configurable": {"session_id": "default"}}
    )
    print(f"Cicerone:\n{result['text']}\n")
