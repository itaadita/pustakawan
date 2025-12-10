import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# -----------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------
st.set_page_config(page_title="Monitoring Progres Pustakawan", layout="centered")
st.title("📄 Monitoring Progres Dokumen Pustakawan")

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
st.markdown("""
### 🔍 Cari Progres Dokumen
Masukkan **NIP Anda** untuk melihat status terbaru.
""")

nip_input = st.text_input("Masukkan NIP (18 digit)", max_chars=18)
btn = st.button("🔎 Cari")

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
    st.warning("❗ Data tidak ditemukan. Usulan belum masuk atau NIP salah.")
    st.stop()

# Ambil baris pertama
row = hasil.iloc[0]

# -----------------------------------------------------------
# HALAMAN 2 — DETAIL DATA
# -----------------------------------------------------------
st.success("Data ditemukan! Berikut detailnya:")

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
# TIMELINE SHOPEE
# -----------------------------------------------------------
st.subheader("🕒 Timeline Progres (Style Shopee)")

def timeline_item(title, date_text, active=False):
    color = "#10A37F" if active else "#BBBBBB"
    dot = f"<div style='width:14px;height:14px;border-radius:50%;background:{color};display:inline-block;margin-right:10px;'></div>"
    text = f"<span style='font-size:16px;font-weight:600'>{title}</span>"
    date = f"<div style='font-size:13px;color:#666;margin-left:24px'>{date_text}</div>" if date_text else ""
    st.markdown(dot + text + date, unsafe_allow_html=True)

timeline_item("Menunggu Disposisi Sekretaris Ditjen Pendis", "", active=(status_terakhir.startswith("Menunggu")))
timeline_item("Proses TTE oleh Pimpinan", row['Progress 1'], active=("TTE" in status_terakhir))
timeline_item("Diterima Biro SDM", row['Progress 2'], active=("Biro SDM" in status_terakhir))
timeline_item("Selesai", "✔️", active=("Selesai" in status_terakhir))
