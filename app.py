import streamlit as st
from datetime import datetime
from notion_client import Client
import pytz

# --- CONFIG PAGE ---
st.set_page_config(page_title="Jardin A-Campo", layout="centered", initial_sidebar_state="collapsed")

# --- VARIABLES D'ENVIRONNEMENT ---
token = st.secrets.get("NOTION_TOKEN")
database_id = st.secrets.get("NOTION_DATABASE_ID")

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

# --- FONCTION UTILITAIRE ---
def get_today_iso():
    paris_tz = pytz.timezone("Europe/Paris")
    return datetime.now(paris_tz).date().isoformat()

# --- STYLES ---
st.markdown("""
    <style>
        .centered-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 400px;
            margin: 0 auto;
        }
        .maintenance-button {
            position: fixed;
            bottom: 20px;
            width: 100%;
            text-align: center;
            z-index: 9999;
        }
    </style>
""", unsafe_allow_html=True)

# --- INTERFACE ---
st.markdown("<h2 style='text-align: center;'>🌱 Jardin A-Campo</h2>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    if st.button("Je commence ma journée"):
        today_str = get_today_iso()

        # Vérifie si une entrée existe déjà aujourd'hui
        results = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Date",
                "date": {
                    "equals": today_str
                }
            }
        )

        if results["results"]:
            st.warning("Une entrée existe déjà pour aujourd’hui.")
        else:
            response = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Date": {
                        "date": {
                            "start": today_str
                        }
                    }
                }
            )
            st.success("🌞 Journée enregistrée avec succès !")
    st.markdown("</div>", unsafe_allow_html=True)

# --- BOUTON MAINTENANCE EN BAS ---
st.markdown("""
    <div class='maintenance-button'>
        <form action="#maintenance">
            <button style='background: none; border: none; font-size: 22px; cursor: pointer;' title="Maintenance">🛠️</button>
        </form>
    </div>
""", unsafe_allow_html=True)

# --- ZONE DE MAINTENANCE ---
with st.expander("🔧 Zone de maintenance", expanded=False):
    if st.button("🧹 Nettoyer les doublons"):
        today_str = get_today_iso()
        entries = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Date",
                "date": {
                    "equals": today_str
                }
            }
        )
        if len(entries["results"]) > 1:
            for page in entries["results"][1:]:
                notion.pages.update(page_id=page["id"], archived=True)
            st.success("Doublons archivés avec succès.")
        else:
            st.info("Aucun doublon à nettoyer aujourd’hui.")