import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

from datetime import date, timedelta

# Load environment
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# CSS Styling
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
        background-color: #A3E635;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚙️ Admin Dashboard")
st.subheader("🔑 Login Admin")

# --- SESSION STATE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.admin_name = ""

# --- LOGIN FORM ---
if not st.session_state.logged_in:
    name = st.text_input(":blue[Nama Admin:]")
    password = st.text_input(":blue[Password:]", type="password")

    if st.button("Login"):
        if name and password:
            check = supabase.rpc(
                "check_admin_password", {"p_name": name, "p_password": password}
            ).execute()

            # cek list dan valid
            if check.data and check.data["valid"]:
                st.session_state.logged_in = True
                st.session_state.admin_name = check.data["name"]
            else:
                st.error("❌ Password salah.")
        else:
            st.warning("⚠️ Harap isi nama admin dan password.")

# --- DASHBOARD ---
else:
    st.success(f"✅ Login sebagai {st.session_state.admin_name}")

    # Pilih tanggal tunggal
    selected_date = st.date_input(
        ":blue[Pilih tanggal:]",
        value=date.today(),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=365),
    )

    # Konversi ke string ISO
    selected_date_str = selected_date.isoformat()

    # Ambil data loans + computers + users sesuai tanggal yang dipilih
    loans = (
        supabase.table("loans")
        .select(
            "id, loan_date, status, user_id, computer_id, "
            "computers(name, location), users(name, nim)"
        )
        .eq("loan_date", selected_date_str)  # hanya tanggal yang dipilih
        .order("loan_date", desc=False)
        .execute()
    )

    if loans.data:
        for loan in loans.data:
            # Tentukan warna status
            status = loan["status"].lower()
            if status == "pending":
                status_color = "#FFD700"  # kuning
            elif status == "approved":
                status_color = "#00D300"  # hijau
            elif status == "rejected":
                status_color = "#8B0000"  # merah
            else:
                status_color = "#FFFFFF"  # default putih

            st.markdown(
                f"""
                <div style="
                    border-radius: 10px; 
                    padding: 10px; 
                    margin-bottom: 5px; 
                    background-color: #1E1E2F; 
                    color: white;
                ">
                    📅 {loan['loan_date']} | 💻 {loan['computers']['name']} 
                    | 👤 {loan['users']['name']} ({loan['users']['nim']}) 
                    | <span style='color:{status_color}; font-weight:bold'>Status: {loan['status']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ ACC", key=f"acc_{loan['id']}"):
                    st.write("DEBUG tombol ACC ditekan:", loan["id"])

                    # --- Update status loan ---
                    resp = (
                        supabase.table("loans")
                        .update({"status": "approved"})
                        .eq("id", loan["id"])
                        .execute()
                    )
                    st.success(f"Peminjaman {loan['computers']['name']} disetujui!")

                    # --- Update computer_schedule: available = False + simpan user_id ---
                    from datetime import datetime

                    loan_date_clean = None
                    if loan.get("loan_date"):
                        try:
                            loan_date_clean = (
                                datetime.fromisoformat(str(loan["loan_date"]))
                                .date()
                                .isoformat()
                            )
                        except Exception:
                            loan_date_clean = str(loan["loan_date"])  # fallback

                    resp2 = (
                        supabase.table("computer_schedule")
                        .update({"available": False, "user_id": loan["user_id"]})
                        .eq("computer_id", loan["computer_id"])
                        .eq("loan_date", loan_date_clean)
                        .execute()
                    )
                    # st.write("DEBUG update computer_schedule:", resp2)

                    # --- Update session state agar UI refresh ---
                    st.session_state["last_action"] = loan["id"]

            with col2:
                if st.button("❌ Tolak", key=f"reject_{loan['id']}"):
                    supabase.table("loans").update({"status": "rejected"}).eq(
                        "id", loan["id"]
                    ).execute()
                    st.warning(f"Peminjaman {loan['computers']['name']} ditolak.")
    else:
        st.info(f"ℹ️ Tidak ada data peminjaman untuk {selected_date_str}.")
