import streamlit as st
from supabase import create_client

Connexion
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG", page_icon="🤝")
st.title("🤝 AEEMG Association")

t1, t2 = st.tabs(["Accueil", "Inscription"])

with t1:
st.header("Fil d'actualité")
st.write("Bienvenue sur l'espace officiel de l'AEEMG !")

with t2:
st.header("Devenir membre")
