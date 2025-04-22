import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
import random
import plotly.express as px
from datetime import datetime

# --- Gemini setup ---
genai.configure(api_key=st.secrets["API_KEY"]) 
model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

# --- Calming UI ---
st.set_page_config(page_title="MoodSense 🌸", layout="centered")
st.markdown("""
    <style>
        body { background-color: #f0f7f4; }
        .stButton>button {
            background-color: #a3d2ca;
            color: black;
            border-radius: 12px;
            font-weight: bold;
        }
        .stTextArea>div>textarea {
            background-color: #f9f9f9;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 MoodSense")

# --- Session state init ---
if "history" not in st.session_state:
    st.session_state.history = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []
if "journal" not in st.session_state:
    st.session_state.journal = []

# --- User input ---
user_input = st.text_area("📝 Write your thoughts here:", height=200)

# --- Toggles ---
show_reasoning = st.checkbox("🔍 Show Gemini's reasoning")
enable_conversation = st.checkbox("🗨️ Conversational Mode")
privacy_mode = st.checkbox("🛡️ Privacy Mode")
st.session_state.journal_mode = st.checkbox("📔 Enable Journal Mode")

# --- Emoji map ---
emoji_map = {
    "Not Depressed": "😃",
    "Mild Depression": "😐",
    "Moderate Depression": "😞",
    "Severe Depression": "😢"
}

# --- Classification ---
def classify_depression(text):
    prompt = f"""Classify the following text into one of these categories:
    - Not Depressed
    - Mild Depression
    - Moderate Depression
    - Severe Depression

    Also return a short reasoning for your decision.

    Text: \"{text}\"
    Response:"""
    response = model.generate_content(prompt)
    return response.text

# --- Follow-up ---
def ask_followups(text):
    followup_prompt = f"""Given this text: \"{text}\", ask 1 gentle follow-up question that might help the person express their feelings more deeply."""
    reply = model.generate_content(followup_prompt)
    return reply.text.strip()

# --- Analyze Button ---
if st.button("🧠 Analyze My Mood"):
    if user_input.strip() == "":
        st.warning("Please write something first.")
    else:
        result = classify_depression(user_input)

        # Get mood label
        label_detected = None
        for label in emoji_map:
            if label.lower() in result.lower():
                label_detected = label
                break

        if label_detected:
            st.markdown(f"### Prediction: **{label_detected}** {emoji_map[label_detected]}")
        else:
            st.markdown("### Prediction: 🤖 Could not determine clearly.")

        if show_reasoning:
            st.markdown("#### 🧠 Gemini's Thought Process:")
            st.write(result)

        if enable_conversation:
            follow_up = ask_followups(user_input)
            st.markdown("#### 🗨️ Gemini asks:")
            st.info(follow_up)

        # Personalized Suggestion
        if label_detected:
            if "Moderate" in label_detected or "Severe" in label_detected:
                st.info("💡 Try this: Take a deep breath, journal your thoughts, or go for a short walk.")
            elif "Mild" in label_detected:
                st.info("💡 A small distraction might help — maybe a playlist or a call with a friend?")
            else:
                st.success("😊 You seem to be in a good place. Keep it up!")

        # Log mood (if not in privacy mode)
        if not privacy_mode and label_detected:
            st.session_state.mood_log.append((datetime.now(), label_detected))

        # Save to history if not private
        if not privacy_mode:
            st.session_state.history.append((user_input, label_detected))

        # Save journal entry
        if st.session_state.journal_mode:
            st.success("📝 Your journal entry has been saved.")
            st.session_state.journal.append((datetime.now(), user_input))

# --- Surprise Kindness ---
if st.button("🎁 Cheer Me Up"):
    kind_quotes = [
        "You are stronger than you think 💪",
        "This too shall pass ☀️",
        "You matter. Always. 💖",
        "You're doing the best you can, and that’s enough 🌿",
        "A smile looks good on you 😊"
    ]
    cute_gifs = [
        "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif",
        "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif",
        "https://media.giphy.com/media/BzyTuYCmvSORqs1ABM/giphy.gif"
    ]
    st.image(random.choice(cute_gifs))
    st.write(random.choice(kind_quotes))

# --- Mood Tracker Dashboard ---
st.markdown("## 📊 Mood Tracker")

if len(st.session_state.mood_log) > 0:
    mood_counts = {}
    for _, mood in st.session_state.mood_log:
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    fig = px.pie(
        names=list(mood_counts.keys()),
        values=list(mood_counts.values()),
        title="Mood Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig)

    last_mood = st.session_state.mood_log[-1][1]
    st.write(f"🧭 Last Recorded Mood: **{last_mood}** {emoji_map.get(last_mood, '')}")

else:
    st.info("No mood data available yet.")

# --- Journal Entries Display ---
if st.session_state.journal_mode and st.session_state.journal:
    st.markdown("### 📔 Your Journal Entries")
    for dt, entry in st.session_state.journal[::-1]:
        st.markdown(f"- *{dt.strftime('%b %d, %Y %H:%M')}*: _{entry[:100]}..._")

# --- Session History ---
if not privacy_mode and st.session_state.history:
    st.markdown("### 🧾 Session History")
    for i, (text, label) in enumerate(st.session_state.history[::-1]):
        st.markdown(f"**{label}** {emoji_map[label]} — _“{text[:100]}...”_")

# --- Clear session ---
if privacy_mode and st.button("🧹 Clear All"):
    st.session_state.history = []
    st.session_state.mood_log = []
    st.session_state.journal = []
    st.success("Session cleared.")



# --- Educational Tips ---
st.markdown("## 🧠 Mental Health Tips & Resources")
st.markdown("""
- **Sleep well** 😴: Aim for 7-8 hours per night.
- **Stay active** 🏃‍♀️: Even 10 minutes of walking helps.
- **Talk to someone** 💬: Don't isolate your feelings.
- **Practice gratitude** 🌻: Note 3 good things daily.
- [MentalHealth.gov](https://www.mentalhealth.gov) for professional resources.
""")
