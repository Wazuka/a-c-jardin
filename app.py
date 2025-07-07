import streamlit as st
from datetime import datetime
from notion_client import Client
import pytz
import random
import os

# --- CONFIG PAGE ---
st.set_page_config(page_title="Jardin A-Campo", layout="centered", initial_sidebar_state="collapsed")

# --- VARIABLES D'ENVIRONNEMENT ---
token = st.secrets.get("NOTION_TOKEN")
database_id = st.secrets.get("NOTION_DATABASE_ID")
password = st.secrets.get("MAINTENANCE_PASSWORD")
message_path = "messages.txt"

# --- CLIENT NOTION ---
if token and database_id:
    notion = Client(auth=token)
else:
    st.error("Les identifiants Notion ne sont pas correctement chargés.")
    st.stop()

# --- VÉRIFICATION DE LA COLONNE "Date" ---
db_info = notion.databases.retrieve(database_id=database_id)
if "Date" not in db_info["properties"] or db_info["properties"]["Date"]["type"] != "date":
    st.error("La colonne 'Date' est manquante ou n’est pas du type 'date' dans la base Notion.")
    st.stop()

# --- UTILS ---
def calcul_score_depuis_config(heure_str, config_path="score_config.json"):
    import json
    from datetime import datetime

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            regles = json.load(f)
    except FileNotFoundError:
        st.warning("Fichier de configuration de score introuvable.")
        return 0

    heure_arrivee = datetime.strptime(heure_str, "%H:%M").time()

    for regle in regles:
        seuil = datetime.strptime(regle["heure_max"], "%H:%M").time()
        if heure_arrivee <= seuil:
            return regle["score"]

    return 0
def get_today_iso():
    paris_tz = pytz.timezone("Europe/Paris")
    now = datetime.now(paris_tz)
    return now.date().isoformat(), now.strftime("%H:%M")

def load_messages():
    if os.path.exists(message_path):
        with open(message_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return ["Belle journée au jardin.", "Merci pour ta présence.", "Un geste simple, une présence forte."]

# --- SESSION INIT ---
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "entry_written" not in st.session_state:
    st.session_state.entry_written = False
if "show_maintenance" not in st.session_state:
    st.session_state.show_maintenance = False

# --- STYLES ---
st.markdown("""
    <style>
        .main .block-container {
            max-width: 600px;
            margin: auto;
        }
        .maintenance-button-fixed {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
        }
        .maintenance-button-fixed button {
            background: none;
            border: none;
            font-size: 22px;
            cursor: pointer;
            color: inherit;
            box-shadow: none;
            padding: 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- TITRE ---
st.markdown("<h2 style='text-align: center;'>🌼 Jardin A-Campo</h2>", unsafe_allow_html=True)

# --- INTERFACE ---
today_str, now_str = get_today_iso()
messages = load_messages()

st.markdown("<div class='centered-container'>", unsafe_allow_html=True)

if not st.session_state.entry_written:
    if st.button("🚀 Commencer ma journée"):
        results = notion.databases.query(
            database_id=database_id,
            filter={"property": "Date", "date": {"equals": today_str}}
        )
        if results["results"] and not st.session_state.confirmed:
            st.warning("Une entrée existe déjà aujourd'hui. Clique à nouveau pour confirmer l'écrasement.")
            st.session_state.confirmed = True
        else:
            for page in results["results"]:
                notion.pages.update(page_id=page["id"], archived=True)
            message = random.choice(messages)
            score = calcul_score_depuis_config(now_str)
            notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Date": {"date": {"start": f"{today_str}T{now_str}:00+02:00"}},
                "Heure": {"rich_text": [{"text": {"content": now_str}}]},
                "Message": {"rich_text": [{"text": {"content": message}}]},
                "Score matin": {"number": score}
            }
        )
            st.session_state.entry_written = True
            st.markdown(f"<div style='background-color:#eaf6ec; padding:0.5em 1em; border-radius:8px;'>"
            f"{message}<br><i>Heure enregistrée : {now_str}</i></div>", unsafe_allow_html=True)

else:
    st.info("Entrée déjà enregistrée aujourd'hui.")

st.markdown("</div>", unsafe_allow_html=True)





