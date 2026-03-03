import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import base64
from io import BytesIO
from PIL import Image

# =========================================================
# CONFIGURATION PAGE
# =========================================================
st.set_page_config(
    page_title="AEEMG - Community",
    page_icon="🌙",
    layout="wide"
)

# =========================================================
# CONNEXION SUPABASE
# =========================================================
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS UTILES
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id) -> str:
    """Retourne le statut de la cotisation : 'valide', 'en_attente', ou 'non_paye'"""
    if not user_id: return "non_paye"
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    try:
        res = supabase.table("cotisations").select("statut").eq("user_id", user_id).gte("date_paiement", first_day).execute()
        if not res.data: return "non_paye"
        # Priorité au statut 'valide' s'il y en a plusieurs
        statuts = [r['statut'] for r in res.data]
        if "valide" in statuts: return "valide"
        if "en_attente" in statuts: return "en_attente"
        return "non_paye"
    except Exception: return "non_paye"

def process_media(file, is_profile=False):
    if file is None: return None, None
    try:
        file_type = file.type.split("/")[0]
        if file_type == "image":
            img = Image.open(file)
            size = (300, 300) if is_profile else (800, 800)
            img.thumbnail(size)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{encoded}", "image"
        else:
            encoded = base64.b64encode(file.read()).decode()
            return f"data:{file.type};base64,{encoded}", "video"
    except Exception as e:
        st.error(f"Erreur média : {e}")
        return None, None

