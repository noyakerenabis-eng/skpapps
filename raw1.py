import streamlit as st
import pandas as pd
import fitz 

from io import StringIO
from io import BytesIO

from datetime import datetime
from datetime import timedelta

from PIL import Image as PILImage

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Aplikasi Pembuat SKP Karantina Tumbuhan Riau",
    layout="wide"
)

HEADER_IMAGE = "Header.png"  # Ganti dengan path gambar header Anda
STEMPEL_PATH = "Stempel.png"

# ==================================================
# STYLE PDF
# ==================================================

styles = getSampleStyleSheet()

style_wrap = ParagraphStyle(
    name="WrapStyle",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10
)

style_judul = ParagraphStyle(
    "JudulLaporan",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    alignment=1,
    spaceAfter=10
)

style_sub_judul = ParagraphStyle(
    "SubJudul",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=14,
    alignment=1
)

# ==================================================
# BACA FILE KARANTINA
# ==================================================

def baca_laporan(file):

    isi = file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    baris = isi.splitlines()

    header_idx = None

    for i, line in enumerate(baris):

        if line.startswith('No.,') or line.startswith('No.,"'):

            header_idx = i
            break

    if header_idx is None:

        raise Exception(
            "Header tabel tidak ditemukan"
        )

    csv_bersih = "\n".join(
        baris[header_idx:]
    )

    df = pd.read_csv(
        StringIO(csv_bersih)
    )

    return df
    
def tambah_stempel_dekat_ketua_tim(pdf_buffer, stempel_path):

    pdf_buffer.seek(0)

    doc = fitz.open(
        stream=pdf_buffer.read(),
        filetype="pdf"
    )

    halaman = doc[-1]

    hasil_cari = halaman.search_for(
        "Ketua Tim"
    )

    if not hasil_cari:

        pdf_buffer.seek(0)
        return pdf_buffer

    posisi = hasil_cari[-1]

    x = posisi.x0 - 45
    y = posisi.y1 - 10

    ukuran = 85

    kotak_stempel = fitz.Rect(
        x,
        y,
        x + ukuran,
        y + ukuran
    )

    halaman.insert_image(
        kotak_stempel,
        filename=stempel_path,
        overlay=True
    )

    hasil_buffer = BytesIO()

    doc.save(
        hasil_buffer
    )

    doc.close()

    hasil_buffer.seek(0)

    return hasil_buffer
# ==================================================
# JUDUL
# ==================================================

st.title(
    "Generator Laporan Karantina"
)
st.warning(
    "Sebelum generate PDF, isi dulu data identitas dan informasi laporan melalui sidebar."
)

# ==================================================
# IDENTITAS
# ==================================================

st.sidebar.header(
    "Identitas Pegawai"
)
nama_lengkap_beserta_gelar = st.sidebar.text_input(
    "Nama Lengkap Beserta Gelar",
    value=""
)
pangkat = st.sidebar.text_input(
    "Pangkat/Golongan/TMT",
    value=""
)

jabatan = st.sidebar.text_input(
    "Jabatan",
    value="Analis Perkarantinaan Tumbuhan Ahli Pertama"
)

kata_jabatan = jabatan.split()

if len(kata_jabatan) >= 3:

    jabatan_ttd = (
        kata_jabatan[0][0]
        + kata_jabatan[1][0]
        + kata_jabatan[2][0]
        + " "
        + " ".join(kata_jabatan[3:])
    )

else:

    jabatan_ttd = jabatan

unit = st.sidebar.text_input(
    "Unit Kerja",
    value="Balai Karantina Hewan, Ikan dan Tumbuhan Riau"
)

dasar = st.sidebar.text_area(
    "Dasar Pelaksanaan",
    height=100
)

rhk = st.sidebar.text_input(
    "Rencana Hasil Kerja",
    value=""
)
ra = st.sidebar.text_input(
    "Rencana Aksi",
    value=""
)
iki = st.sidebar.text_input(
    "Indikator Kerja Individu",
    value=""
)

kolom_file, kolom_ttd = st.columns(2)

with kolom_file:

    st.subheader(
        "File Laporan"
    )

    file_penugasan = st.file_uploader(
        "Upload File Penugasan Periode Ini dan/ Sebelumnya (jika terdapat penugasan diluar periode)",
        type=["csv"],
        accept_multiple_files=True
    )

    file_pelepasan = st.file_uploader(
        "Upload File Pelepasan (maksimal 3 file)",
        type=["csv"],
        accept_multiple_files=True
    )

