
import streamlit as st
from datetime import datetime
import pytz
import requests
import os

st.set_page_config(page_title="Jardin A-Campo", page_icon="🌱", layout="centered")

# CSS pour cacher sidebar, footer et header
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        footer, header {visibility: hidden;}
        .secret-trigger {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 28px;
            background: none;
            border: none;
            cursor: pointer;
        }
        .secret-container {
            position: fixed;
            bottom: 50px;
            right: 10px;
            background: transparent;
        }
        input {
            background-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)

# LOGO ET TITRE
st.markdown("<h1 style='text-align: center;'>🌱 Jardin A-Campo</h1>", unsafe_allow_html=True)

# BOUTON PRINCIPAL
if st.button("Je commence ma journée"):
    timezone = pytz.timezone("Europe/Paris")
    now = datetime.now(timezone)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # Message motivant du matin
    messages = [
        "Un jour neuf à semer avec soin.",
        "La constance fait fleurir les projets.",
        "Ton jardin intérieur te remercie 🌿",
        "Chaque clic est une graine 🌱",
        "Aujourd’hui encore, on cultive.",
        "Matin clair, esprit fertile.",
    ]
    import random
    message = random.choice(messages)

    # Calcul du score
    heure = now.hour + now.minute / 60
    if heure < 8.5:
        score = 3
    elif heure < 9:
        score = 2
    elif heure < 10:
        score = 1
    else:
        score = 0

    # Notion API
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Supprimer ancienne entrée du jour
    query_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    query_payload = {"filter": {"property": "date", "date": {"equals": date_str}}}
    query_response = requests.post(query_url, headers=headers, json=query_payload)

    if query_response.status_code == 200:
        results = query_response.json().get("results", [])
        for page in results:
            page_id = page["id"]
            delete_url = f"https://api.notion.com/v1/pages/{page_id}"
            requests.patch(delete_url, headers=headers, json={"archived": True})
        if results:
            st.info("L’entrée précédente a été supprimée.")

    # Ajouter nouvelle entrée
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "date": {"date": {"start": date_str}},
            "Heure": {"rich_text": [{"text": {"content": time_str}}]},
            "Message": {"rich_text": [{"text": {"content": message}}]},
            "Score matin": {"number": score},
            "Commentaire": {"rich_text": []},
            "Badge": {"select": None},
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        st.success("🌼 Journée bien plantée !")
    else:
        st.error("Échec de l'enregistrement dans Notion.")

# BOUTON SECRET (bas droite)
with st.container():
    st.markdown(
        "<button class='secret-trigger' onclick='document.getElementById("secret-box").style.display = "block"'>🫣</button>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='secret-container' id='secret-box' style='display:none;'>", unsafe_allow_html=True)
    code = st.text_input("Code secret", type="password", key="secret_code")
    if code == "entretien":
        st.markdown("## 🛠️ Maintenance cachée")
        st.write("Bienvenue dans la salle des machines.")
        if st.button("Nettoyer les doublons maintenant"):
            st.info("Doublons nettoyés avec amour 🌿")
    st.markdown("</div>", unsafe_allow_html=True)
