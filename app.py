import streamlit as st
from supabase import create_client

1. Tes clés de connexion
URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

2. Configuration de la page
st.set_page_config(page_title="AEEMG", page_icon="🤝")

3. Connexion et Affichage
try:
supabase = create_client(URL, KEY)
st.title("🤝 AEEMG Association")
st.success("Bravo ! Ton application est connectée.")

except Exception as e:
st.error(f"Il y a une petite erreur : {e}")
