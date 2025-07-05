import streamlit as st
from datetime import datetime
import pytz
from notion_client import Client
from notion_client.errors import APIResponseError
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

# Configuration de la page
st.set_page_config(page_title="Jardin A-Campo", page_icon="🌱", layout="centered")

# Initialisation du client Notion
notion = Client(auth=NOTION_TOKEN)

# Cacher le menu Streamlit et le footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Logo et titre
st.markdown("<h1 style='text-align: center;'>🌱 Jardin A-Campo</h1>", unsafe_allow_html=True)

# Heure locale (Paris)
now = datetime.now(pytz.timezone('Europe/Paris'))
today_str = now.strftime('%Y-%m-%d')
heure = now.strftime('%H:%M')

# État du formulaire
st.markdown("<br>", unsafe_allow_html=True)
clicked = st.button("Je commence ma journée")

# Fonction d'enregistrement
def enregistrer_entree():
    try:
        # Suppression des doublons du jour
        response = notion.databases.query(
            **{
                "database_id": DATABASE_ID,
                "filter": {
                    "property": "date",
                    "date": {"equals": today_str}
                }
            }
        )
        for result in response.get("results", []):
            notion.pages.update(page_id=result["id"], archived=True)
        if response.get("results"):
            st.info("L’entrée précédente a été supprimée.")

        # Enregistrement de la nouvelle entrée
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "date": {"date": {"start": today_str}},
                "Heure": {"rich_text": [{"text": {"content": heure}}]},
                "Message": {"rich_text": [{"text": {"content": "🌞 Nouvelle journée commencée"}}]}
            }
        )
        st.success("Entrée enregistrée dans Notion.")
    except APIResponseError as e:
        st.error("Échec de l'enregistrement dans Notion.")
        st.error(f"{e}")

if clicked:
    enregistrer_entree()

# 🔒 Affichage du bouton emoji pour révéler la maintenance
st.markdown(
    """
    <div style='position: fixed; bottom: 16px; right: 16px; z-index: 9999;'>
        <button onclick="var box = document.getElementById('secret-box'); box.style.display = (box.style.display === 'none' ? 'block' : 'none');" style='font-size: 24px; background: none; border: none; cursor: pointer;'>🫣</button>
    </div>
    """,
    unsafe_allow_html=True
)

# Boîte secrète
st.markdown(
    """
    <div id="secret-box" style="display:none; margin-top: 40px;">
        <h2>🔧 Maintenance cachée</h2>
        <p>Bienvenue dans la salle des machines.</p>
        <input type="password" placeholder="Code secret" style="padding: 8px; width: 100%; max-width: 300px;" />
        <br><br>
        <button style="padding: 8px 16px;">Nettoyer les doublons maintenant</button>
    </div>
    """,
    unsafe_allow_html=True
)
