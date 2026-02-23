import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG")
st.title("🤝 AEEMG Association")

menu = st.radio("Navigation", ["Accueil", "Inscription"], horizontal=True)

if menu == "Accueil": st.write("### Bienvenue sur le fil d'actualité !")

if menu == "Inscription":
st.write("### Formulaire d'inscription")
nom = st.text_input("Ton Nom")
prenom = st.text_input("Ton Prénom")
email = st.text_input("Ton Email")
if st.button("Valider"): st.success("C'est envoyé !")
