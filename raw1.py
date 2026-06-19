
                data_tabel.append(
                    [
                        paragraf(row[0]),
                        paragraf(format_tanggal(row[1])),
                        paragraf(row[2]),
                        paragraf(row[3]),
                        detail_hasil,
                    ]
                )

            data_tabel.append(
                [
                    Paragraph("<b>Jumlah Sertifikat</b>", style_wrap),
                    "",
                    "",
                    "",
                    Paragraph(f"<b>{len(df_hasil)}</b>", style_wrap),
                ]
            )

            tabel = Table(
                data_tabel,
                colWidths=[28, 65, 85, 80, 275],
                repeatRows=1,
            )

            tabel.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                        ("VALIGN", (0, 1), (-1, -1), "TOP"),
                        ("SPAN", (0, -1), (3, -1)),
                        ("ALIGN", (0, -1), (3, -1), "CENTER"),
                        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F2F2F2")),
                    ]
                )
            )

            elements.append(tabel)
            elements.append(Spacer(1, 15))

            stempel_dan_ttd = Table(
                [
                    [
                        buat_image_path(STEMPEL_PATH, 90, 90),
                        buat_image_upload(ttd_kiri, 100, 40),
                    ]
                ],
                colWidths=[90, 100],
            )

            stempel_dan_ttd.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )

            kiri = Table(
                [
                    [Paragraph("Mengetahui,<br/>Ketua Tim Karantina Tumbuhan", style_wrap)],
                    [Spacer(1, 10)],
                    [stempel_dan_ttd],
                    [Spacer(1, 10)],
                    [Paragraph("<b>Surya Dharma, S.P.</b><br/>NIP. 197705152001121002", style_wrap)],
                ],
                colWidths=[220],
            )

            kanan = Table(
                [
                    [
                        Paragraph(
                            f"Pekanbaru, {datetime.now().day} {BULAN[datetime.now().month]} {datetime.now().year}"
                            f"<br/><br/>{escape(teks(jabatan))}",
                            style_wrap,
                        )
                    ],
                    [Spacer(1, 10)],
                    [buat_image_upload(ttd_kanan, 100, 40)],
                    [Spacer(1, 10)],
                    [
                        Paragraph(
                            f"<b>{escape(teks(nama_ttd_petugas))}</b><br/>NIP. {escape(teks(nip_petugas))}",
                            style_wrap,
                        )
                    ],
                ],
                colWidths=[220],
            )

            ttd_table = Table(
                [[kiri, "", kanan]],
                colWidths=[220, 90, 220],
            )

            ttd_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                )
            )

            elements.append(ttd_table)

            pdf.build(elements)
            buffer.seek(0)

            st.success("PDF berhasil dibuat")
            st.download_button(
                "Download PDF",
                data=buffer,
                file_name="laporan_karantina.pdf",
                mime="application/pdf",
            )

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Upload file penugasan dan file pelepasan untuk mulai membuat laporan.")
