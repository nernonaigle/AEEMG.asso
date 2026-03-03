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
st.set_page_config(page_title="AEEMG - Community", page_icon="🌙", layout="wide")

# =========================================================
# CONNEXION SUPABASE
# =========================================================
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id) -> str:
    if not user_id: return "non_paye"
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    try:
        res = supabase.table("cotisations").select("statut").eq("user_id", user_id).gte("date_paiement", first_day).execute()
        if not res.data: return "non_paye"
        statuts = [r['statut'] for r in res.data]
        if "valide" in statuts: return "valide"
        if "en_attente" in statuts: return "en_attente"
        return "non_paye"
    except: return "non_paye"

def process_media(file):
    if file is None: return None, None
    try:
        encoded = base64.b64encode(file.read()).decode()
        return f"data:{file.type};base64,{encoded}", file.type.split("/")[0]
    except: return None, None

# =========================================================
# DESIGN "ULTRA-LUMINEUX" (STYLE APPLE/FACEBOOK LIGHT)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

/* Reset global pour éviter le sombre */
.stApp {
    background: #F0F2F5 !important; /* Gris très clair style Facebook */
    color: #1c1e21 !important;
}

/* Container principal */
.main .block-container { max-width: 1100px !important; padding-top: 2rem; }

/* Cartes Blanches Lumineuses */
.glass-card {
    background: #FFFFFF !important;
    border-radius: 16px;
    padding: 25px;
    border: 1px solid #E4E6EB;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    color: #1c1e21 !important;
}

/* Post Card */
.post-card {
    background: #FFFFFF !important;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid #E4E6EB;
}

/* Badges de Statut */
.badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
}
.bg-success { background: #E7F3FF; color: #1877F2; } /* Bleu/Vert clair */
.bg-warning { background: #FFF9E0; color: #F7B928; } /* Jaune clair */
.bg-danger { background: #FFEBEB; color: #FA383E; }  /* Rouge clair */
