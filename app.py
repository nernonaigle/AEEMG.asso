import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTION DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN INSTITUTIONNEL (Vert Émeraude Foncé) ---
st.set_page_config(page_title="AEEMG - Adhésion", page_icon="🌙", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background: linear-gradient(rgba(2, 44, 34, 0.85), rgba(2, 44, 34, 0.95)),
        url("https://images.unsplash.com/photo-1518005020250-6eb5f3f2754d?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }

    .stButton>button {
        border-radius: 12px !important;
        background-color: #065f46 !important; /* Vert Emeraude Foncé */
        color: white !important;
        border: 1px solid #D4AF37 !important; /* Bordure Or */
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #047857 !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# 2. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None
if "step_inscription" not in st.session_state:
    st.session_state.step_inscription = 1
if "temp_user" not in st.session_state:
    st.session_state.temp_user = {}

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    st.write("---")
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        st.markdown(f"🟢 **{st.session_state.user_info['prenom']}**")
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        if st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin") 
        menu = st.radio("Menu Principal", options)

# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 style='color: white;'>✨ Parcours d'Adhésion</h1>", unsafe_allow_html=True)
    
    # Barre de progression
    progression = ["Identifiants", "État Civil", "Engagement"]
    st.info(f"Étape {st.session_state.step_inscription} : {progression[st.session_state.step_inscription-1]}")

    if st.session_state.step_inscription == 1:
        with st.form("step1"):
            st.markdown("### 🔑 Vos identifiants de connexion")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            confirm = st.text_input("Confirmer le mot de passe", type="password")
            if st.form_submit_button("Continuer"):
                if pwd == confirm and email:
                    st.session_state.temp_user['email'] = email
                    st.session_state.temp_user['password'] = hasher_password(pwd)
                    st.session_state.step_inscription = 2
                    st.rerun()
                else: st.error("Vérifiez l'email et les mots de passe.")

    elif st.session_state.step_inscription == 2:
        with st.form("step2"):
            st.markdown("### 📋 État Civil & Localisation")
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            dnaiss = c1.date_input("Date de naissance", min_value=datetime(1960,1,1))
            lnaiss = c2.text_input("Lieu de naissance")
            pere = c1.text_input("Nom du Père")
            mere = c2.text_input("Nom de la Mère")
            domicile = c1.text_input("Domicile actuel")
            ville = c2.text_input("Ville")
            organe = st.selectbox("Organe de base", ["Bureau National", "Cellule Universitaire", "Antenne Régionale"])
            
            if st.form_submit_button("Continuer"):
                st.session_state.temp_user.update({
                    "nom": nom, "prenom": prenom, "date_naissance": str(dnaiss),
                    "lieu_naissance": lnaiss, "nom_pere": pere, "nom_mere": mere,
                    "domicile": domicile, "ville": ville, "organe_base": organe
                })
                st.session_state.step_inscription = 3
                st.rerun()

    elif st.session_state.step_inscription == 3:
        with st.form("step3"):
            st.markdown("### ✍️ Engagement et Motivation")
            source = st.selectbox("Comment avez-vous entendu parler de l'AEEMG ?", ["Réseaux Sociaux", "Ami/Famille", "Événement", "Autre"])
            motivation = st.text_area("Justifiez votre lettre d'adhésion (Vos motivations)", height=200)
            st.write("---")
            accept_rgpd = st.checkbox("Je consens au partage de mes données et j'accepte les règles de confidentialité de l'AEEMG.")
            
            if st.form_submit_button("Soumettre ma demande d'adhésion"):
                if accept_rgpd and motivation:
                    data = st.session_state.temp_user
                    data.update({"motivation": motivation, "source": source, "statut": "en_attente", "cotisation": False})
                    supabase.table("membres").insert(data).execute()
                    st.balloons()
                    st.success("Demande envoyée avec succès ! L'administration va examiner votre profil.")
                    st.session_state.step_inscription = 1
                else: st.warning("Veuillez remplir la motivation et accepter les conditions.")

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center; color: white;'>🔑 Connexion</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", hasher_password(p_l)).execute()
            if res.data:
                user = res.data[0]
                if user['statut'] == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, user
                    st.rerun()
                else:
                    st.warning("⏳ Votre adhésion est encore en cours d'examen par l'administration.")
            else: st.error("Identifiants incorrects")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"""<div style='text-align: center; padding: 20px;'>
            <img src='https://api.dicebear.com/7.x/avataaars/svg?seed={u['nom']}' style='border-radius: 50%; width: 120px; background: white; border: 3px solid #D4AF37;'>
            <h1 style='color: white;'>{u['prenom']} {u['nom']}</h1>
        </div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="glass-card">
                <h3>📋 Ma Fiche</h3>
                <p><b>Organe :</b> {u.get('organe_base', 'N/A')}</p>
                <p><b>Ville :</b> {u.get('ville', 'N/A')}</p>
                <p><b>Email :</b> {u['email']}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="glass-card">
                <h3>💎 Cotisation</h3>
                <p>Statut : {'✅ À jour' if u['cotisation'] else '❌ Non payée'}</p>
            </div>""", unsafe_allow_html=True)
    else: st.warning("Connectez-vous")

elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
        st.title("🛠️ Administration Royale")
        tab_v, tab_p, tab_m = st.tabs(["✅ Validation Adhésions", "💰 Paiements", "👥 Membres"])
        
        with tab_v:
            res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
            if not res.data: st.info("Aucune demande en attente.")
            for m in res.data:
                with st.expander(f"Demande de {m['prenom']} {m['nom']}"):
                    st.write(f"**Père :** {m['nom_pere']} | **Mère :** {m['nom_mere']}")
                    st.write(f"**Motivation :** {m['motivation']}")
                    if st.button("Approuver l'Adhésion", key=f"app_{m['email']}"):
                        supabase.table("membres").update({"statut": "approuve"}).eq("email", m['email']).execute()
                        st.success("Membre approuvé !")
                        st.rerun()

        with tab_p:
            res_p = supabase.table("paiements").select("*").eq("statut", "en attente").execute()
            for p in res_p.data:
                st.write(f"Paiement de {p['email']}")
                if st.button("Valider paiement", key=f"vp_{p['id']}"):
                    supabase.table("paiements").update({"statut": "validé"}).eq("id", p['id']).execute()
                    supabase.table("membres").update({"cotisation": True}).eq("email", p['email']).execute()
                    st.rerun()
                    
        with tab_m:
            st.subheader("Liste Complète")
            m_res = supabase.table("membres").select("*").execute()
            st.table(m_res.data)

elif menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.session_state.user_info = None
    st.session_state.step_inscription = 1
    st.rerun()
