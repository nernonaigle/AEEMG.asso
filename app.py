import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

try:
supabase = create_client(v_url, v_key)
st.set_page_config(page_title="AEEMG")
st.title("🤝 AEEMG Association")
st.success("Bravo ! Connexion réussie.")

except Exception as e:
st.error(f"Erreur : {e}")
