import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# CSS
st.markdown(
    """
    <style>
    .stApp { background-color: #0A0F29; color: #FFD700; margin: 0 auto;}
    section[data-testid="stSidebar"] { background-color: #FFFFFF; color: #000000; }
    section[data-testid="stSidebar"] * { color: #000000 !important; }
    .stButton>button {
        color: #065F46;
        background-color: #A3E635;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.subheader("📑 Cek Peminjaman Komputer")

nim = st.text_input(":blue[Masukkan NIM:]")
password = st.text_input(":blue[Password:]", type="password")

if st.button("Lihat Status Peminjaman"):
    if nim and password:
        # Cek user
        check = supabase.rpc(
            "check_user_password", {"p_nim": nim, "p_password": password}
        ).execute()

        if check.data and check.data["valid"]:
            user_id = check.data["id"]
            st.success("✅ Login berhasil!")

            # Ambil data peminjaman dari loans + users + computers
            loans = (
                supabase.table("loans")
                .select(
                    "loan_date, status, "
                    "computer_id, "
                    "computers(name, location),"
                    "users(name, nim)"
                )
                .eq("user_id", user_id)
                .order("loan_date", desc=True)
                .execute()
            )

            if loans.data:
                st.subheader("📋 Riwayat Peminjaman Anda")
                df_loans = pd.DataFrame(loans.data)

                # Flatten nested dicts
                df_loans["Nama Komputer"] = df_loans["computers"].apply(
                    lambda x: x["name"]
                )
                df_loans["Nama Lab"] = df_loans["computers"].apply(
                    lambda x: x["location"]
                )
                df_loans["Nama User"] = df_loans["users"].apply(lambda x: x["name"])
                df_loans["NIM"] = df_loans["users"].apply(lambda x: x["nim"])

                # Rename kolom
                df_loans = df_loans.rename(
                    columns={"loan_date": "Tanggal", "status": "Status"}
                )

                def highlight_status(val):
                    if val == "approved":
                        color = "lightgreen"
                    elif val == "pending":
                        color = "yellow"
                    else:
                        color = "lightcoral"
                    return f"background-color: {color}"

                styled_df = df_loans[
                    [
                        "NIM",
                        "Nama User",
                        "Nama Lab",
                        "Nama Komputer",
                        "Tanggal",
                        "Status",
                    ]
                ].style.applymap(highlight_status, subset=["Status"])
                st.dataframe(styled_df, use_container_width=True)

            else:
                st.info("ℹ️ Belum ada riwayat peminjaman.")
        else:
            st.error("❌ Login gagal. NIM atau password salah.")
    else:
        st.warning("⚠️ Harap isi NIM dan Password dulu.")
