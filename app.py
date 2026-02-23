import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG")
st.title("🤝 AEEMG Association")

t1, t2 = st.tabs(["Accueil", "Profil"])

with t1: st.write("✅ Bienvenue sur le fil d'actualité de l'AEEMG !")

with t2: st.write("👤 Votre page de profil sera bientôt disponible.")
