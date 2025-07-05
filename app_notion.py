
import streamlit as st
import random
from datetime import datetime
import pytz
import requests

st.set_page_config(page_title="Commencer la journée", page_icon="🌞")
st.markdown("<h1 style='color:#0048BC;'>🌞 Commencer la journée</h1>", unsafe_allow_html=True)

# --- Paramètres Notion ---
NOTION_TOKEN = "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"
DATABASE_ID = "227d9baaf0138087aa24cc256305a7b4"

# Messages possibles
messages = [
    "Clara est ravie. Le jardin aussi.",
    "Tu avances, et moi je te regarde pousser.",
    "Ce matin est une page blanche, et tu es déjà en train de l’écrire.",
    "Un nouveau jour, une graine plantée.",
    "8h12. Et tout est encore possible.",
    "Ton énergie du matin est une lumière. Continue.",
    "🌱 À cette heure, tout pousse mieux.",
    "C’est le calme du matin qui te rend fort.",
    "Clara sourit doucement : tu es à l’heure.",
    "Journée commencée à l’heure, tout pousse mieux."
]

def add_entry_to_notion(date_str, time_str, message):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Nom": { "title": [{ "text": { "content": date_str } }] },
            "date": { "date": { "start": date_str } },
            "Heure": { "rich_text": [{ "text": { "content": time_str } }] },
            "Message": { "rich_text": [{ "text": { "content": message } }] }
        }
    }
    res = requests.post(url, headers=headers, json=data)
    return res.status_code == 200 or res.status_code == 201

# --- Interface ---
if st.button("Je commence ma journée"):
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    message = random.choice(messages)

    if add_entry_to_notion(date_str, time_str, message):
        st.success(f"🌱 Journée commencée à {time_str} – {message}")
    else:
        st.error("Échec de l'enregistrement dans Notion.")
else:
    st.info("Clique sur le bouton pour démarrer ta journée.")
