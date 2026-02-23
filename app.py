import streamlit as st
from supabase import create_client

url = ""
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

supabase = create_client(url, key)

st.title("🤝 AEEMG Association")

tab1, tab2 = st.tabs(["Accueil", "Profil"])

with tab1: st.header("📱 Fil d'actualité"); st.write("Bienvenue sur l'espace AEEMG !")

with tab2: st.header("👤 Mon Profil"); nom = st.text_input("Ton nom"); st.write(nom)
