# Template slide ITB (LaTeX Beamer + LibreOffice Impress)

Tema yang sama dengan slide SLR disertasi: biru ITB `#005AAB`, aksen emas `#E8A317`,
pita judul biru dengan logo ITB, footer biru muda bergaris emas, halaman bagian berpita biru di kiri.
Bebas dibagikan ke teman; isi contoh sudah generik.

| Folder | Isi | Untuk siapa |
|---|---|---|
| `latex/` | `tema-itb.sty`, `contoh.tex`, `contoh.pdf`, `itb-logo.png` | yang menulis slide di LaTeX |
| `libreoffice/` | `tema-itb.otp` (template Impress), `contoh-itb.odp`, `contoh-itb.pptx` (template PowerPoint), `build_odp.py` | yang memakai LibreOffice Impress / PowerPoint |
| `fonts/` | Fira Sans (Book, Bold, miring), `OFL.txt` | dipasang untuk PowerPoint |

## LaTeX

```latex
\documentclass[aspectratio=169, 10pt]{beamer}
\usepackage[indonesian]{babel}
\usepackage{tema-itb}
```

Kompilasi dengan XeLaTeX: `latexmk -xelatex contoh.tex`. Perlu paket TeX Live `beamertheme-metropolis`,
`fira`, `pgf`. Simpan `tema-itb.sty` dan `itb-logo.png` di folder yang sama dengan berkas `.tex`.

Perintah yang tersedia:

| Perintah | Hasil |
|---|---|
| `\istilah{..}` | istilah kunci, biru tebal |
| `\asing{..}` | istilah asing, miring |
| `\sumber{..}` | baris sumber kecil abu-abu |
| `\begin{intinya}[Judul] .. \end{intinya}` | kotak ringkasan (bawaan judul "Intinya") |
| `\kartu[warna]{lebar}{judul}{isi}` | kartu berkepala warna (`\card` juga jalan) |
| `\stat[warna]{angka}{label}`, `\statw` | ubin angka tunggal |
| `node[tile=warna]` + `\tilenum{ukuran}{angka}` | ubin untuk grid TikZ |
| `\chip{n}{teks}` | bulatan bernomor |
| gaya TikZ `tahap`, `panah`, `kotakpucat` | diagram alur dan agenda |

Warna: `itbBiru`, `itbBiruTua`, `itbBiruMuda`, `itbEmas`, `itbMerah`, `itbAbu`, `itbPucat`.
Ubah footer dengan `\renewcommand{\teksfooter}{...}`; untuk slide berbahasa Inggris
`\renewcommand{\namabagian}{Part}`.

## LibreOffice Impress

`libreoffice/contoh-itb.odp` adalah tiruan **persis** dari `latex/contoh.pdf` (LaTeX tidak diubah).
Setiap posisi, ukuran huruf, warna, garis dan jarak diukur dari PDF Beamer, lalu hasil ODP dibandingkan
kata per kata dan piksel per piksel. Selisih yang tersisa di bawah 0,5 mm.

Elemen khas yang ikut:
- **Butir**: ▶ biru muda, sub-butir − emas, ukuran dan indentasi seperti Beamer.
- **Dua kolom dengan kartu**: kepala berwarna (biru, biru tua, emas, merah) di atas badan bergaris.
- **Kotak**: *intinya* (blok Metropolis), kotak pucat agenda, chip bernomor, ubin angka, tahap + panah,
  sorot emas.
- **Tabel**: objek tabel Impress sungguhan bergaya booktabs. Garis atas dan bawah tebal, garis bawah kepala
  tipis, tanpa garis tegak, kolom angka rata kanan, angka berlebar sama seperti Metropolis. Salin tabel
  contoh untuk membuat tabel baru, lalu tambah baris atau kolom seperti biasa.
- **Font Fira Sans** dengan angka gaya lama, sama dengan paket `FiraSans` di LaTeX. Font sudah ditanam di
  `.otp`/`.odp`.

Cara pakai:
- Pasang template: **Berkas → Templat → Kelola Templat → Impor**, pilih `tema-itb.otp`.
  Atau cukup buka `tema-itb.otp`.
- Master slide: **ITB Judul**, **ITB Isi** (pita judul, logo, footer), **ITB Bagian** (pemisah bagian),
  **ITB Penutup** (slide biru penutup). Ganti lewat **Slide → Ubah Master Slide**.
- Gaya bentuk dan teks berawalan **ITB** ada di panel Gaya (F11) → Gaya Gambar.
- Footer: **Sisip → Kepala dan Kaki** → kolom Footer → **Terapkan ke Semua**.

Batas yang tidak bisa ditiru Impress secara otomatis (di slide contoh sudah ditiru manual):
- **Nomor "k/N"**: Beamer hanya menghitung frame isi. Di slide contoh nomornya ditulis tetap; slide baru
  memakai nomor slide otomatis dari master.
- **Garis progres emas**: di Beamer otomatis. Di Impress bentuknya biasa (gaya **ITB Garis progres**), jadi
  lebarnya diatur per slide.
- **Penataan huruf TeX**: TeX sedikit meregangkan spasi antar-kata dan menggeser teks mengikuti bentuk
  huruf. Di slide contoh ini ditiru per elemen; teks baru memakai spasi biasa (selisih ≤ 1–2 mm).

`.pptx`: `contoh-itb.pptx` adalah versi PowerPoint (master slide dan slide contoh ikut). Untuk PowerPoint, pasang dulu font di folder `fonts/` (lisensi SIL OFL, `fonts/OFL.txt`).
PowerPoint tidak mendukung angka gaya lama, jadi di `.pptx` angkanya angka biasa. Kolom terakhir tabel
juga dilebarkan 1,5 mm agar tidak terbungkus. Hasil `.pptx` diperiksa lewat LibreOffice, belum di
PowerPoint asli.

Untuk mengubah warna atau ukuran secara massal, sunting `libreoffice/build_odp.py` lalu jalankan
`python3 build_odp.py`. Hanya butuh Python 3, ditambah LibreOffice untuk ekspor `.pptx`. Skrip ini
membangun ulang `.otp`, `.odp` dan `.pptx`.
