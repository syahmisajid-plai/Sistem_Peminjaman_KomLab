import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime

# Load environment
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# --- CSS Styling ---
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

    # --- Pilihan tanggal ---
    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    next_7_days_str = [d.isoformat() for d in next_7_days]

    options = ["Pilih tanggal"] + next_7_days_str + ["Semua 7 hari ke depan"]

    # Set default value ke "Semua 7 hari ke depan"
    default_option = "Semua 7 hari ke depan"
    selected_option = st.selectbox(
        ":blue[Pilih tanggal:]", options, index=options.index(default_option)
    )

    # Tentukan tanggal yang akan digunakan di query
    if selected_option == "Semua 7 hari ke depan":
        selected_dates = next_7_days_str
    elif selected_option in next_7_days_str:
        selected_dates = [selected_option]
    else:
        selected_dates = []

    # --- Ambil data loans ---
    loans = None  # inisialisasi agar selalu ada
    if selected_dates:
        loans = (
            supabase.table("loans")
            .select(
                "id, loan_date, status, user_id, computer_id, "
                "computers(name, location), users(name, nim)"
            )
            .in_("loan_date", selected_dates)
            .order("loan_date", desc=False)
            .execute()
        )

    # --- Tampilkan data loans ---
    if loans and loans.data:
        # Tambahkan sorting: pending dulu
        sorted_loans = sorted(
            loans.data, key=lambda x: 0 if x["status"].lower() == "pending" else 1
        )

        for loan in sorted_loans:
            status = loan["status"].lower()
            if status == "pending":
                status_color = "#FFD700"
            elif status == "approved":
                status_color = "#00D300"
            elif status == "rejected":
                status_color = "#8B0000"
            else:
                status_color = "#FFFFFF"

            st.markdown(
                f"""
                <div style="
                    border-radius: 10px; 
                    padding: 10px; 
                    margin-bottom: 5px; 
                    background-color: #1E1E2F; 
                    color: white;
                ">
                    📅 {loan['loan_date']} | 💻 {loan['computers']['name']} | 🏫 {loan['computers']['location']} 
                    | 👤 {loan['users']['name']} ({loan['users']['nim']}) 
                    | <span style='color:{status_color}; font-weight:bold'>Status: {loan['status']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ ACC", key=f"acc_{loan['id']}"):
                    # --- Update status loan ---
                    supabase.table("loans").update({"status": "approved"}).eq(
                        "id", loan["id"]
                    ).execute()
                    st.success(f"Peminjaman {loan['computers']['name']} disetujui!")

                    # --- Update computer_schedule: available = False + simpan user_id ---
                    loan_date_clean = None
                    if loan.get("loan_date"):
                        try:
                            loan_date_clean = (
                                datetime.fromisoformat(str(loan["loan_date"]))
                                .date()
                                .isoformat()
                            )
                        except Exception:
                            loan_date_clean = str(loan["loan_date"])

                    supabase.table("computer_schedule").update(
                        {"available": False, "user_id": loan["user_id"]}
                    ).eq("computer_id", loan["computer_id"]).eq(
                        "loan_date", loan_date_clean
                    ).execute()

                    st.session_state["last_action"] = loan["id"]

            with col2:
                if st.button("❌ Tolak", key=f"reject_{loan['id']}"):
                    supabase.table("loans").update({"status": "rejected"}).eq(
                        "id", loan["id"]
                    ).execute()
                    st.warning(f"Peminjaman {loan['computers']['name']} ditolak.")
    else:
        st.info("⚠️ Harap pilih tanggal atau tidak ada data peminjaman.")
