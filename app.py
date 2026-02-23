# --- 🎨 DESIGN "ÉMERAUDE & MOSQUÉE" ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# Utilisation de f-string pour éviter les conflits de caractères
css_style = """
    <style>
    .stApp {
        background: linear-gradient(rgba(18, 54, 38, 0.9), rgba(18, 54, 38, 0.9)), 
                    url("https://images.unsplash.com/photo-1590076214667-cda9e7b1ff34?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Style des conteneurs transparents */
    [data-testid="stForm"], [data-testid="stMetric"], .stChatMessage {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 20px !important;
    }

    h1, h2, h3, label, p, span {
        color: white !important;
    }

    .stButton>button {
        background-color: #2D6A4F !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid #40916C;
        font-weight: bold;
    }
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)
