import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# -----------------------------------------------------------
# KONFIGURASI HALAMAN
# -----------------------------------------------------------
st.set_page_config(
    page_title="Monitoring Progres Usul Jabatan Fungsional Pustakawan",
    layout="centered"
)

# -----------------------------------------------------------
# HEADER KEMENAG (TANPA LOGO, HANYA TEKS)
# -----------------------------------------------------------
st.markdown("""
    <div style="text-align:left; margin-left:0px;">
        <p style="margin:0; font-size:20px; font-weight:bold;">
            KEMENTERIAN AGAMA REPUBLIK INDONESIA
        </p>
        <p style="margin:0; font-size:18px;">
            DIREKTORAT JENDERAL PENDIDIKAN ISLAM
        </p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# TITLE UTAMA
# -----------------------------------------------------------
st.markdown("""
    <div style="text-align:center; margin-top:40px;">
        <h2 style="color:#2c3e50;">📄 Monitoring Progres Dokumen Pustakawan</h2>
        <p style="font-size:16px; color:#34495e; margin-top:20px;">
            Masukkan <b>NIP</b> Anda untuk melakukan pencarian progres <br>
            <strong>Monitoring Usul Dokumen JF Pustakawan</strong>.
        </p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# GOOGLE SHEET CONNECTION
# -----------------------------------------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

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
# INPUT PENCARIAN
# -----------------------------------------------------------
col1, col2, col3 = st.columns([1,3,1])
with col2:
    nip_input = st.text_input("Contoh: 198701012000011001", label_visibility="collapsed")
    btn = st.button("🔍 Lacak")

st.markdown("<hr>", unsafe_allow_html=True)

if not btn:
    st.stop()

# -----------------------------------------------------------
# VALIDASI NIP
# -----------------------------------------------------------
nip_input = nip_input.strip()

if not nip_input.isdigit() or len(nip_input) != 18:
    st.error("⚠️ NIP harus 18 digit numerik.")
    st.stop()

# -----------------------------------------------------------
# CEK DATA
# -----------------------------------------------------------
hasil = df[df["NIP"].astype(str).str.strip() == nip_input]

if hasil.empty:
    st.warning("❗ Tidak ditemukan data usul untuk NIP ini. Silakan cek kembali atau konfirmasi ke Satker Pengusul.")
    st.stop()

row = hasil.iloc[0]

# -----------------------------------------------------------
# DETAIL DATA
# -----------------------------------------------------------
st.subheader("📌 Hasil Pencarian:")
st.write(f"**Nama:** {row['Nama']}")
st.write(f"**NIP:** {row['NIP']}")
st.write(f"**Unit Kerja:** {row['Unit Kerja']}")
st.write(f"**Jabatan Lama:** {row['Jabatan Lama']}")
st.write(f"**Jabatan Baru:** {row['Jabatan Baru']}")
st.write(f"**Jenis:** {row['Jenis']}")

# -----------------------------------------------------------
# HITUNG STEP PROGRES
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
# TEKS SETIAP STEP (OTOMATIS SESUAI PROGRES)
# -----------------------------------------------------------
# Step 1
if progress_step >= 1:
    step1_text = "Disposisi dan Verifikasi Validasi Berkas"
else:
    step1_text = "Menunggu Disposisi Sekretaris Ditjen Pendis dan Proses Verifikasi Validasi Berkas"

# Step 2
if progress_step >= 2:
    step2_text = "Proses TTE Surat Rekomendasi oleh pimpinan"
else:
    step2_text = "Proses TTE Surat Rekomendasi oleh pimpinan"

# Step 3
if progress_step >= 3:
    step3_text = "Berkas sudah diterima oleh Biro SDM - Setjen Kemenag"
else:
    step3_text = "Menunggu berkas diterima Biro SDM"

# Step 4
if progress_step == 4:
    step4_text = "Semua proses selesai oleh Subtim Kepegawaian - Tim OKH"
else:
    step4_text = "Menunggu seluruh proses selesai"

# -----------------------------------------------------------
# STYLE CARD
# -----------------------------------------------------------
def card_style(step):
    if progress_step >= step:
        return "background-color:#d4edda; border-left:6px solid #28a745;"
    else:
        return "background-color:#fff3cd; border-left:6px solid #ffc107;"

# -----------------------------------------------------------
# TIMELINE
# -----------------------------------------------------------
st.markdown("### 🧭 Timeline Proses Dokumen")
st.markdown("---")

# Step 1 (tanpa tanggal)
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

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown("""
    <div style="text-align: center; font-size: 13px; color: gray; margin-top:25px;">
        Diberdayakan oleh: <b>Tim Kerja OKH - Sekretariat Direktorat Jenderal Pendidikan Islam</b>
    </div>
""", unsafe_allow_html=True)
