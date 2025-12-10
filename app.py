import streamlit as st
import pandas as pd
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

st.set_page_config(page_title="Monitoring Progres Pustakawan", layout="wide")
st.title("📄 Monitoring Progres Dokumen Pustakawan")

# --- Google Sheet Connection ----------------------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]   # Ambil dari Streamlit Secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- Baca Google Sheet -----------------------------------------------------
sheet = client.open("Data Pegawai").worksheet("Sheet1")  
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Konversi tanggal otomatis (jika ada)
for col in ["Progress 1", "Progress 2"]:
    if col in df.columns:
        df[col] = df[col].astype(str)

# Pilih nama
selected_name = st.selectbox("Pilih Nama", df["Nama"].tolist())
row = df[df["Nama"] == selected_name].iloc[0]

# --- Menampilkan Detail -------------------------------------------------
st.subheader("📌 Detail Dokumen")
st.write(f"**Nama:** {row['Nama']}")
st.write(f"**NIP:** {row['NIP']}")
st.write(f"**Unit Kerja:** {row['Unit Kerja']}")
st.write(f"**Jabatan Lama:** {row['Jabatan Lama']}")
st.write(f"**Jabatan Baru:** {row['Jabatan Baru']}")
st.write(f"**Jenis:** {row['Jenis']}")

# --- Status Terakhir ------------------------------------------------------
if row['Keterangan'] == True or str(row['Keterangan']).lower() == 'true':
    status_terakhir = "Selesai ✔️"
elif pd.notna(row["Progress 2"]) and row["Progress 2"].strip() != "":
    status_terakhir = "Diterima Biro SDM"
elif pd.notna(row["Progress 1"]) and row["Progress 1"].strip() != "":
    status_terakhir = "Proses TTE Pimpinan"
else:
    status_terakhir = "Menunggu Disposisi Sekretaris Ditjen Pendis"

st.subheader("📍 Status Terakhir")
st.info(status_terakhir)

# --- Timeline Shopee Style -----------------------------------------------
st.subheader("🕒 Timeline Progres (Style Shopee)")

def timeline_item(title, date_text, active=False):
    color = "#10A37F" if active else "#BBBBBB"
    dot = f"<div style='width:14px;height:14px;border-radius:50%;background:{color};display:inline-block;margin-right:10px;'></div>"
    text = f"<span style='font-size:16px;font-weight:600'>{title}</span>"
    date = f"<div style='font-size:13px;color:#666;margin-left:24px'>{date_text}</div>" if date_text else ""
    st.markdown(dot + text + date, unsafe_allow_html=True)

# Timeline order seperti Shopee
timeline_item("Menunggu Disposisi Sekretaris Ditjen Pendis", "", active=(status_terakhir.startswith("Menunggu")))
timeline_item("Proses TTE oleh Pimpinan", row['Progress 1'], active=("TTE" in status_terakhir))
timeline_item("Diterima Biro SDM", row['Progress 2'], active=("Biro SDM" in status_terakhir))
timeline_item("Selesai", "✔️", active=("Selesai" in status_terakhir))
