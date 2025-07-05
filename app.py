
import streamlit as st
import random
from datetime import datetime
import pytz
import requests

if "confirm_replace" not in st.session_state:
    st.session_state.confirm_replace = False

st.set_page_config(page_title="Commencer la journée", page_icon="🌞")
st.markdown("<h1 style='color:#0048BC;'>🌞 Commencer la journée</h1>", unsafe_allow_html=True)

import streamlit.components.v1 as components

# Ferme la sidebar automatiquement à l'ouverture
components.html(
    """
    <script>
    const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
    if (sidebar) sidebar.style.display = 'none';
    setTimeout(() => {
        if (sidebar) sidebar.style.display = '';
    }, 100);  // réactive la sidebar après chargement
    </script>
    """,
    height=0,
    width=0,
)


# Choix caché : entrée du code secret
code = st.sidebar.text_input("Code secret", type="password")
if code == "entretien":
    page = "Maintenance"
else:
    page = "Accueil"

# --- Paramètres Notion ---
NOTION_TOKEN = "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"
DATABASE_ID = "227d9baaf01380b88d2dfdf1145b3750"

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

def get_page_id_for_today():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    today = datetime.now(pytz.timezone("Europe/Paris")).strftime("%Y-%m-%d")
    payload = {
        "filter": {
            "property": "date",
            "date": {
                "equals": today
            }
        }
    }

    res = requests.post(url, headers=headers, json=payload)
    data = res.json()

    if "results" in data and len(data["results"]) > 0:
        return data["results"][0]["id"]  # Renvoie l’ID de la page
    else:
        return None  # Aucune page trouvée aujourd’hui

def delete_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "archived": True
    }
    res = requests.patch(url, headers=headers, json=payload)
    return res.status_code == 200


# --- Interface ---
if st.button("Je commence ma journée", key="start_day"):
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    message = random.choice(messages)

    # Vérifie s’il existe déjà une entrée pour aujourd’hui
    existing_page_id = get_page_id_for_today()

    if existing_page_id and not st.session_state.confirm_replace:
        st.warning("🌿 Une entrée existe déjà pour aujourd’hui.\n👉 Clique à nouveau pour la remplacer.")
        st.session_state.confirm_replace = True

    else:
        if existing_page_id:
            deleted = delete_page(existing_page_id)
            if deleted:
                st.info("L’entrée précédente a été supprimée.")
            else:
                st.error("❌ Erreur lors de la suppression de l’entrée existante.")
                st.stop()

        success = add_entry_to_notion(date_str, time_str, message)
        if success:
            st.success(f"🌱 Journée commencée à {time_str} – {message}")
            st.session_state.confirm_replace = False
        else:
            st.error("Échec de l'enregistrement dans Notion.")

if page == "Accueil":
    st.title("🌱 Jardin A-Campo")
    
    if st.button("Je commence ma journée"):
        tz = pytz.timezone("Europe/Paris")
        now = datetime.now(tz)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        message = random.choice(messages)

        existing_page_id = get_page_id_for_today()

        if existing_page_id and not st.session_state.confirm_replace:
            st.warning("🌿 Une entrée existe déjà pour aujourd’hui.\n👉 Clique à nouveau pour la remplacer.")
            st.session_state.confirm_replace = True

        else:
            if existing_page_id:
                deleted = delete_page(existing_page_id)
                if deleted:
                    st.info("L’entrée précédente a été supprimée.")
                else:
                    st.error("❌ Erreur lors de la suppression de l’entrée existante.")
                    st.stop()

            success = add_entry_to_notion(date_str, time_str, message)
            if success:
                st.success(f"🌱 Journée commencée à {time_str} – {message}")
                st.session_state.confirm_replace = False
            else:
                st.error("Échec de l'enregistrement dans Notion.")

elif page == "Maintenance":
    st.header("🛠️ Maintenance cachée")
    st.write("Bienvenue dans la salle des machines.")

    if st.button("Nettoyer les doublons maintenant"):
        clean_duplicates()


