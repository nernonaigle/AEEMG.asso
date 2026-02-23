import streamlit as st
from supabase import create_client

supabase = create_client("", "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0")

st.title("🤝 AEEMG Association")
st.success("Bravo ! La connexion est enfin établie.")

tab1, tab2 = st.tabs(["Accueil", "Profil"])
with tab1: st.write("Bienvenue sur le fil d'actualité de l'AEEMG.")
with tab2: st.write("Ici, tu pourras modifier ton profil.")
