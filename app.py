import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN ULTRA MODERNE (Glassmorphism & Gold) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
    }

    .stApp {
        background: linear-gradient(135deg, rgba(2, 44, 34, 0.95) 0%, rgba(1, 20, 15, 0.98) 100%),
        url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }

    /* Cartes en Verre Flouté */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: white;
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 175, 55, 0.3);
    }

    /* Boutons Modernes */
    .stButton>button {
        border-radius: 16px !important;
        background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important;
        color: white !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        height: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        transform: scale(1.03) translateY(-2px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
        border-color: #D4AF37 !important;
    }

    /* Inputs Modernes */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Titres en Or */
    .gold-text {
        color: #D4AF37;
        font-weight: 800;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Cacher le menu Streamlit pour faire pro */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37; font-size: 2.5em;'>🌙</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white; margin-top:-20px;'>AEEMG</h2>", unsafe_allow_html=True)
    st.write("---")
    
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        # Avatar stylisé
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <img src='https://api.dicebear.com/7.x/bottts/svg?seed={st.session_state.user_info.get('nom')}' style='width: 80px; border-radius: 50%; border: 2px solid #D4AF37;'>
                <p style='color: white; margin-top: 10px;'>En ligne : <b>{st.session_state.user_info.get('prenom')}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        options = ["🏠 Tableau de Bord", "🛠️ Admin", "🚪 Déconnexion"]
        if st.session_state.user_info.get('email') != "nernonedouard99@gmail.com":
            if "🛠️ Admin" in options: options.remove("🛠️ Admin")
        menu = st.radio("Menu", options)

# --- PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 class='gold-text'>✨ Devenir Membre</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ccc;'>Rejoignez l'excellence AEEMG en quelques clics.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("inscription_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            email = c1.text_input("Adresse Email officielle")
            pwd = c2.text_input("Créer un mot de passe", type="password")
            ville = c1.text_input("Ville de résidence")
            organe = c2.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
            motivation = st.text_area("Votre motivation pour l'association", placeholder="Décrivez votre engagement...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Lancer ma demande d'adhésion"):
                if email and pwd and len(motivation) > 10:
                    data = {
                        "nom": nom, "prenom": prenom, "email": email, 
                        "password": hasher_password(pwd), "ville": ville, 
                        "organe_base": organe, "motivation": motivation,
                        "statut": "en_attente", "cotisation": False
                    }
                    try:
                        supabase.table("membres").insert(data).execute()
                        st.balloons()
                        st.success("✨ Demande enregistrée ! Un administrateur va l'examiner prochainement.")
                    except:
                        st.error("❌ Cet email semble déjà être utilisé dans nos registres.")
                else:
                    st.warning("⚠️ Merci de remplir tous les champs (motivation > 10 caractères).")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔑 Connexion":
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown("<h2 class='gold-text'>Accès Membre</h2>", unsafe_allow_html=True)
        e_log = st.text_input("Email")
        p_log = st.text_input("Mot de passe", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrer dans l'espace"):
            res = supabase.table("membres").select("*").eq("email", e_log).eq("password", hasher_password(p_log)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, user
                    st.rerun()
                else:
                    st.warning("⏳ Adhésion en cours de validation. Revenez vers nous bientôt !")
            else:
                st.error("❌ Email ou mot de passe incorrect.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"<h1 class='gold-text'>Bienvenue, {u['prenom']} !</h1>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="glass-card">
                <small style='color: #D4AF37;'>Statut</small>
                <h3>✅ Membre</h3>
                <p>ID : #00{u['id']}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="glass-card">
                <small style='color: #D4AF37;'>Organe</small>
                <h3>🏠 {u['organe_base']}</h3>
                <p>{u['ville']}</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            cotis = "Payée" if u['cotisation'] else "À régler"
            color = "#10b981" if u['cotisation'] else "#ef4444"
            st.markdown(f"""<div class="glass-card">
                <small style='color: #D4AF37;'>Cotisation</small>
                <h3 style='color: {color};'>{cotis}</h3>
                <p>Exercice 2026</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("Veuillez vous connecter.")

elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
        st.markdown("<h1 class='gold-text'>🛠️ Administration AEEMG</h1>", unsafe_allow_html=True)
        
        res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
        if not res.data:
            st.info("Tout est à jour. Aucune demande d'adhésion en attente.")
        else:
            for m in res.data:
                with st.expander(f"Dossier : {m['prenom']} {m['nom']}"):
                    st.markdown(f"""
                        <div style='background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px;'>
                            <p><b>Ville :</b> {m['ville']}</p>
                            <p><b>Motivation :</b><br>{m['motivation']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Valider l'adhésion", key=f"btn_{m['id']}"):
                        supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                        st.success(f"Compte activé !")
                        st.rerun()

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
