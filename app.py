import streamlit as st
from supabase import create_client

# Connexion à ta base
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# Barre latérale pour la navigation
page = st.sidebar.radio("Aller vers :", ["Inscription", "Liste des membres"])

# --- PAGE 1 : INSCRIPTION ---
if page == "Inscription":
    st.title("📝 Inscription AEEMG")
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("Email")

    if st.button("S'inscrire"):
        data = {"nom": nom, "prenom": prenom, "email": email}
        supabase.table("membres").insert(data).execute()
        st.success(f"Félicitations {prenom}, tu es bien inscrit !")

# --- PAGE 2 : LISTE DES MEMBRES ---
elif page == "Liste des membres":
    st.title("📊 Membres inscrits")
    res = supabase.table("membres").select("*").execute()
    
    if res.data:
        for m in res.data:
            st.info(f"👤 {m.get('prenom')} {m.get('nom')}")
    else:
        st.write("Aucun membre pour le moment.")