# =========================================================
# DESIGN / CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.main .block-container { max-width: 1000px !important; padding-top: 2rem; }
.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.8), rgba(255,255,255,0.9)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* Badge de statut sur le profil */
.status-badge {
    padding: 5px 15px;
    border_radius: 20px;
    font-size: 0.8rem;
    font-weight: 800;
    text-transform: uppercase;
}
.status-valide { background: #dcfce7; color: #166534; border: 1px solid #166534; }
.status-attente { background: #fef9c3; color: #854d0e; border: 1px solid #854d0e; }
.status-non { background: #fee2e2; color: #991b1b; border: 1px solid #991b1b; }

.glass-card { background: rgba(255, 255, 255, 0.98); border-radius: 24px; padding: 25px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 20px; }
.post-card { background: #ffffff; border-radius: 20px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
.gold-text { background: linear-gradient(90deg, #B8860B, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }

div.stButton > button { border-radius: 12px; background: #064e3b; color: white; font-weight: 800; height: 3.5rem; width: 100%; border: none; }
div.stButton > button:hover { background: #D4AF37; color: white; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION ET SIDEBAR
# =========================================================
if "connecte" not in st.session_state: st.session_state.connecte = False
if "user_info" not in st.session_state: st.session_state.user_info = None

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#064e3b;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# LOGIQUE DES PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>CONNEXION</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        email = st.text_input("VOTRE EMAIL")
        password = st.text_input("MOT DE PASSE", type="password")
        if st.button("SE CONNECTER"):
            res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
            if res.data:
                user = res.data[0]
                if user.get("statut") == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else: st.warning("Compte en attente de validation.")
            else: st.error("Identifiants incorrects.")
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📝 Inscription":
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 REJOINDRE L'AEEMG</h1>", unsafe_allow_html=True)
    with st.form("inscription"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("NOM DE FAMILLE")
        prenom = c2.text_input("PRÉNOM")
        ville = c1.text_input("VILLE DE RÉSIDENCE")
        organe = c2.selectbox("ORGANE DE BASE", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"])
        email = st.text_input("EMAIL")
        p1, p2 = st.columns(2)
        pw = p1.text_input("MOT DE PASSE", type="password")
        cpw = p2.text_input("CONFIRMATION", type="password")
        if st.form_submit_button("🚀 ENVOYER LE DOSSIER"):
            if pw == cpw and email:
                data = {"nom": nom.upper(), "prenom": prenom.capitalize(), "email": email.lower(), "password": hasher_password(pw), "ville": ville, "organe_de_base": organe, "statut": "en_attente"}
                supabase.table("membres").insert(data).execute()
                st.success("✅ Dossier envoyé !")

elif st.session_state.connecte:
    u = st.session_state.user_info
    cotis_statut = check_cotisation_du_mois(u['id'])
    
    # Définition visuelle du badge
    status_class = "status-valide" if cotis_statut == "valide" else ("status-attente" if cotis_statut == "en_attente" else "status-non")
    status_label = "À Jour" if cotis_statut == "valide" else ("En attente" if cotis_statut == "en_attente" else "Non Payé")

    if menu == "🏠 Tableau de Bord":
        # HEADER SOCIAL AMÉLIORÉ
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 80px;">
            <div style="height: 180px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 20px;"></div>
            <div style="position: absolute; bottom: -40px; left: 30px; display: flex; align-items: flex-end; gap: 20px;">
                <img src="{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width: 120px; height: 120px; border-radius: 50%; border: 5px solid white; object-fit: cover; background: white;">
                <div style="padding-bottom: 10px;">
                    <h1 style="margin: 0; color: #064e3b; font-size: 1.8rem; font-weight: 800;">{u.get('prenom')} {u.get('nom')}</h1>
                    <div style="display:flex; gap:10px; align-items:center;">
                        <span style="font-weight: 700; color: #475569;">⭐ {u.get('organe_de_base')}</span>
                        <span class="status-badge {status_class}">{status_label}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📌 INFOS")
            st.write(f"**Ville:** {u.get('ville')}")
            st.write(f"**Email:** {u.get('email')}")
            st.markdown("---")
            if cotis_statut != "valide":
                st.warning("Pensez à régulariser votre cotisation du mois.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # ZONE DE PUBLICATION
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("EXPRIMEZ-VOUS...", placeholder=f"Quoi de neuf, {u.get('prenom')} ?")
                media = st.file_uploader("IMAGE/VIDÉO", type=['jpg','png','mp4'])
                if st.form_submit_button("🚀 PUBLIER"):
                    m_url, m_type = process_media(media)
                    new_post = {"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "contenu": txt, "media_url": m_url, "media_type": m_type, "date_pub": datetime.now().isoformat()}
                    supabase.table("posts").insert(new_post).execute()
                    st.rerun()

            # FLUX DE POSTS
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(5).execute()
            for post in res_posts.data:
                st.markdown(f"""
                <div class="post-card">
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;">
                        <b>{post['auteur_nom']}</b>
                    </div>
                    <p style="margin-top:10px;">{post['contenu']}</p>
                </div>
                """, unsafe_allow_html=True)

    elif menu == "💳 Cotisations":
        st.markdown(f"<h2 class='gold-text'>Mois de {calendar.month_name[date.today().month]}</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("Déclarer un paiement")
            with st.form("paiement_form", clear_on_submit=True):
                montant = st.number_input("Montant (GNF)", min_value=0, value=5000)
                ref = st.text_input("Référence de transaction / Numéro")
                preuve = st.file_uploader("Photo du reçu (Optionnel)", type=['jpg','png'])
                if st.form_submit_button("✅ Envoyer la preuve"):
                    p_url, _ = process_media(preuve)
                    data_c = {
                        "user_id": u['id'], 
                        "montant": montant, 
                        "reference": ref, 
                        "preuve_url": p_url,
                        "date_paiement": datetime.now().isoformat(),
                        "statut": "en_attente"
                    }
                    supabase.table("cotisations").insert(data_c).execute()
                    st.success("Preuve envoyée ! L'administrateur va vérifier.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("Historique récent")
            hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).order("date_paiement", desc=True).limit(5).execute()
            if hist.data:
                for h in hist.data:
                    st.write(f"📅 {h['date_paiement'][:10]} - **{h['montant']} GNF** - `{h['statut']}`")
            else:
                st.info("Aucun historique pour le moment.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🪪 Carte de Membre":
        if cotis_statut != "valide":
            st.error("⚠️ Vous devez être à jour de votre cotisation pour voir votre carte.")
        else:
            st.success("Voici votre carte de membre AEEMG !")
            # (Ici on insérera le visuel de la carte)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
