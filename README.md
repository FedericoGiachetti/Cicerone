# 🌆 CICERONE 

> **TL;DR**  
> Cicerone is an MVP of a chat-based local assistant for Milan.  
> It suggests activities by combining events, weather, and calendar data, and answers in a natural, WhatsApp-like Italian tone.  
> Built as a proof of concept to explore how AI can make local recommendations more personal and conversational.

---

## 📌 Project Status

This is a working **MVP / proof of concept**:  
- Core loop functional (chat with weather, events, calendar).  
- Tone and accuracy still experimental.  
- Basic AI-generated UI, for the sake of presentation.
- Aims to demonstrate concept and future potential, not a finished product.

---

## 🚀 Features

Cicerone suggests **context-aware recommendations** of activities and events in Milan by combining:
- Large language model (currently OpenAI `gpt-3.5-turbo`, previously tested with LLaMA 3 8B Instruct via Together API)
- User preferences and general information (e.g. age)
- Public events (Eventbrite API)
- Weather data (OpenWeather API) 
- Personal calendar events (Google Calendar API), to avoid scheduling conflicts

The goal: a natural, informal WhatsApp-style chat that feels like talking to a friend with superpowers for Milan events — he just knows it all.

---

## 💡 Why Cicerone?

Compared to event discovery platforms that exist today:

- **Closer to real conversations**  
  Natural, chat-based interaction, like asking a friend who knows both you and the city, and uses a tone with a touch of milanese slang.
- **AI powered and user-friendlt**:
  Intelligently combines information from multiple soruces e.g. weather data -> No need for user to manually cross-check weather and events.
- **Nuanced preferences**  
  Expressed in natural language -> can subtly adapt to your current mood expressed in your own words.

---

## 🧪 Technical Notes

- If Google Calendar is not configured, the assistant still works (it will simply note that calendar integration is inactive).
- Design choice: **no Chain-of-Thought reasoning**.  
  Focus is on fast, agile replies instead of long deliberations.  
- Design choice: **Events are retrieved using Eventbrite API instead of scraping**  
  - API: stable, legal, JSON payloads  
  - Scraping: fragile, error-prone, legally risky
- **Model choice:**  
  - Current: OpenAI `gpt-3.5-turbo`.  
  - Initially tested with LLaMA 3 8B Instruct, but it produced frequent grammar mistakes in Italian, which made it unsuitable for a project focused on conversational quality and tone.

- **Additional features implemented:**  
  - Lightweight memory for storing user name, age, and preferences.  
  - CO-STAR prompting structure for clearer contextual reasoning.  
  - Few-shot prompting (general, specific, and “no events” edge cases) to guide tone and behavior.  

---

## ⚠️ Disclaimer
The code uses the correct Eventbrite endpoint (`/v3/events/search/`), but standard API keys do not include access to the **Public Events API** scope.  
As a result, API requests may return a `404` response or an empty `"events": []` payload.  

Since this is an MVP, this behavior is deliberately accepted, as the aim is just to demonstrate the integration structure and product idea.

---

## ⚙️ Quick Setup

1. **Create environment file**
   - Copy `.env.example` to `.env` and add your API keys.

2. **[OPTIONAL] Google Calendar**
   - To integrate Google Calendar, download `client_secrets.json` from Google Cloud and place it in the project root.  
   - Otherwise, ignore this step and the assistant will still work, though it will not be aware of your calendar events. 

3. **Install dependencies**
   from the project root:
   ```bash
   pip install -r requirements.txt

4. **Run the Streamlit app**
    streamlit run app.py

---

## 🛠️ Future Potential To-Do List
- **Evaluation framework**  
  - Testing so far has been manual, based on personal experimentation and interaction with the system. While the code runs without errors and delivers the intended outcomes, the next step is to build a structured evaluation framework to provide systematic and repeatable quality checks.
   - **Functional checks:**  
      - Mentions the weather when relevant.  
      - Uses Eventbrite results when available.  
      - References calendar events if enabled.  
   - **Style checks:**  
      - Italian, chatty, WhatsApp-like tone, with a touch of Milanese slang (yet not excessive).
      - Balanced number of bullet points + emoji when listing events.  
   - **Safety & quality:**  
      - No invented venues or dates.  

- **Alternative event APIs**  
  - Eventbrite has limited coverage -> Explore other free aggregators with open APIs.

- **Fine-tuning for WhatsApp tone**  
  - Supervised Fine-Tuning (LoRA) usign some language-specific Italian (or even better Milanese) chat pairs to improve Cicerone's local tone 

- **UI / Frontend**  
  - Design a web or mobile app interface.


---

## Draft and Product/Business Ideas 
The project leaves room for several potential business opportunities if it were to be developed into a full-scale app or service.
- **Personality options and partnership opportunities**  
  - Allow the user to choose the model’s tone, inspired by well-known Milanese personas.  
  - The following are just examples:  
    *Who do you want your Cicerone to be?*  
      a) Base Cicerone (Default)  
      b) Boomer Milanese  
      c) Milanese Imbruttito  
      d) Il Pagante  
  - To achieve this, the model could be fine-tuned using data gathered from these personalities, potentially through partnerships with them.

- **Premium version**  
  - Exclusive tips, discounted entries, personalized experiences  
  - Partnerships with local venues, museums, theaters  
  - Possible collaborations with cultural brands (*Milano Says*, *Milanese Imbruttito*, *Boomer Milanese*)

- **Social features** 
  - Cross-match chats of multiple users' chats to suggest and coordinate shared activities.  
  - Requires explicit user consent and privacy handling.
  - *Example*:
    - 🇮🇹 *Cicerone: "Ho visto che anche il Luis stava cercando un pub dove andare stasera. Potreste beccarvi insieme"*  
    - 🇬🇧 *Cicerone: "I noticed Luigi was also looking for a pub tonight. Maybe would be nice if you met"*

---

## 🪪 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
