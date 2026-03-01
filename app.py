import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime
import time

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN MODERNISÉ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, rgba(2, 44, 34, 0.95) 0%, rgba(1, 20, 15, 0.98) 100%),
        url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important;
        color: white !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        height: 45px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); border-color: #D4AF37 !important; }
    .gold-text { color: #D4AF37; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 3. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
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
    st.markdown("<h1 class='gold-text'>✨ Inscription AEEMG</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prénom")
            email = c1.text_input("Email")
            pwd = c2.text_input("Mot de passe", type="password")
            ville = c1.text_input("Ville")
            organe = c2.selectbox("Organe", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
            motivation = st.text_area("Motivation")
            if st.form_submit_button("Envoyer ma demande"):
                if email and pwd and len(motivation) > 5:
                    data = {"nom": nom, "prenom": prenom, "email": email, "password": hasher_password(pwd), "ville": ville, "organe_base": organe, "motivation": motivation, "statut": "en_attente", "cotisation": False}
                    try:
                        supabase.table("membres").insert(data).execute()
                        st.success("Demande envoyée ! En attente de validation.")
                        st.balloons()
                    except: st.error("Email déjà utilisé.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Accès Membre</h2>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
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
                else: st.warning("⏳ Compte en attente de validation.")
            else: st.error("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>👋 Salam, {u['prenom']} !</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ccc; margin-top:-15px;'>Ravi de vous revoir dans votre espace membre AEEMG.</p>", unsafe_allow_html=True)

    # --- 📊 LIGNE DE STATISTIQUES ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="glass-card" style="text-align: center;">
            <p style="color: #D4AF37; margin-bottom: 5px;">Statut Membre</p>
            <h2 style="margin: 0;">✨ Actif</h2>
            <p style="font-size: 0.8em; color: #888;">ID: #00{u['id']}</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        cotis_text = "✅ À jour" if u['cotisation'] else "⚠️ À régler"
        cotis_color = "#10b981" if u['cotisation'] else "#ef4444"
        st.markdown(f"""<div class="glass-card" style="text-align: center;">
            <p style="color: #D4AF37; margin-bottom: 5px;">Cotisation 2026</p>
            <h2 style="margin: 0; color: {cotis_color};">{cotis_text}</h2>
            <p style="font-size: 0.8em; color: #888;">{u['organe_base']}</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="glass-card" style="text-align: center;">
            <p style="color: #D4AF37; margin-bottom: 5px;">Engagement</p>
            <h2 style="margin: 0;">🥈 Argent</h2>
            <p style="font-size: 0.8em; color: #888;">Fidèle membre</p>
        </div>""", unsafe_allow_html=True)

    # --- 📢 ACTUALITÉS & ACTIONS ---
    c_actu, c_action = st.columns([2, 1])
    with c_actu:
        st.markdown("### 📢 Fil d'Actualités")
        st.markdown(f"""<div class="glass-card" style="padding: 15px; border-left: 5px solid #D4AF37;">
            <small style="color: #888;">15 Mars 2026</small>
            <h4 style="margin: 5px 0;">🌙 Assemblée Générale</h4>
            <p style="font-size: 0.9em;">Rappel : Présence obligatoire pour tous les membres du Bureau National.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="glass-card" style="padding: 15px; border-left: 5px solid #065f46;">
            <small style="color: #888;">01 Mars 2026</small>
            <h4 style="margin: 5px 0;">✨ Nouveau portail membre</h4>
            <p style="font-size: 0.9em;">Votre espace membre a été mis à jour pour une meilleure expérience.</p>
        </div>""", unsafe_allow_html=True)

    with c_action:
        st.markdown("### ⚡ Actions Rapides")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.button("📄 Ma Carte Membre"):
            st.info("Fonctionnalité bientôt disponible !")
        if st.button("💳 Payer Cotisation"):
            st.success("Redirigez-vous vers l'onglet Cotisation")
        if st.button("📂 Mes Documents"):
            st.write("Accès rapide activé")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "💳 Cotisations":
    st.markdown("<h1 class='gold-text'>💳 Ma Cotisation</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("Le montant de la cotisation annuelle est de **10.000 GNF**.")
    st.info("Moyens de paiement : Orange Money / Mobile Money au +224 XXX XX XX XX")
    with st.form("pay_form"):
        trans_id = st.text_input("Numéro de Transaction (ID)")
        if st.form_submit_button("Déclarer mon paiement"):
            st.success("Reçu enregistré ! L'admin va vérifier votre paiement.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📂 Documents":
    st.markdown("<h1 class='gold-text'>📂 Bibliothèque de l'AEEMG</h1>", unsafe_allow_html=True)
    docs = [("📜 Statuts et Règlement Intérieur", "PDF"), ("📖 Guide du Membre", "PDF"), ("📋 Formulaire de projet", "DOCX")]
    for name, type_doc in docs:
        with st.expander(name):
            st.write(f"Type : {type_doc}")
            st.button(f"Télécharger {name}", key=name)

elif menu == "📸 Galerie":
    st.markdown("<h1 class='gold-text'>📸 Galerie Photos</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.image("https://images.unsplash.com/photo-1523240715630-991c2e82bc28?w=500", caption="Conférence 2025")
    c2.image("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=500", caption="Sortie de cohésion")
    c3.image("https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=500", caption="Séminaire Étudiant")

elif menu == "🛠️ Admin":
    if st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
        st.markdown("<h1 class='gold-text'>🛠️ Espace Administrateur</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["👥 Validation Membres", "📊 Statistiques"])
        with tab1:
            res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
            if not res.data: st.info("Aucune demande en attente.")
            for m in res.data:
                with st.expander(f"Dossier de {m['prenom']} {m['nom']}"):
                    st.write(f"Motivation : {m['motivation']}")
                    if st.button("Approuver ce membre", key=f"app_{m['id']}"):
                        supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                        st.success("Membre approuvé !")
                        st.rerun()
        with tab2:
            count = supabase.table("membres").select("id", count="exact").execute()
            st.metric("Total Membres", count.count if count.count else 0)

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
