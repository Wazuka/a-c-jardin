
import streamlit as st
import requests
import random
from datetime import datetime
import pytz

st.set_page_config(page_title="Jardin A-Campo", page_icon="🌱")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        footer, header {visibility: hidden;}
        .secret-button {
            border: none;
            background-color: transparent;
            font-size: 22px;
            cursor: pointer;
            position: fixed;
            bottom: 10px;
            right: 12px;
            z-index: 100;
        }
        .secret-input {
            position: fixed;
            bottom: 45px;
            right: 10px;
            width: 120px;
            z-index: 101;
        }
    </style>
""", unsafe_allow_html=True)

NOTION_TOKEN = "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"
DATABASE_ID = "227d9baaf01380b88d2dfdf1145b3750"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

messages = [
    "Aujourd’hui, on plante les graines d’un grand projet 🌱",
    "Ton jardin n’attend que toi pour fleurir 🌼",
    "Lève-toi, pousse droit, et attrape la lumière ☀️",
    "Focus, ancrage, action. Aujourd’hui compte. 🍃",
    "Chaque clic est une pousse en plus 🌿",
    "Tu sais pourquoi tu es là. Allez. C’est parti. 🚀",
]

def get_page_id_for_today():
    tz = pytz.timezone("Europe/Paris")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    for page in data["results"]:
        date_prop = page["properties"].get("date", {}).get("date", {})
        if date_prop.get("start") == today:
            return page["id"]
    return None

def delete_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"archived": True}
    response = requests.patch(url, headers=headers, json=payload)
    return response.status_code == 200

def add_entry_to_notion(date_str, time_str, message):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "date": {"date": {"start": date_str}},
            "heure": {"rich_text": [{"text": {"content": time_str}}]},
            "message": {"rich_text": [{"text": {"content": message}}]}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def clean_duplicates():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=headers)
    data = res.json()
    if "results" not in data:
        st.error("Impossible de récupérer les données depuis Notion.")
        return

    pages_by_date = {}
    for page in data["results"]:
        props = page.get("properties", {})
        date_info = props.get("date", {}).get("date")
        if not date_info:
            continue
        date_value = date_info["start"]
        page_id = page["id"]
        pages_by_date.setdefault(date_value, []).append(page_id)

    total_archived = 0
    for date, page_ids in pages_by_date.items():
        if len(page_ids) > 1:
            to_archive = page_ids[1:]
            for pid in to_archive:
                deleted = delete_page(pid)
                if deleted:
                    total_archived += 1
    st.success(f"{total_archived} doublon(s) supprimé(s) avec succès.")

if "confirm_replace" not in st.session_state:
    st.session_state.confirm_replace = False
if "reveal_code" not in st.session_state:
    st.session_state.reveal_code = False

st.title("🌱 Jardin A-Campo")

if st.button("Je commence ma journée", key="start_day"):
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

# 👁️ Emoji discret pour révéler le champ secret
if st.button("🫣", key="toggle", help="Code secret", use_container_width=False):
    st.session_state.reveal_code = not st.session_state.reveal_code

# Code secret affiché si déclenché
if st.session_state.reveal_code:
    with st.container():
        code = st.text_input("Code secret", type="password", key="secret_code")
        if code == "entretien":
            st.header("🛠️ Maintenance cachée")
            st.write("Bienvenue dans la salle des machines.")
            if st.button("Nettoyer les doublons maintenant", key="cleaner"):
                clean_duplicates()
