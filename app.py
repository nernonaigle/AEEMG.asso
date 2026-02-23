import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG")
st.title("🤝 AEEMG Association")

st.header("📢 Fil d'actualité")
st.write("Bienvenue sur l'espace officiel de l'AEEMG !")

st.divider()

st.header("📝 Inscription")
nom = st.text_input("Votre Nom")
prenom = st.text_input("Votre Prénom")
email = st.text_input("Votre Email")

if st.button("Envoyer mon inscription"):
    try:
        data = {"nom": nom, "prenom": prenom, "email": email}
        supabase.table("membres").insert(data).execute()
        st.success("Félicitations !")
    except Exception as e:
        st.error(f"Détail de l'erreur : {e}")
