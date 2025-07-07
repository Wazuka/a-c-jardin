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
            notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Date": {"date": {"start": f"{today_str}T{now_str}:00+02:00"}},
                "Heure": {"rich_text": [{"text": {"content": now_str}}]}
            }
        )
            st.session_state.entry_written = True
            st.success(f"{random.choice(messages)}\nHeure enregistrée : {now_str}")
else:
    st.info("Entrée déjà enregistrée aujourd'hui.")

st.markdown("</div>", unsafe_allow_html=True)

# --- BOUTON MAINTENANCE FIXE BAS CENTRE ---
st.markdown("""
    <div class='maintenance-button-fixed'>
    <div style='text-align: center;'>
        <!-- Le bouton Streamlit est géré en Python -->
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🛠️", key="maintenance_icon"):
    st.session_state.show_maintenance = not st.session_state.show_maintenance


if st.session_state.show_maintenance:
    with st.form("maintenance_form"):
        password_input = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Valider")
        if submitted:
            if password_input == password:
                st.success("Accès maintenance autorisé")
                if st.button("🧹 Supprimer les doublons"):
                    entries = notion.databases.query(
                        database_id=database_id,
                        filter={"property": "Date", "date": {"equals": today_str}}
                    )
                    if len(entries["results"]) > 1:
                        for page in entries["results"][1:]:
                            notion.pages.update(page_id=page["id"], archived=True)
                        st.success("Doublons archivés avec succès.")
                    else:
                        st.info("Aucun doublon à nettoyer aujourd’hui.")
            else:
                st.error("Mot de passe incorrect")
