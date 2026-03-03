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
    page_title="AEEMG - Espace Membre",
    page_icon="🌙",
    layout="wide"
)

# =========================================================
# CONNEXION SUPABASE (Gardez vos clés ici)
# =========================================================
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS UTILES
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id: int) -> bool:
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = (supabase.table("cotisations")
               .select("*")
               .eq("user_id", user_id)
               .eq("statut", "valide")
               .gte("date_paiement", first_day)
               .lte("date_paiement", last_day)
               .execute())
        return bool(res.data)
    except: return False

def process_media(file, is_profile=False):
    if file is None: return None, None
    file_type = file.type.split("/")[0]
    if file_type == "image":
        img = Image.open(file)
        size = (300, 300) if is_profile else (800, 800)
        img.thumbnail(size)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded}", "image"
    encoded = base64.b64encode(file.read()).decode()
    return f"data:{file.type};base64,{encoded}", "video"

# =========================================================
# DESIGN / CSS (Amélioré)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp {
    background: linear-gradient(135deg, rgba(2,44,34,0.95), rgba(1,20,15,0.98)),
    url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}
.glass-card {
    background: rgba(255,255,255,0.06); backdrop-filter: blur(15px);
    border-radius: 16px; padding: 25px; border: 1px solid rgba(255,255,255,0.12);
    color: white; margin-bottom: 20px;
}
.gold-text { color: #D4AF37; font-weight: 800; }
.badge-paye { background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; }
.badge-impaye { background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; }

/* Carte de Membre Style */
.member-card {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 100%);
    border: 2px solid #D4AF37; border-radius: 15px; padding: 20px;
    width: 350px; position: relative; overflow: hidden; color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIQUE DE SESSION
# =========================================================
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center;color:#D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u["id"])
        avatar = u.get("photo_url") if u.get("photo_url") else "https://www.w3schools.com/howto/img_avatar.png"
        st.image(avatar, width=100)
        st.markdown(f"<p style='text-align:center'><b>{u['prenom']} {u['nom']}</b></p>", unsafe_allow_html=True)
        
        badge_class = "badge-paye" if est_a_jour else "badge-impaye"
        status_txt = "✅ À JOUR" if est_a_jour else "⚠️ À RÉGLER"
        st.markdown(f"<div class='{badge_class}' style='text-align:center'>{status_txt}</div><br>", unsafe_allow_html=True)
        
        menu = st.radio("Menu", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES DE L'APPLICATION
# =========================================================

# --- CONNEXION ---
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center'>Connexion Espace Membre</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
            if res.data:
                user = res.data[0]
                if user["statut"] == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else: st.warning("⏳ Compte en attente de validation")
            else: st.error("Identifiants incorrects")
        st.markdown("</div>", unsafe_allow_html=True)

# --- INSCRIPTION ---
elif menu == "📝 Inscription":
    st.markdown("<h2 class='gold-text' style='text-align:center'>Rejoindre l'AEEMG</h2>", unsafe_allow_html=True)
    with st.form("form_inscription"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
        with col2:
            password = st.text_input("Mot de passe", type="password")
            ville = st.text_input("Ville")
            organe = st.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale"])
        
        photo = st.file_uploader("Photo de profil (Optionnel)", type=['jpg', 'png', 'jpeg'])
        motivation = st.text_area("Pourquoi rejoindre l’AEEMG ?")
        
        if st.form_submit_button("Envoyer ma demande"):
            if not all([nom, prenom, email, password, ville, motivation]):
                st.error("⚠️ Remplissez tous les champs obligatoires")
            else:
                p_url, _ = process_media(photo, is_profile=True)
                supabase.table("membres").insert({
                    "nom": nom, "prenom": prenom, "email": email,
                    "password": hasher_password(password), "ville": ville,
                    "motivation": motivation, "organe_base": organe,
                    "statut": "en_attente", "photo_url": p_url
                }).execute()
                st.success("✅ Demande envoyée ! Vous recevrez un mail après validation.")

# --- TABLEAU DE BORD ---
elif menu == "🏠 Tableau de Bord" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>Salam {u['prenom']} !</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='glass-card'><h3>Statut</h3><p>{u['statut'].upper()}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='glass-card'><h3>Organe</h3><p>{u['organe_base']}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='glass-card'><h3>Ville</h3><p>{u['ville']}</p></div>", unsafe_allow_html=True)

# --- COTISATIONS ---
elif menu == "💳 Cotisations" and st.session_state.connecte:
    st.markdown("<h2 class='gold-text'>Gestion des Cotisations</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Payer ma cotisation", "Mon Historique"])
    
    with tab1:
        with st.form("pay_cotis"):
            montant = st.number_input("Montant (GNF)", min_value=0, value=5000)
            preuve = st.file_uploader("Capture d'écran du transfert", type=['jpg', 'png'])
            if st.form_submit_button("Envoyer la preuve"):
                p_data, _ = process_media(preuve)
                supabase.table("cotisations").insert({
                    "user_id": st.session_state.user_info["id"],
                    "montant": montant, "preuve_url": p_data,
                    "statut": "en_attente", "date_paiement": date.today().isoformat()
                }).execute()
                st.info("Preuve envoyée. Un administrateur va la valider.")

    with tab2:
        res = supabase.table("cotisations").select("*").eq("user_id", st.session_state.user_info["id"]).execute()
        if res.data: st.table(res.data)
        else: st.write("Aucun historique pour le moment.")

# --- CARTE DE MEMBRE ---
elif menu == "🪪 Carte de Membre" and st.session_state.connecte:
    st.markdown("<h2 class='gold-text'>Votre Carte Numérique</h2>", unsafe_allow_html=True)
    u = st.session_state.user_info
    photo = u.get("photo_url") or "https://www.w3schools.com/howto/img_avatar.png"
    
    card_html = f"""
    <div class="member-card">
        <div style="text-align:center">
            <img src="{photo}" style="width:100px; height:100px; border-radius:50%; border:2px solid #D4AF37;">
            <h3 style="margin:10px 0;">{u['prenom']} {u['nom']}</h3>
            <p style="color:#D4AF37; font-size:0.9em;">MEMBRE AEEMG</p>
        </div>
        <hr style="border:0.5px solid rgba(212,175,55,0.3)">
        <p style="font-size:0.8em;"><b>ID:</b> #00{u['id']}</p>
        <p style="font-size:0.8em;"><b>Organe:</b> {u['organe_base']}</p>
        <p style="font-size:0.8em;"><b>Ville:</b> {u['ville']}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    st.button("📥 Télécharger ma carte (Bientôt disponible)")

# --- DOCUMENTS & GALERIE (Squelettes prêts) ---
elif menu == "📂 Documents" and st.session_state.connecte:
    st.markdown("<h2 class='gold-text'>Documents Officiels</h2>", unsafe_allow_html=True)
    st.info("Les statuts et règlements intérieurs seront bientôt téléchargeables ici.")

elif menu == "📸 Galerie" and st.session_state.connecte:
    st.markdown("<h2 class='gold-text'>Galerie Photos</h2>", unsafe_allow_html=True)
    st.write("Retrouvez ici les photos des derniers événements.")

# --- DÉCONNEXION ---
elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
