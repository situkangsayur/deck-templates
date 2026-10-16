# Deck templates

Kumpulan template slide, masing-masing dalam dua bentuk: **LaTeX Beamer** dan **LibreOffice Impress**
(`.otp` / `.odp`) dan **PowerPoint** (`.pptx`). Satu template = satu subfolder.

| Template | Gaya | LaTeX | Impress / PowerPoint | Pratinjau |
|---|---|---|---|---|
| [`itb-stei/`](itb-stei/) | biru ITB `#005AAB`, aksen emas, logo ITB, 16:9 (Metropolis) | `latex/tema-itb.sty` | `libreoffice/tema-itb.otp`, `libreoffice/contoh-itb.pptx` | [LaTeX](itb-stei/preview/latex.png) · [Impress](itb-stei/preview/libreoffice.png) |

## Struktur tiap template

```
<nama-template>/
  README.md          cara pakai, daftar perintah/komponen
  latex/             paket .sty + contoh.tex + contoh.pdf + aset (logo)
  libreoffice/       template .otp + contoh .odp/.pptx + skrip pembangun
  preview/           gambar pratinjau
```

## Menambah template baru

1. Salin folder template yang paling mirip, ganti namanya.
2. Ubah palet/logo di `latex/*.sty` dan di `libreoffice/build_odp.py` (konstanta `C`, `FOOTER_TEKS`), lalu
   `python3 build_odp.py` dan `soffice --headless --convert-to pptx contoh-*.odp`.
3. Kompilasi contoh LaTeX (`latexmk -xelatex contoh.tex`), perbarui `preview/`, tambahkan baris di tabel di atas.
