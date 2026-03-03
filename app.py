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

def check_cotisation_du_mois(user_id) -> bool:
    if not user_id: return False
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
        return len(res.data) > 0
    except Exception: return False

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
# DESIGN / CSS MODERNE (2026 Style)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* Global Style */
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, rgba(2,44,34,0.97), rgba(1,20,15,0.99)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
}

.post-card {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 15px;
    border-left: 3px solid #D4AF37;
    margin-bottom: 25px;
    transition: transform 0.3s ease;
}
.post-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.07); }

/* Typography */
.gold-text {
    background: linear-gradient(90deg, #D4AF37, #F4D03F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* Badges */
.status-badge {
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}
.badge-paye { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
.badge-impaye { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }

/* Custom Buttons (CSS only for display) */
div.stButton > button {
    border-radius: 12px;
    background: rgba(212, 175, 55, 0.1);
    color: #D4AF37;
    border: 1px solid #D4AF37;
    transition: 0.3s;
    width: auto;
    padding: 0.5rem 1.5rem;
}
div.stButton > button:hover {
    background: #D4AF37;
    color: white;
}

/* Sidebar Custom */
[data-testid="stSidebar"] {
    background-color: rgba(1, 20, 15, 0.95);
    border-right: 1px solid rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True
