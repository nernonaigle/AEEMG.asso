import streamlit as st
from supabase import create_client

supabase = create_client("", "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0")

st.title("🤝 AEEMG Association")
st.write("Connexion établie avec succès !")

tab1, tab2 = st.tabs(["Accueil", "Profil"])
with tab1: st.write("Contenu de l'accueil")
with tab2: st.write("Contenu du profil")
