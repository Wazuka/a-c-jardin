
import streamlit as st
from datetime import datetime
from notion_client import Client
import pytz

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Jardin A-Campo", page_icon=":seedling:", layout="wide")

# --- STYLES CSS CUSTOM ---
st.markdown(
    """
    <style>
        .main {padding-bottom: 4rem;}
        button[kind="primary"] {
            background-color: transparent !important;
            color: #262730 !important;
            border: none !important;
            font-size: 1.1rem;
            box-shadow: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- VARIABLES D'ENVIRONNEMENT ---
token = st.secrets.get("NOTION_TOKEN")
database_id = st.secrets.get("NOTION_DATABASE_ID")

# --- CLIENT NOTION ---
if token and database_id:
    notion = Client(auth=token)
else:
    st.error("Les identifiants Notion ne sont pas correctement chargés.")
    st.stop()

# --- EN-TÊTE ---
st.markdown("<h1 style='text-align: center;'>🌱 Jardin A-Campo</h1>", unsafe_allow_html=True)

# --- BOUTON PRINCIPAL ---
if st.button("Je commence ma journée", use_container_width=False):
    paris_tz = pytz.timezone("Europe/Paris")
    now = datetime.now(paris_tz)
    today_str = now.strftime("%Y-%m-%d")

    # Vérifier les entrées existantes pour aujourd'hui
    results = notion.databases.query(
        **{
            "database_id": database_id,
            "filter": {
                "property": "Date",
                "date": {
                    "equals": today_str
                }
            }
        }
    )

    if len(results["results"]) > 0:
        page_id = results["results"][0]["id"]
        notion.pages.update(page_id=page_id, archived=True)
        st.info("L’entrée précédente a été supprimée.")

    try:
        notion.pages.create(
            **{
                "parent": {"database_id": database_id},
                "properties": {
                    "Nom": {
                        "title": [
                            {
                                "text": {
                                    "content": "🌄 Arrivée matinale"
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": today_str
                        }
                    },
                    "Heure": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": now.strftime("%H:%M")
                                }
                            }
                        ]
                    }
                }
            }
        )
        st.success("Bravo, ta journée est lancée !")
    except Exception as e:
        st.error("Échec de l'enregistrement dans Notion.")
        st.error(str(e))

# --- BOUTON MAINTENANCE EN BAS ---
st.markdown(
    """
    <div style='position: fixed; bottom: 20px; width: 100%; text-align: center; z-index: 9999;'>
        <form action='#secret-box'>
            <button style=\"background: none; border: none; font-size: 24px; cursor: pointer; text-align: center;\" title=\"Accès maintenance\">🛠️</button>
        </form>
    </div>
    """,
    unsafe_allow_html=True
)

# --- ZONE SECRÈTE (MANUELLE POUR L'INSTANT) ---
if "_show_secret" not in st.session_state:
    st.session_state["_show_secret"] = False

if st.session_state["_show_secret"]:
    st.subheader("🔧 Maintenance cachée")
    st.write("Bienvenue dans la salle des machines.")
    if st.button("Nettoyer les doublons maintenant"):
        st.success("Nettoyage effectué.")
