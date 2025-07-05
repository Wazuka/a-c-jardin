
import streamlit as st
from datetime import datetime
from notion_client import Client
import pytz
import os

st.set_page_config(page_title="Jardin A-Campo", layout="centered")

# Chargement des secrets depuis l'environnement Streamlit
NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", os.getenv("NOTION_TOKEN"))
NOTION_DATABASE_ID = st.secrets.get("NOTION_DATABASE_ID", os.getenv("NOTION_DATABASE_ID"))

# Debug visible pour test (supprimable ensuite)
st.sidebar.write(f"TOKEN starts with: {str(NOTION_TOKEN)[:6]}...")
st.sidebar.write(f"DB ID: {NOTION_DATABASE_ID}")

# Gestion erreur de token manquant
if NOTION_TOKEN is None or NOTION_DATABASE_ID is None:
    st.error("Les identifiants Notion ne sont pas correctement chargés.")
    st.stop()

client = Client(auth=NOTION_TOKEN)

st.markdown("<h1 style='text-align: center;'>🌱 Jardin A-Campo</h1>", unsafe_allow_html=True)

if st.button("Je commence ma journée"):
    paris_tz = pytz.timezone("Europe/Paris")
    now = datetime.now(paris_tz)
    today_date = now.date().isoformat()
    current_time = now.strftime("%H:%M")

    # Vérifie s’il existe déjà une entrée pour aujourd’hui
    existing = client.databases.query(
        **{
            "database_id": NOTION_DATABASE_ID,
            "filter": {
                "property": "date",
                "date": {
                    "equals": today_date
                }
            }
        }
    )

    if existing["results"]:
        st.warning("Une entrée existe déjà pour aujourd’hui.")
    else:
        try:
            new_page = client.pages.create(
                **{
                    "parent": {"database_id": NOTION_DATABASE_ID},
                    "properties": {
                        "date": {"date": {"start": today_date}},
                        "Heure": {"rich_text": [{"text": {"content": current_time}}]},
                        "Message": {"rich_text": [{"text": {"content": "🌞 Bonjour ! Une belle journée commence."}}]},
                        "Score matin": {"number": 1}
                    }
                }
            )
            st.success("Entrée enregistrée avec succès dans Notion.")
        except Exception as e:
            st.error("Échec de l'enregistrement dans Notion.")
            st.error(str(e))
