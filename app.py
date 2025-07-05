
import streamlit as st
import pandas as pd
from datetime import datetime
import random
import os

st.set_page_config(page_title="Commencer la journée", page_icon="🌞")

st.markdown("<h1 style='color:#0048BC;'>🌞 Commencer la journée</h1>", unsafe_allow_html=True)

if not os.path.exists("messages.txt"):
    st.error("Le fichier de messages est manquant.")
else:
    with open("messages.txt", "r", encoding="utf-8") as f:
        messages = [line.strip() for line in f if line.strip()]

if st.button("Je commence ma journée"):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    message = random.choice(messages) if messages else "Bonne journée !"

    # Enregistrement dans le fichier CSV
    new_entry = pd.DataFrame([[date_str, time_str, message]], columns=["Date", "Heure", "Message"])
    if os.path.exists("journal_jardin.csv"):
        new_entry.to_csv("journal_jardin.csv", mode="a", header=False, index=False)
    else:
        new_entry.to_csv("journal_jardin.csv", index=False)

    st.success(f"🌱 Journée commencée à {time_str} – {message}")
else:
    st.info("Clique sur le bouton pour démarrer ta journée.")