with kolom_ttd:

    st.subheader(
        "Tanda Tangan"
    )

    ttd_kiri = st.file_uploader(
        "TTD Ketua Tim",
        type=["png"]
    )
  
    ttd_kanan = st.file_uploader(
        "TTD Petugas",
        type=["png"]
    )


if file_pelepasan and len(file_pelepasan) > 3:

    st.error(
        "Maksimal 3 file pelepasan"
    )

    st.stop()

# ==================================================
# PROSES
# ==================================================

if file_penugasan and file_pelepasan:
    try:

        # ==========================================
        # BACA PENUGASAN
        # ==========================================
        list_df_penugasan = []
        
        for file in file_penugasan:
        
            df_tmp = baca_laporan(file)
        
            list_df_penugasan.append(df_tmp)
        
        df_penugasan = pd.concat(
            list_df_penugasan,
            ignore_index=True
        )
       
        if "No Permohonan" not in df_penugasan.columns:

            st.error(
               "Kolom No Permohonan tidak ditemukan"
            )
            st.stop()
        if "Jenis Tugas" not in df_penugasan.columns:
            st.error(
                 "Kolom Jenis Tugas tidak ditemukan"
             )

            st.stop()
        # ==========================================
        # NAMA DAN NIP OTOMATIS
        # ==========================================
        
        nama_petugas = str(
              df_penugasan.iloc[0]["Nama Petugas"]
        )

        nip_petugas = str(
            df_penugasan.iloc[0]["NIP Petugas"]
        )

        nip_petugas = (
            nip_petugas
            .replace('="', '')
            .replace('"', '')
        )

        st.success(
            f"Petugas : {nama_petugas}"
        )
        # ==========================================
        # REKAP JENIS TUGAS
        # ==========================================
        
        rekap_jenis_tugas = (
            df_penugasan
            .dropna(subset=["No Permohonan"])
            .groupby("Jenis Tugas")["No Permohonan"]
            .nunique()
            .reset_index(name="Jumlah No Permohonan Unik")
        )
        
        st.subheader(
            "Rekap Jenis Tugas"
        )
        
        st.dataframe(
            rekap_jenis_tugas,
            use_container_width=True
        )
        
        jenis_tugas_opsi = sorted(
            df_penugasan["Jenis Tugas"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        
        jenis_tugas_dipilih = st.multiselect(
            "Pilih Jenis Tugas untuk Generate Dokumen",
            options=jenis_tugas_opsi,
            default=jenis_tugas_opsi
        )
        if not jenis_tugas_dipilih:

            st.warning(
                "Pilih minimal satu Jenis Tugas untuk generate dokumen"
            )
            st.stop()
        df_penugasan_terpilih = df_penugasan[
            df_penugasan["Jenis Tugas"]
            .astype(str)
            .isin(jenis_tugas_dipilih)
        ]
        
       
        # ==========================================
        # NOMOR DOKUMEN UNIK
        # ==========================================

        nomor_dokumen = (
            df_penugasan_terpilih["No Permohonan"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
       
        # ==========================================
        # BACA PELEPASAN
        # ==========================================

        list_df = []

        for file in file_pelepasan:

            df_tmp = baca_laporan(file)

            list_df.append(df_tmp)

        df_pelepasan = pd.concat(
            list_df,
            ignore_index=True
        )

        if "No. K.1.1" not in df_pelepasan.columns:

            st.error(
                "Kolom No. K.1.1 tidak ditemukan"
            )

            st.stop()

        # ==========================================
        # FILTER
        # ==========================================

        df_filter = df_pelepasan[
            df_pelepasan["No. K.1.1"]
            .astype(str)
            .isin(nomor_dokumen)
        ]
        with st.sidebar.expander(
            "Informasi Proses"
        ):

            st.metric(
                "Jenis Tugas Dipilih",
                len(jenis_tugas_dipilih)
            )
    
            st.metric(
                "Nomor Dokumen Unik",
                len(nomor_dokumen)
            )
    
            st.metric(
                "Baris Cocok",
                len(df_filter)
            )
       
        nomor_opsi = sorted(
            df_filter["No. K.1.1"]
            .astype(str)
            .unique()
            .tolist()
        )

        # ==========================================
        # PENGATURAN HASIL
        # ==========================================

        st.subheader(
            "Pengaturan Hasil Pemeriksaan"
        )

        semua_admin = st.checkbox(
            "Semua Administrasi = Lengkap, sah dan benar",
            value=True
        )

        semua_kesehatan = st.checkbox(
            "Semua Kesehatan = BEBAS OPTK",
            value=True
        )

        semua_kesimpulan = st.checkbox(
            "Semua Kesimpulan = PEMBEBASAN",
            value=True
        )

        admin_override = {}

        kesehatan_override = {}

        kesimpulan_override = {}

        # ==========================================
        # ADMINISTRASI
        # ==========================================

        if not semua_admin:

            st.subheader(
                "Pengecualian Administrasi"
            )

            for nomor in nomor_opsi:

                admin_override[nomor] = st.text_input(
                    f"Administrasi - {nomor}",
                    value="Lengkap, sah dan benar"
                )

        # ==========================================
        # KESEHATAN
        # ==========================================

        if not semua_kesehatan:

            st.subheader(
                "Pengecualian Kesehatan"
            )

            for nomor in nomor_opsi:

                kesehatan_override[nomor] = st.text_input(
                    f"Kesehatan - {nomor}",
                    value="BEBAS OPTK"
                )

        # ==========================================
        # KESIMPULAN
        # ==========================================

        if not semua_kesimpulan:

            st.subheader(
                "Pengecualian Kesimpulan"
            )

            for nomor in nomor_opsi:

                kesimpulan_override[nomor] = st.text_input(
                    f"Kesimpulan - {nomor}",
                    value="PEMBEBASAN"
                )

        # ==========================================
        # GENERATE DATAFRAME
        # ==========================================

        if st.button(
            "Generate PDF"
        ):

            hasil = []

            nomor_urut = 1

            for nomor, grup in df_filter.groupby(
                "No. K.1.1"
            ):

                tanggal = grup.iloc[0][
                    "Tgl Dokumen"
                ]

                satpel = grup.iloc[0][
                    "Satpel"
                ]

                nomor_dok_hasil = grup.iloc[0][
                    "Nomor Dokumen"
                ]

                nomor_permohonan = str(nomor)

                if "-T1." in nomor_permohonan:
                    tujuan = grup.iloc[0]["Tujuan"]

                elif "-T2." in nomor_permohonan:
                    tujuan = grup.iloc[0]["Asal"]

                elif "-T3." in nomor_permohonan:        
                    tujuan = grup.iloc[0]["Daerah Tujuan"]

                elif "-T4." in nomor_permohonan:
                    tujuan = grup.iloc[0]["Daerah Asal"]

                else:
                    tujuan = "-"

                komoditas = ", ".join(
                    grup["Komoditas"]
                    .dropna()
                    .astype(str)
                    .unique()
                )

                nomor_seri = ", ".join(
                    grup["Nomor Seri"]
                    .dropna()
                    .astype(str)
                    .unique()
                )

                administrasi = (
                    "Lengkap, sah dan benar"
                    if semua_admin
                    else admin_override.get(
                        nomor,
                        "Lengkap, sah dan benar"
                    )
                )

                kesehatan = (
                    "BEBAS OPTK"
                    if semua_kesehatan
                    else kesehatan_override.get(
                        nomor,
                        "BEBAS OPTK"
                    )
                )

                kesimpulan = (
                    "PEMBEBASAN"
                    if semua_kesimpulan
                    else kesimpulan_override.get(
                        nomor,
                        "PEMBEBASAN"
                    )
                )

                hasil.append([
                    nomor_urut,
                    tanggal,
                    satpel,
                    nomor,
                    nomor_dok_hasil,
                    komoditas,
                    tujuan,
                    nomor_seri,
                    administrasi,
                    kesehatan,
                    kesimpulan
                ])

                nomor_urut += 1

            df_hasil = pd.DataFrame(
                hasil,
                columns=[
                    "No.",
                    "Tgl Dokumen",
                    "Satpel",
                    "K.1.1",
                    "Nomor Dokumen",
                    "Komoditas",
                    "Tujuan",
                    "Nomor Seri",
                    "Administrasi",
                    "Kesehatan",
                    "Kesimpulan"
                ]
            )
            df_hasil["Tgl Dokumen"] = pd.to_datetime(
                df_hasil["Tgl Dokumen"]
            )
            df_hasil = df_hasil.sort_values(
                by="Tgl Dokumen",
                ascending=True
            ).reset_index(drop=True)

            df_hasil["No."] = range(
                1,
                len(df_hasil) + 1
            )

            st.success(
                f"Berhasil membuat {len(df_hasil)} data laporan"
            )

            st.dataframe(
                df_hasil,
                use_container_width=True
            )
                        # ==========================================
            # DATA UNTUK PDF
            # ==========================================

            rows = df_hasil.values.tolist()

            # ==========================================
            # PERIODE
            # ==========================================

            # Ambil range tanggal dari tabel hasil
            tanggal_min = df_hasil["Tgl Dokumen"].min()
            tahun = tanggal_min.year
            bulan = tanggal_min.month

            if tanggal_min.day < 16:
                # mundur satu bulan jika ada dokumen sebelum tanggal 16
                if bulan == 1:
                    bulan = 12
                    tahun -= 1
                else:
                    bulan -= 1

            # tanggal awal = 16 bulan referensi
            tanggal_awal = datetime(tahun, bulan, 16)

            # tanggal akhir = 15 bulan berikutnya
            if bulan == 12:
                tanggal_akhir = datetime(tahun+1, 1, 15)
            else:
                tanggal_akhir = datetime(tahun, bulan+1, 15)

            bulan_nama = {
                1:"Januari", 2:"Februari", 3:"Maret", 4:"April",
                5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus",
                9:"September", 10:"Oktober", 11:"November", 12:"Desember"
            }

            waktu_pelaksanaan = (
                f"{tanggal_awal.day} {bulan_nama[tanggal_awal.month]} {tanggal_awal.year} "
                f"s.d. {tanggal_akhir.day} {bulan_nama[tanggal_akhir.month]} {tanggal_akhir.year}"
            )

            bulan = {
                1:"Januari",
                2:"Februari",
                3:"Maret",
                4:"April",
                5:"Mei",
                6:"Juni",
                7:"Juli",
                8:"Agustus",
                9:"September",
                10:"Oktober",
                11:"November",
                12:"Desember"
            }

            waktu_pelaksanaan = (
                f"{tanggal_awal.day} "
                f"{bulan[tanggal_awal.month]} "
                f"{tanggal_awal.year} s.d. "
                f"{tanggal_akhir.day} "
                f"{bulan[tanggal_akhir.month]} "
                f"{tanggal_akhir.year}"
            )

            # ==========================================
            # PDF
            # ==========================================

            buffer = BytesIO()

            pdf = SimpleDocTemplate(
                buffer,
                leftMargin=15,
                rightMargin=15,
                topMargin=15,
                bottomMargin=15
            )

            elements = []

            # ==========================================
            # HEADER
            # ==========================================

            try:

                header = Image(
                    HEADER_IMAGE,
                    width=520,
                    height=80
                )

                elements.append(
                    header
                )

            except:
                pass

            elements.append(
                Spacer(1, 10)
            )

            elements.append(
                Paragraph(
                    "LAPORAN PELAKSANAAN KEGIATAN KARANTINA TUMBUHAN",
                    style_judul
                )
            )

            # ==========================================
            # IDENTITAS
            # ==========================================

            data_identitas = [

                ["1.", "Identitas Pegawai", "", ""],

                ["", "a. Nama", ":", nama_petugas],

                ["", "b. NIP", ":", nip_petugas],

                [
                    "",
                    "c. Pangkat/golongan ruang/TMT",
                    ":",
                    pangkat
                ],

                [
                    "",
                    "d. Jabatan",
                    ":",
                    jabatan
                ],

                [
                    "",
                    "e. Unit Kerja",
                    ":",
                    unit
                ],

                [
                    "2.",
                    "Dasar Pelaksanaan",
                    ":",
                    dasar
                ],

                [
                    "3.",
                    "Rencana Hasil Kerja",
                    ":",
                    rhk
                ],
                [
                    "4.",
                    "Rencana Aksi",
                    ":",
                    ra
                ],
                [
                    "5.",
                    "Indikator Kinerja Individu",
                    ":",
                    iki
                ],
                [
                    "6.",
                    "Waktu Pelaksanaan",
                    ":",
                    waktu_pelaksanaan
                ]

            ]

            tabel_identitas = Table(
                data_identitas,
                colWidths=[
                    10,
                    140,
                    10,
                    340
                ]
            )

            tabel_identitas.setStyle(
                TableStyle([

                    ('FONTNAME',
                     (0,0),
                     (-1,-1),
                     'Helvetica'),

                    ('FONTSIZE',
                     (0,0),
                     (-1,-1),
                     9),

                    ('VALIGN',
                     (0,0),
                     (-1,-1),
                     'TOP'),

                    ('LEFTPADDING',
                     (0,0),
                     (-1,-1),
                     0),

                    ('RIGHTPADDING',
                     (0,0),
                     (-1,-1),
                     0),
                    ('TOPPADDING', 
                     (0,0), (-1,-1), 
                     0),
                    
                    ('BOTTOMPADDING', 
                     (0,0), (-1,-1), 
                     0),

                ])
            )

            elements.append(
                tabel_identitas
            )

            elements.append(
                Spacer(1,15)
            )

            # ==========================================
            # SUB JUDUL
            # ==========================================

            elements.append(
                Paragraph(
                    "DAFTAR KEGIATAN SEBAGAI HASIL PELAKSANAAN PEKERJAAN",
                    style_sub_judul
                )
            )

            elements.append(
                Spacer(1,5)
            )

            # ==========================================
            # HEADER TABEL
            # ==========================================

            data_tabel = [[

                Paragraph(
                    "<b>No</b>",
                    style_wrap
                ),

                Paragraph(
                    "<b>Waktu<br/>Pelaksanaan</b>",
                    style_wrap
                ),

                Paragraph(
                    "<b>Lokasi Kegiatan</b>",
                    style_wrap
                ),

                Paragraph(
                    "<b>Nomor Dokumen</b>",
                    style_wrap
                ),

                Paragraph(
                    "<b>Hasil Kegiatan</b>",
                    style_wrap
                )

            ]]
            # ==========================================
            # ISI TABEL
            # ==========================================

            for row in rows:

                hasil = Table([

                    [
                        Paragraph("<b>Nomor Sertifikat</b>", style_wrap),
                        ":",
                        Paragraph(str(row[4]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Jenis MP</b>", style_wrap),
                        ":",
                        Paragraph(str(row[5]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Area Asal/Tujuan</b>", style_wrap),
                        ":",
                        Paragraph(str(row[6]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Nomor Seri Dokumen</b>", style_wrap),
                        ":",
                        Paragraph(str(row[7]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Hasil Administrasi</b>", style_wrap),
                        ":",
                        Paragraph(str(row[8]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Hasil Kesehatan</b>", style_wrap),
                        ":",
                        Paragraph(str(row[9]), style_wrap)
                    ],

                    [
                        Paragraph("<b>Kesimpulan</b>", style_wrap),
                        ":",
                        Paragraph(str(row[10]), style_wrap)
                    ]

                ],
                colWidths=[85,8,145])

                hasil.setStyle(
                    TableStyle([

                        ('VALIGN',
                         (0,0),
                         (-1,-1),
                         'TOP'),

                        ('LEFTPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('RIGHTPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('TOPPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('BOTTOMPADDING',
                         (0,0),
                         (-1,-1),
                         0)

                    ])
                )

                data_tabel.append([

                    Paragraph(
                        str(row[0]),
                        style_wrap
                    ),

                    Paragraph(
                        str(row[1])[:10],
                        style_wrap
                    ),

                    Paragraph(
                        str(row[2]),
                        style_wrap
                    ),

                    Paragraph(
                        str(row[3]),
                        style_wrap
                    ),

                    hasil

                ])

            # ==========================================
            # TOTAL
            # ==========================================

            data_tabel.append([

                Paragraph(
                    "<b>Jumlah Sertifikat</b>",
                    style_wrap
                ),

                "",
                "",
                "",

                Paragraph(
                    f"<b>{len(rows)}</b>",
                    style_wrap
                )

            ])

            # ==========================================
            # TABEL UTAMA
            # ==========================================

            tabel = Table(
                data_tabel,
                colWidths=[
                    28,
                    65,
                    85,
                    80,
                    275
                ]
            )

            tabel.setStyle(
                TableStyle([

                    ('GRID',
                     (0,0),
                     (-1,-1),
                     0.5,
                     colors.black),

                    ('BACKGROUND',
                     (0,0),
                     (-1,0),
                     colors.HexColor("#E6E6E6")),

                    ('FONTNAME',
                     (0,0),
                     (-1,0),
                     'Helvetica-Bold'),

                    ('ALIGN',
                     (0,0),
                     (-1,0),
                     'CENTER'),

                    ('VALIGN',
                     (0,0),
                     (-1,0),
                     'MIDDLE'),

                    ('VALIGN',
                     (0,1),
                     (-1,-1),
                     'TOP'),

                    ('SPAN',
                     (0,-1),
                     (3,-1)),

                    ('ALIGN',
                     (0,-1),
                     (3,-1),
                     'CENTER'),

                    ('FONTNAME',
                     (0,-1),
                     (-1,-1),
                     'Helvetica-Bold'),

                    ('BACKGROUND',
                     (0,-1),
                     (-1,-1),
                     colors.HexColor("#F2F2F2"))

                ])
            )

            elements.append(
                tabel
            )

            
            # ==========================================
            # TTD
            # ==========================================

            elements.append(
                Spacer(1,15)
            )
          
            if ttd_kiri and ttd_kanan:
            
                ttd_surya = Image(
                    ttd_kiri,
                    width=100,
                    height=40
                )
                ttd_petugas = Image(
                    ttd_kanan,
                    width=100,
                    height=40
                )
                            
                TTD_WIDTH = 565
            
                kiri = Table([
                    [
                        Paragraph(
                            "<br/>Mengetahui,<br/>Ketua Tim Karantina Tumbuhan",
                            style_wrap
                        )
                    ],
            
                    [Spacer(1,0)],
            
                    [ttd_surya],   # sekarang stempel + tanda tangan kiri jadi satu blok
            
                    [Spacer(1,0)],
            
                    [
                        Paragraph(
                            "<b>Surya Dharma, S.P.</b><br/>NIP. 197705152001121002",
                            style_wrap
                        )
                    ]
            
                ],
                colWidths=[TTD_WIDTH/2])

                kanan = Table([
                    [Spacer(1,10)],
                    [
                        Paragraph(
                            jabatan_ttd,
                            style_wrap
                        )
                    ],

                    [Spacer(1,3)],

                    [ttd_petugas],

                    [Spacer(1,0)],

                    [
                        Paragraph(
                            f"<b>{nama_lengkap_beserta_gelar}</b><br/>"
                            f"NIP. {nip_petugas}",
                            style_wrap
                        )
                    ]

                ],
                colWidths=[TTD_WIDTH/2])
                tanggal_kanan = Paragraph(
                    f"Pekanbaru, {datetime.now().day} "
                    f"{bulan[datetime.now().month]} "
                    f"{datetime.now().year}",
                    style_wrap
                )
                
                baris_tanggal = Table(
                    [["", "", tanggal_kanan]],
                    colWidths=[
                        150,
                        50,
                        200
                    ]
                )
                
                elements.append(
                    baris_tanggal
                )
                
                elements.append(
                    Spacer(1,0)
                )
                ttd_table = Table(
                    [["", kiri, "", kanan]],
                    colWidths=[
                        100,
                        200,
                        50,
                        200
                    ]
                )

                ttd_table.setStyle(
                    TableStyle([

                        ('VALIGN',
                         (0,0),
                         (-1,-1),
                         'TOP'),

                        ('LEFTPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('RIGHTPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('TOPPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('BOTTOMPADDING',
                         (0,0),
                         (-1,-1),
                         0),

                        ('ALIGN',
                         (0,0),
                         (-1,-1),
                         'CENTER')
                    ])
                )

                elements.append(
                    ttd_table
                )



            # ==========================================
            # BUILD PDF
            # ==========================================

            pdf.build(elements)
            buffer.seek(0)
            buffer = tambah_stempel_dekat_ketua_tim(
                buffer,
                STEMPEL_PATH
            )

            st.success(
                "PDF berhasil dibuat"
            )

            st.download_button(
                "📄 Download PDF",
                data=buffer,
                file_name="laporan_karantina.pdf",
                mime="application/pdf"
            )

    except Exception as e:

        st.error(
            f"Terjadi kesalahan: {e}"
        )
