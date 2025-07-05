import streamlit as st
import requests
from datetime import datetime
import pytz

# Ton token et ton ID de base
NOTION_TOKEN = "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"
DATABASE_ID = "227d9baaf01380b88d2dfdf1145b3750"

# Supprime (archive) une page dans Notion
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

# Fonction de nettoyage
def clean_duplicates():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    res = requests.post(url, headers=headers)
    data = res.json()

    if "results" not in data:
        st.error("Impossible de récupérer les données depuis Notion.")
        return

    # Regrouper toutes les entrées par date
    pages_by_date = {}
    for page in data["results"]:
        props = page.get("properties", {})
        date_info = props.get("date", {}).get("date")
        if not date_info:
            continue
        date_value = date_info["start"]
        page_id = page["id"]

        if date_value in pages_by_date:
            pages_by_date[date_value].append(page_id)
        else:
            pages_by_date[date_value] = [page_id]

    # Archiver toutes les entrées sauf une (la plus ancienne par date)
    total_archived = 0
    for date, page_ids in pages_by_date.items():
        if len(page_ids) > 1:
            to_archive = page_ids[1:]
            for pid in to_archive:
                deleted = delete_page(pid)
                if deleted:
                    total_archived += 1

    st.success(f"{total_archived} doublon(s) supprimé(s) avec succès.")

# Interface Streamlit
st.title("🧹 Nettoyage des doublons - Jardin A-Campo")

if st.button("Nettoyer les doublons maintenant"):
    clean_duplicates()
