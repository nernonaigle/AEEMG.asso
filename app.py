import streamlit as st
from supabase import create_client

On remplit bien les deux zones entre guillemets :
url_supabase = ""
cle_supabase = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

Connexion
supabase = create_client(url_supabase, cle_supabase)

st.title("🤝 AEEMG Association")
st.success("Connexion réussie !")

tab1, tab2 = st.tabs(["Accueil", "Profil"])
with tab1: st.write("Bienvenue sur le fil d'actualité.")
with tab2: st.write("Page de profil.")
