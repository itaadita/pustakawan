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

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1giPSg_pVhAp-2UlLtBDGaO-DiCGZCxDvOmG7Fm09am0/edit?usp=sharing"
)

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
# TENTUKAN PROGRESS STEP OTOMATIS
# -----------------------------------------------------------

if str(row["Keterangan"]).lower() == "true":
    progress_step = 4
elif str(row["Progress 2"]).strip():
    progress_step = 3
elif str(row["Progress 1"]).strip():
    progress_step = 2
else:
    progress_step = 1

# -----------------------------------------------------------
# LOGIKA TEKS SETIAP STEP
# -----------------------------------------------------------
# Step 1
if progress_step >= 1:
    step1_text = "Disposisi Setditjen Pendis dan Verifikasi Validasi Berkas sudah selesai"
else:
    step1_text = "Menunggu Disposisi Sekretaris Ditjen Pendis dan Proses Verifikasi Validasi Berkas"

# Step 2
if progress_step >= 2:
    step2_text = "Surat Rekomendasi sudah selesai di TTE oleh pimpinan"
else:
    step2_text = "Proses TTE Surat Rekomendasi oleh pimpinan"

# Step 3
if progress_step >= 3:
    step3_text = "Surat Rekomendasi dan Berkas usul sudah diterima oleh Biro SDM - Setjen Kementerian Agama"
else:
    step3_text = "Menunggu Berkas diterima oleh Biro SDM"

# Step 4
if progress_step == 4:
    step4_text = "Semua Proses sudah selesai oleh Subtim Kepegawaian - TIM OKH Ditjen Pendis"
else:
    step4_text = "Menunggu seluruh proses selesai"

# -----------------------------------------------------------
# STYLE CARD ELEGAN (HIJAU / KUNING)
# -----------------------------------------------------------

def card_style(step):
    if progress_step >= step:
        return "background-color:#d4edda; border-left:6px solid #28a745;"   # DONE
    else:
        return "background-color:#fff3cd; border-left:6px solid #ffc107;"   # PROGRESS

# -----------------------------------------------------------
# TAMPILKAN TIMELINE
# -----------------------------------------------------------
st.subheader("🕒 Timeline Proses Dokumen")
st.markdown("---")

# Step 1
st.markdown(f"""
<div style="{card_style(1)} padding:15px; margin-bottom:10px; border-radius:10px;">
<b>Step 1:</b><br>{step1_text}
</div>
""", unsafe_allow_html=True)

# Step 2
st.markdown(f"""
<div style="{card_style(2)} padding:15px; margin-bottom:10px; border-radius:10px;">
<b>Step 2:</b><br>{step2_text}<br>
📅 {row["Progress 1"] if row["Progress 1"] else "-"}
</div>
""", unsafe_allow_html=True)

# Step 3
st.markdown(f"""
<div style="{card_style(3)} padding:15px; margin-bottom:10px; border-radius:10px;">
<b>Step 3:</b><br>{step3_text}<br>
📅 {row["Progress 2"] if row["Progress 2"] else "-"}
</div>
""", unsafe_allow_html=True)

# Step 4
st.markdown(f"""
<div style="{card_style(4)} padding:15px; margin-bottom:10px; border-radius:10px;">
<b>Step 4:</b><br>{step4_text}<br>
📅 {"✔️" if progress_step == 4 else "-"}
</div>
""", unsafe_allow_html=True)
