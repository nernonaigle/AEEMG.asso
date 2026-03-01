import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime
import time

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN INSTITUTIONNEL (Vert Émeraude & Or) ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background: linear-gradient(rgba(2, 44, 34, 0.9), rgba(2, 44, 34, 0.95)),
        url("https://images.unsplash.com/photo-1518005020250-6eb5f3f2754d?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }

    .stButton>button {
        border-radius: 12px !important;
        background-color: #065f46 !important;
        color: white !important;
        border: 1px solid #D4AF37 !important;
        transition: all 0.3s ease;
        height: 45px;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #047857 !important;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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
        st.markdown(f"🟢 **{st.session_state.user_info.get('prenom')}**")
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        if st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin") 
        menu = st.radio("Menu Principal", options)

# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 style='color: white;'>✨ Parcours d'Adhésion</h1>", unsafe_allow_html=True)
    
    steps = ["Identifiants", "État Civil", "Engagement"]
    st.progress(st.session_state.step_inscription / 3)
    st.info(f"Étape {st.session_state.step_inscription} sur 3 : {steps[st.session_state.step_inscription-1]}")

    if st.session_state.step_inscription == 1:
        with st.form("step1"):
            st.markdown("### 🔑 Créez vos accès")
            email = st.text_input("Adresse Email")
            pwd = st.text_input("Mot de passe", type="password")
            confirm = st.text_input("Confirmez le mot de passe", type="password")
            if st.form_submit_button("Continuer →"):
                if pwd == confirm and "@" in email:
                    st.session_state.temp_user['email'] = email
                    st.session_state.temp_user['password'] = hasher_password(pwd)
                    st.session_state.step_inscription = 2
                    st.rerun()
                else: st.error("Vérifiez l'email et les mots de passe.")

    elif st.session_state.step_inscription == 2:
        with st.form("step2"):
            st.markdown("### 📋 Informations Personnelles")
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            dnaiss = c1.date_input("Date de naissance", min_value=datetime(1960,1,1))
            lnaiss = c2.text_input("Lieu de naissance")
            pere = c1.text_input("Nom du Père")
            mere = c2.text_input("Nom de la Mère")
            domicile = c1.text_input("Domicile")
            ville = c2.text_input("Ville")
            organe = st.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
            
            if st.form_submit_button("Continuer →"):
                st.session_state.temp_user.update({
                    "nom": nom, "prenom": prenom, "date_naissance": str(dnaiss),
                    "lieu_naissance": lnaiss, "nom_pere": pere, "nom_mere": mere,
                    "domicile": domicile, "ville": ville, "organe_base": organe
                })
                st.session_state.step_inscription = 3
                st.rerun()

    elif st.session_state.step_inscription == 3:
        with st.form("step3"):
            st.markdown("### ✍️ Lettre d'Adhésion")
            source = st.selectbox("Comment nous avez-vous connu ?", ["Réseaux Sociaux", "Bouche à oreille", "Affichage", "Événement"])
            motivation = st.text_area("Pourquoi souhaitez-vous rejoindre l'AEEMG ?", height=150)
            st.write("---")
            accept_rgpd = st.checkbox("J'accepte la politique de confidentialité.")
            
            if st.form_submit_button("Soumettre ma demande"):
                if accept_rgpd and len(motivation) > 10:
                    data = st.session_state.temp_user
                    data.update({"motivation": motivation, "source": source, "statut": "en_attente", "cotisation": False})
                    try:
                        supabase.table("membres").insert(data).execute()
                        st.balloons()
                        st.success("✅ Demande envoyée ! Redirection vers la connexion...")
                        
                        # Réinitialisation pour la prochaine fois
                        st.session_state.step_inscription = 1
                        st.session_state.temp_user = {}
                        
                        # Pause de 3 secondes pour laisser l'utilisateur voir le message
                        time.sleep(3)
                        st.rerun()
                    except:
                        st.error("Cet email est déjà inscrit.")
                else: st.warning("Veuillez remplir la motivation (min. 10 caractères).")

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center; color: white;'>🔑 Accès Membre</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", hasher_password(p_l)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, user
                    st.rerun()
                else: st.warning("⏳ Votre adhésion est en attente de validation par l'administration.")
            else: st.error("Email ou mot de passe incorrect.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"<h1 style='text-align: center; color: white;'>Bienvenue, {u.get('prenom')}</h1>", unsafe_allow_html=True)
        st.write("---")
        st.markdown(f"""<div class="glass-card">
            <h3>Félicitations !</h3>
            <p>Vous êtes officiellement membre approuvé de l'AEEMG.</p>
            <p><b>ID Membre :</b> #00{u.get('id')}</p>
            <p><b>Section :</b> {u.get('organe_base')}</p>
        </div>""", unsafe_allow_html=True)
    else: st.warning("Veuillez vous connecter.")

elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
        st.title("🛠️ Gestion AEEMG")
        t1, t2, t3 = st.tabs(["📢 Adhésions", "💰 Finances", "👥 Membres"])
        with t1:
            res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
            if not res.data: st.info("Aucune demande en attente.")
            for m in res.data:
                with st.expander(f"Demande de {m['prenom']} {m['nom']}"):
                    st.write(f"**Motivation :** {m.get('motivation')}")
                    if st.button("Approuver le membre", key=f"app_{m['id']}"):
                        supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                        st.success("Membre approuvé avec succès !")
                        st.rerun()

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
