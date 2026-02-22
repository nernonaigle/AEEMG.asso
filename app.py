{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Roman;\f1\froman\fcharset0 Times-Bold;\f2\fswiss\fcharset0 Helvetica;
\f3\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww14820\viewh15160\viewkind0
\deftab720
\pard\pardeftab720\sa240\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 import streamlit as st from supabase import create_client\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 1. Configuration de la connexion\
Remplace les valeurs entre guillemets par tes propres cl\'e9s Supabase\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 url = "
\f2 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 https://ryfrekltrgaqyryzozhc.supabase.co
\f0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 " key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 Initialisation de la connexion\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 try: supabase = create_client(url, key) except Exception as e: st.error("Erreur de connexion : V\'e9rifiez vos cl\'e9s URL et API")\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 Configuration de la page\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 st.set_page_config(page_title="Mon Association", page_icon="
\f3 \uc0\u55358 \u56605 
\f0 ", layout="wide")\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 Barre lat\'e9rale (Menu)\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 st.sidebar.title("
\f3 \uc0\u55356 \u57119 
\f0  Espace Membres") menu = ["Accueil / Mur", "Cr\'e9er mon Profil", "Publier une Activit\'e9", "Annuaire des Membres"] choix = st.sidebar.radio("Navigation", menu)\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 --- PAGE ACCUEIL (LE MUR) ---\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 if choix == "Accueil / Mur": st.title("
\f3 \uc0\u55357 \u56561 
\f0  Fil d'actualit\'e9") st.write("Bienvenue sur le r\'e9seau social de l'association !") st.divider()\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 --- PAGE PROFIL ---\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 elif choix == "Cr\'e9er mon Profil": st.title("
\f3 \uc0\u55357 \u56420 
\f0  Mon Profil") st.write("Remplissez vos informations pour que la communaut\'e9 vous connaisse.")\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 --- PAGE PUBLIER ---\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 elif choix == "Publier une Activit\'e9": st.title("
\f3 \uc0\u9997 \u65039 
\f0  Publier sur le mur")\
\pard\pardeftab720\sa321\partightenfactor0

\f1\b\fs48 \cf0 --- PAGE ANNUAIRE ---\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b0\fs24 \cf0 elif choix == "Annuaire des Membres": st.title("
\f3 \uc0\u55357 \u56421 
\f0  Annuaire de la communaut\'e9") st.write("Retrouvez ici tous les membres inscrits \'e0 l'association.") st.table(\{"Membres": ["Admin", "Pr\'e9sident", "Secr\'e9taire"], "R\'f4le": ["Fondateur", "Direction", "Gestion"]\})\
}