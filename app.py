import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# -----------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------
st.set_page_config(page_title="Monitoring Progres Pustakawan", layout="centered")

st.markdown("""
<div style="text-align:center; margin-top:20px;">
    <h2 style="color:#2c3e50;">📄 Monitoring Progres Dokumen Pustakawan</h2>
    <p style="font-size:16px; color:#34495e;">
        Masukkan <b>NIP</b> untuk melihat progres dokumen penilaian jabatan fungsional pustakawan.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# GOOGLE SHEET CONNECTION
# -----------------------------------------------------------
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client = gspread.authorize(creds)

# Buka Spreadsheet
sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1giPSg_pVhAp-2UlLtBDGaO-DiCGZCxDvOmG7Fm09am0/edit?usp=sharing"
)

# Buka TAB
worksheet = sheet.worksheet("datapegawai")
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# -----------------------------------------------------------
# DASHBOARD AWAL — INPUT NIP
# -----------------------------------------------------------
col1, col2, col3 = st.columns([1,3,1])
with col2:
    nip_input = st.text_input("Contoh: 198765432019032001", label_visibility="collapsed")
    btn = st.button("🔍 Lacak")

st.markdown("<hr>", unsafe_allow_html=True)

# Jika belum menekan tombol → berhenti di sini
if not btn:
    st.stop()

# -----------------------------------------------------------
# VALIDASI INPUT
# -----------------------------------------------------------
nip_input = nip_input.strip()

if not nip_input.isdigit() or len(nip_input) != 18:
    st.error("⚠️ NIP harus 18 digit numerik.")
    st.stop()

# -----------------------------------------------------------
# CEK DATA BERDASARKAN NIP
# -----------------------------------------------------------
hasil = df[df["NIP"].astype(str).str.strip() == nip_input]

if hasil.empty:
    st.warning("❗ Data tidak ditemukan.")
    st.stop()

# Ambil baris pertama
row = hasil.iloc[0]

# -----------------------------------------------------------
# DETAIL DATA
# -----------------------------------------------------------
st.subheader("📌 Detail Dokumen")
st.write(f"**Nama:** {row['Nama']}")
st.write(f"**NIP:** {row['NIP']}")
st.write(f"**Unit Kerja:** {row['Unit Kerja']}")
st.write(f"**Jabatan Lama:** {row['Jabatan Lama']}")
st.write(f"**Jabatan Baru:** {row['Jabatan Baru']}")
st.write(f"**Jenis:** {row['Jenis']}")

# -----------------------------------------------------------
# LOGIKA STATUS TERAKHIR
# -----------------------------------------------------------
if str(row['Keterangan']).lower() == 'true':
    status_terakhir = "Selesai ✔️"
elif row["Progress 2"].strip():
    status_terakhir = "Diterima Biro SDM"
elif row["Progress 1"].strip():
    status_terakhir = "Proses TTE Pimpinan"
else:
    status_terakhir = "Menunggu Disposisi Sekretaris Ditjen Pendis"

st.subheader("📍 Status Terakhir")
st.info(status_terakhir)

# -----------------------------------------------------------
# TIMELINE STYLE SHOPEE (VERSI SURAT MUTASI)
# -----------------------------------------------------------

st.markdown("""
<style>
.timeline {
    border-left: 3px solid #3498db;
    margin-left: 20px;
    padding-left: 20px;
}
.entry {
    margin-bottom: 18px;
    position: relative;
}
.entry:before {
    content: "●";
    position: absolute;
    left: -23px;
    font-size: 18px;
    color: #3498db;
}
.done:before {
    color: #2ecc71;
}
</style>
""", unsafe_allow_html=True)

st.subheader("🕒 Timeline Proses Dokumen")

def add_step(step_no, title, date_text, active=False):
    status_class = "done" if active else "progress"
    emoji = "✅" if active else "⏳"

    html = (
        f"<div class='entry {status_class}'>"
        f"<b>Step {step_no}:</b> {title} {emoji}<br>"
        f"📅 {date_text if date_text else '-'}"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

# Step 1
add_step(
    1,
    "Menunggu Disposisi Sekretaris Ditjen Pendis",
    "-",
    active=status_terakhir.startswith("Menunggu")
)

# Step 2
add_step(
    2,
    "Proses TTE oleh Pimpinan",
    row['Progress 1'],
    active=("TTE" in status_terakhir)
)

# Step 3
add_step(
    3,
    "Diterima Biro SDM",
    row['Progress 2'],
    active=("Biro SDM" in status_terakhir)
)

# Step 4
add_step(
    4,
    "Selesai",
    "✔️",
    active=("Selesai" in status_terakhir)
)
