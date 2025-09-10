import streamlit as st

st.set_page_config(page_title="Sistem Peminjaman Lab", page_icon="💻", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background-color: #0A0F29; color: #FFD700; margin: 0 auto;}
    section[data-testid="stSidebar"] { background-color: #FFFFFF; color: #000000; }
    section[data-testid="stSidebar"] * { color: #000000 !important; }
    .computer-card { border-radius: 10px; padding: 15px; margin: 5px; text-align: center; font-weight: bold; }
    .available { background-color: #006400; color: #FFFFFF; }
    .not-available { background-color: #8B0000; color: #FFFFFF; }
    .computer-card p { color: #FFFFFF !important; }
    
    .stButton>button {
        color: #065F46;
        background-color: #A3E635;  /* Mengatur warna latar belakang tombol */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Judul utama
st.title("💻 Sistem Peminjaman Komputer & Alat Lab")

st.markdown(
    """
Selamat datang di **Sistem Peminjaman Lab**.  
Silakan pilih menu di sidebar untuk:
- 📅 Pengajuan Peminjaman
- 📊 Melihat Daftar Peminjaman
- ⚙️ Akses Dashboard Admin
"""
)

# Bisa tambahkan identitas kampus/lab
st.info("🔒 Pastikan login sebagai admin untuk mengakses Dashboard.")


# from supabase import create_client, Client
# import os

# load_dotenv()

# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_KEY")

# supabase: Client = create_client(url, key)
