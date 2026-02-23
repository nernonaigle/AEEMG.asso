import streamlit as st
from supabase import create_client

Variables de connexion
v_url = ""
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

Connexion directe
supabase = create_client(v_url, v_key)

Interface
st.title("🤝 AEEMG Association")
st.success("Connexion réussie !")

tab1, tab2 = st.tabs(["Accueil", "Profil"])
with tab1: st.write("Bienvenue sur le fil d'actualité.")
with tab2: st.write("Page de profil.")
