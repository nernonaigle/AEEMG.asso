import streamlit as st
from supabase import create_client

# 1. Connexion à ta base
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# 2. Configuration de la page et Menu
st.set_page_config(page_title="AEEMG Asso", page_icon="🤝")
page = st.sidebar.radio("Navigation", ["Inscription", "Liste des membres"])

# --- PAGE 1 : INSCRIPTION ---
if page == "Inscription":
    st.title("📝 Inscription AEEMG")
    st.write("Bienvenue ! Veuillez remplir le formulaire ci-dessous.")
    
    with st.form("form_inscription"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        
        # Le bouton est à l'intérieur du formulaire maintenant
        bouton_valider = st.form_submit_button("S'inscrire")

    if bouton_valider:
        if nom and prenom and email:
            data = {"nom": nom, "prenom": prenom, "email": email}
            supabase.table("membres").insert(data).execute()
            st.success(f"Félicitations {prenom}, l'inscription est réussie ! ✅")
        else:
            st.warning("Veuillez remplir tous les champs.")

# --- PAGE 2 : LISTE DES MEMBRES ---
elif page == "Liste des membres":
    st.title("📊 Administration")
    
    code = st.text_input("Entrez le code secret pour voir les membres", type="password")
    
    if code == "AEEMG2026": # Ton code secret
        res = supabase.table("membres").select("*").execute()
        if res.data:
            st.write(f"Il y a {len(res.data)} membres inscrits :")
            for m in res.data:
                st.info(f"👤 {m.get('prenom')} {m.get('nom')} ({m.get('email')})")
        else:
            st.write("La liste est vide.")
    elif code != "":
        st.error("Code secret incorrect ❌")
