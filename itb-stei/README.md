# Template slide ITB (LaTeX Beamer + LibreOffice Impress)

Tema yang sama dengan slide SLR disertasi: biru ITB `#005AAB`, aksen emas `#E8A317`,
pita judul biru dengan logo ITB, footer biru muda bergaris emas, halaman bagian berpita biru di kiri.
Bebas dibagikan ke teman; isi contoh sudah generik.

| Folder | Isi | Untuk siapa |
|---|---|---|
| `latex/` | `tema-itb.sty`, `contoh.tex`, `contoh.pdf`, `itb-logo.png` | yang menulis slide di LaTeX |
| `libreoffice/` | `tema-itb.otp` (template), `contoh-itb.odp`, `contoh-itb.pptx`, `build_odp.py` | yang memakai LibreOffice Impress / PowerPoint |
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

`libreoffice/contoh-itb.odp` berisi 10 slide yang sama dengan `latex/contoh.pdf`. Posisi, ukuran huruf dan
warnanya diukur dari PDF Beamer, jadi tampilannya sama.

- **Font Fira Sans** (sama dengan LaTeX) sudah ditanam di `.otp`/`.odp`. Untuk `.pptx`/PowerPoint, pasang dulu
  font di folder `fonts/` (lisensi SIL OFL, `fonts/OFL.txt`): klik dua kali tiap `.otf` → *Install*. Di Linux,
  salin ke `~/.local/share/fonts/`.
- Pasang template: **Berkas → Templat → Kelola Templat → Impor**, pilih `tema-itb.otp`.
  Atau cukup buka `tema-itb.otp`; LibreOffice membuat presentasi baru darinya.
- Tiga master slide: **ITB Judul**, **ITB Isi** (pita judul, logo, footer, nomor halaman "n/N"),
  **ITB Bagian** (pemisah bagian). Ganti lewat **Slide → Ubah Master Slide**.
- Komponen (kartu, ubin angka, kotak intinya, chip, tahap, panah, sorot emas, tabel bergaris) ada di
  slide contoh. Salin-tempel, atau pakai gaya gambar berawalan **ITB** di panel Gaya (F11).
- Garis progres emas di bawah pita judul adalah bentuk biasa (gaya **ITB Garis progres**), bukan
  otomatis seperti di Beamer. Atur lebarnya per slide kalau ingin dipakai.
- Footer: **Sisip → Kepala dan Kaki** → kolom Footer → **Terapkan ke Semua**.

Perbedaan yang tersisa dibanding LaTeX: nomor halaman Impress menghitung semua slide, sedangkan
Beamer hanya menghitung frame isi. Di `.pptx` angka tampil sebagai angka biasa, bukan angka gaya lama.

Untuk mengubah warna/ukuran secara massal, sunting `libreoffice/build_odp.py` lalu jalankan
`python3 build_odp.py`. Hanya butuh Python 3, ditambah LibreOffice untuk ekspor `.pptx`.
Skrip ini membangun ulang `.otp`, `.odp` dan `.pptx`.
