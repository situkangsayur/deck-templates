#!/usr/bin/env python3
"""Bangun template LibreOffice Impress bergaya ITB, sama dengan ../latex/contoh.pdf (tema-itb.sty).

Posisi, ukuran huruf dan warna diukur dari PDF Beamer (halaman 16 x 9 cm, diskalakan ke 25,4 x 14,288 cm,
faktor 1,5875), jadi slide Impress tampil seperti versi LaTeX.

Keluaran (di folder ini):
  tema-itb.otp     template Impress
  contoh-itb.odp   presentasi contoh, slide-nya sama dengan contoh.pdf
Font Fira Sans ditanam di dalam berkas (folder ../fonts juga berisi font yang sama untuk dipasang).

Tanpa dependensi selain Python 3.  Jalankan:  python3 build_odp.py
"""
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
LOGO = HERE / "itb-logo.png"
FONT_DIR = HERE.parent / "fonts"
FONT_FILES = ["FiraSans-Book.otf", "FiraSans-BookItalic.otf", "FiraSans-Bold.otf", "FiraSans-BoldItalic.otf"]

# Halaman 16:9, satuan cm.
W, H = 25.4, 14.288
TB = 1.55             # tinggi pita judul
FY, FT = 13.70, 0.59  # pita footer
FONT = "Fira Sans"
FITUR = ":onum"       # angka gaya lama, sama dengan paket FiraSans di LaTeX (LibreOffice: "Fira Sans:onum")

C = dict(biru="#005AAB", tua="#003D75", muda="#4B75BA", emas="#E8A317", abu="#4A5360",
         latar="#FAFBFD", merah="#B4321C", pucat="#EBF2F8", pucatGaris="#99BDDD",
         blokKepala="#E0EBF5", blokIsi="#F2F7FB", footer="#D4E3F1", teks="#212121",
         jalur="#CEBAB7", tahapMuda="#73A4D1", putih="#FFFFFF")

FOOTER_TEKS = "Nama Anda · Judul Presentasi Anda · STEI ITB"

NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
      'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
      'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
      'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
      'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" '
      'xmlns:xlink="http://www.w3.org/1999/xlink" '
      'xmlns:dc="http://purl.org/dc/elements/1.1/" '
      'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
      'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" '
      'xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" '
      'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" '
      'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
      'xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" '
      'office:version="1.3"')


def cm(v):
    return f"{v:.3f}cm"


def geo(x, y, w, h):
    return f'svg:x="{cm(x)}" svg:y="{cm(y)}" svg:width="{cm(w)}" svg:height="{cm(h)}"'


def font_decls():
    faces = "".join(
        f'<svg:font-face-src><svg:font-face-uri xlink:href="Fonts/{f}" xlink:type="simple">'
        f'<svg:font-face-format svg:string="opentype"/></svg:font-face-uri></svg:font-face-src>'
        for f in FONT_FILES if (FONT_DIR / f).exists())
    return (f'<office:font-face-decls><style:font-face style:name="{FONT}" svg:font-family="&apos;{FONT}{FITUR}&apos;" '
            f'style:font-family-generic="swiss" style:font-pitch="variable">{faces}</style:font-face>'
            '<style:font-face style:name="DejaVu Sans" svg:font-family="&apos;DejaVu Sans&apos;" '
            'style:font-family-generic="swiss"/></office:font-face-decls>')


# --------------------------------------------------------------------------- gaya bernama
def txt(size, color=C["teks"], bold=False, italic=False, angka=None):
    fitur = FITUR if angka is None else angka
    s = (f'fo:font-family="&apos;{FONT}{fitur}&apos;" style:font-family-generic="swiss" '
         f'fo:font-size="{size}pt" fo:color="{color}"')
    s += ' fo:font-weight="bold"' if bold else ' fo:font-weight="normal"'
    s += ' style:letter-kerning="true"'
    if italic:
        s += ' fo:font-style="italic"'
    return f"<style:text-properties {s}/>"


def pad_attrs(pad):
    t, r, b, l = pad if isinstance(pad, tuple) else (pad,) * 4
    return (f'fo:padding-top="{cm(t)}" fo:padding-right="{cm(r)}" fo:padding-bottom="{cm(b)}" '
            f'fo:padding-left="{cm(l)}"')


GAYA_PAD = {}  # padding tiap gaya bernama, untuk gaya turunan (geser teks) di slide contoh


def gstyle(name, display, fill=None, stroke=None, sw=0.03, size=14.2, color=C["teks"], bold=False,
           align="start", valign="top", pad=0.0, spacing=0.0, lh=None):
    GAYA_PAD[name] = (pad if isinstance(pad, tuple) else (pad,) * 4, valign)
    fillp = f'draw:fill="solid" draw:fill-color="{fill}"' if fill else 'draw:fill="none"'
    strokep = (f'draw:stroke="solid" svg:stroke-color="{stroke}" svg:stroke-width="{cm(sw)}"'
               if stroke else 'draw:stroke="none"')
    return (f'<style:style style:name="{name}" style:display-name="{display}" style:family="graphic" '
            f'style:parent-style-name="standard">'
            f'<style:graphic-properties {fillp} {strokep} draw:textarea-vertical-align="{valign}" '
            f'draw:textarea-horizontal-align="justify" draw:auto-grow-height="false" draw:auto-grow-width="false" '
            f'{pad_attrs(pad)} fo:wrap-option="wrap" draw:shadow="hidden"/>'
            f'<style:paragraph-properties fo:text-align="{align}" fo:margin-top="0cm" '
            f'fo:margin-bottom="{cm(spacing)}" fo:line-height="{cm(lh) if lh else "100%"}"/>'
            f'{txt(size, color, bold)}</style:style>')


WARNA = [("", "biru", "biru"), ("-tua", "tua", "biru tua"), ("-emas", "emas", "emas"), ("-merah", "merah", "merah")]


def named_graphic_styles():
    out = [
        '<style:default-style style:family="graphic"><style:graphic-properties svg:stroke-color="#3465A4" '
        'draw:fill-color="#729FCF"/><style:paragraph-properties style:writing-mode="lr-tb"/>'
        f'{txt(15.8)}</style:default-style>',
        '<style:style style:name="standard" style:family="graphic"><style:graphic-properties draw:stroke="none" '
        'draw:fill="none" draw:shadow="hidden" fo:padding-top="0cm" fo:padding-bottom="0cm" fo:padding-left="0cm" '
        'fo:padding-right="0cm"/>' + txt(15.8) + '</style:style>',
        gstyle("Teks", "ITB Teks", size=15.8),
        gstyle("Teks-kecil", "ITB Teks kecil", size=12.7),
        gstyle("Catatan-kecil", "ITB Catatan kecil (sumber)", size=11.1, color=C["abu"]),
        gstyle("Kotak-pucat", "ITB Kotak pucat", fill=C["pucat"], stroke=C["pucatGaris"], sw=0.022, size=14.2,
               valign="middle", pad=(0, 0.22, 0.18, 0.22), lh=0.71),
        gstyle("Chip", "ITB Chip bernomor", fill=C["biru"], size=14.2, color=C["putih"], bold=True, align="center",
               valign="middle"),
        gstyle("Chip-kecil", "ITB Chip bernomor kecil", fill=C["biru"], size=11.1, color=C["putih"], bold=True,
               align="center", valign="middle"),
        gstyle("Intinya-kepala", "ITB Intinya - kepala", fill=C["blokKepala"], size=15.8, color=C["biru"],
               bold=True, valign="middle", pad=(0, 0.18, 0, 0.18)),
        gstyle("Intinya-isi", "ITB Intinya - isi", fill=C["blokIsi"], size=15.8, valign="top",
               pad=(0.09, 0.18, 0.09, 0.18)),
        gstyle("Label-emas", "ITB Label emas", fill=C["emas"], size=11.1, color="#000000", bold=True,
               align="center", valign="middle"),
        gstyle("Nomor-bagian", "ITB Nomor bagian", size=101, color=C["putih"], bold=True, align="center"),
        gstyle("Label-bagian", "ITB Label bagian", size=14.2, color=C["putih"], align="center"),
        gstyle("Judul-penulis", "ITB Halaman judul - penulis", size=14.2),
        gstyle("Judul-pembimbing", "ITB Halaman judul - pembimbing", size=12.7),
        gstyle("Judul-institusi", "ITB Halaman judul - institusi", size=11.1, lh=0.51),
        gstyle("Nomor", "ITB Nomor halaman tetap", size=11.1, color=C["biru"], align="end", valign="middle"),
        '<style:style style:name="Sorot" style:display-name="ITB Sorot emas" style:family="graphic" '
        f'style:parent-style-name="standard"><style:graphic-properties draw:fill="none" draw:stroke="solid" '
        f'svg:stroke-color="{C["emas"]}" svg:stroke-width="0.112cm"/></style:style>',
        '<style:style style:name="Panah" style:display-name="ITB Panah" style:family="graphic" '
        f'style:parent-style-name="standard"><style:graphic-properties draw:stroke="solid" svg:stroke-color="{C["biru"]}" '
        'svg:stroke-width="0.078cm" draw:marker-end="Panah" draw:marker-end-width="0.3cm"/></style:style>',
        '<style:style style:name="Garis-tabel" style:display-name="ITB Garis tabel tebal" style:family="graphic" '
        f'style:parent-style-name="standard"><style:graphic-properties draw:stroke="solid" '
        f'svg:stroke-color="{C["teks"]}" svg:stroke-width="0.045cm"/></style:style>',
        '<style:style style:name="Garis-tabel-tipis" style:display-name="ITB Garis tabel tipis" '
        'style:family="graphic" style:parent-style-name="standard"><style:graphic-properties draw:stroke="solid" '
        f'svg:stroke-color="{C["teks"]}" svg:stroke-width="0.028cm"/></style:style>',
        '<style:style style:name="Progres" style:display-name="ITB Garis progres" style:family="graphic" '
        f'style:parent-style-name="standard"><style:graphic-properties draw:stroke="none" draw:fill="solid" '
        f'draw:fill-color="{C["emas"]}"/></style:style>',
    ]
    for suf, key, nama in WARNA:
        col = C[key]
        out.append(gstyle(f"Kartu-kepala{suf}", f"ITB Kartu {nama} - kepala", fill=col, size=12.7,
                          color=C["putih"], bold=True, valign="middle", pad=(0, 0.11, 0, 0.11)))
        out.append(gstyle(f"Kartu-isi{suf}", f"ITB Kartu {nama} - isi", fill=C["putih"], stroke=col, sw=0.045,
                          size=12.7, pad=(0.09, 0.22, 0.1, 0.22), lh=0.60))
        out.append(gstyle(f"Ubin{suf}", f"ITB Ubin angka {nama}", fill=col, size=11.1, color=C["putih"],
                          align="center", valign="middle", pad=(0, 0.12, 0.12, 0.12)))
    out.append(gstyle("Tahap", "ITB Tahap", fill=C["biru"], size=14.2, color=C["putih"], bold=True,
                      align="center", valign="middle", lh=0.66))
    out.append(gstyle("Tahap-muda", "ITB Tahap muda", fill=C["tahapMuda"], size=14.2, color=C["putih"],
                      bold=True, align="center", valign="middle", lh=0.66))
    return "".join(out)


# Tanda butir: ▶ biru muda (tingkat 1), − emas (tingkat 2), • abu (tingkat 3+).
BUTIR = [("▶", C["muda"], 80, 0.03, 0.68), ("−", C["emas"], 100, 1.15, 0.68), ("•", C["abu"], 100, 2.3, 0.6)]


def bullet_list_style(name):
    lv = []
    for i in range(1, 10):
        ch, col, rel, before, width = BUTIR[min(i - 1, 2)]
        if i > 3:
            before += 0.9 * (i - 3)
        lv.append(f'<text:list-level-style-bullet text:level="{i}" text:bullet-char="{ch}">'
                  f'<style:list-level-properties text:space-before="{cm(before)}" text:min-label-width="{cm(width)}"/>'
                  f'<style:text-properties fo:font-family="&apos;DejaVu Sans&apos;" style:use-window-font-color="false" '
                  f'fo:color="{col}" fo:font-size="{rel}%"/></text:list-level-style-bullet>')
    return f'<text:list-style style:name="{name}">{"".join(lv)}</text:list-style>'


def mname(master):
    """Nama internal master. LibreOffice memasangkan gaya 'ITB Isi-title' ke master bernama tampilan 'ITB Isi'."""
    return f"ITB_20_{master}"


def presentation_styles(master, title_size, title_color, title_valign="middle", title_align="start"):
    p = mname(master)

    def st(cls, parent=""):
        par = f' style:parent-style-name="{p}-{parent}"' if parent else ""
        return (f'<style:style style:name="{p}-{cls}" style:display-name="ITB {master}-{cls}" '
                f'style:family="presentation"{par}>')
    nol = 'fo:padding-top="0cm" fo:padding-bottom="0cm" fo:padding-left="0cm" fo:padding-right="0cm"'
    s = [st("background") + '<style:graphic-properties draw:stroke="none" draw:fill="solid" '
         f'draw:fill-color="{C["latar"]}"/></style:style>',
         st("backgroundobjects") + '<style:graphic-properties draw:shadow="hidden"/></style:style>',
         st("notes") + f'{txt(14)}</style:style>',
         st("title") + f'<style:graphic-properties draw:stroke="none" draw:fill="none" '
         f'draw:textarea-vertical-align="{title_valign}" draw:auto-grow-height="false" {nol}/>'
         f'<style:paragraph-properties fo:text-align="{title_align}" fo:line-height="100%"/>'
         f'{txt(title_size, title_color, True)}</style:style>',
         st("subtitle") + f'<style:graphic-properties draw:stroke="none" draw:fill="none" '
         f'draw:textarea-vertical-align="top" {nol}/><style:paragraph-properties fo:text-align="start"/>'
         f'{txt(19, C["teks"])}</style:style>',
         st("outline1") + '<style:graphic-properties draw:stroke="none" draw:fill="none" '
         f'draw:auto-grow-height="false" draw:textarea-vertical-align="top" {nol}>'
         f'{bullet_list_style("L-" + master)}</style:graphic-properties>'
         '<style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.21cm" fo:line-height="100%"/>'
         f'{txt(15.8)}</style:style>']
    sizes = {2: 14.2, 3: 12.7}
    for i in range(2, 10):
        s.append(st(f"outline{i}", f"outline{i - 1}")
                 + '<style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.21cm"/>'
                 f'<style:text-properties fo:font-size="{sizes.get(i, 12.7)}pt"/></style:style>')
    return "".join(s)


# --------------------------------------------------------------------------- master slide
AUTO_STYLES = f"""
<style:page-layout style:name="PM1"><style:page-layout-properties fo:margin-top="0cm" fo:margin-bottom="0cm"
 fo:margin-left="0cm" fo:margin-right="0cm" fo:page-width="{cm(W)}" fo:page-height="{cm(H)}"
 style:print-orientation="landscape"/></style:page-layout>
<style:style style:name="Mdp1" style:family="drawing-page"><style:drawing-page-properties draw:fill="solid"
 draw:fill-color="{C['latar']}" draw:background-size="full"/></style:style>
<style:style style:name="Mgr-biru" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="none" draw:fill="solid" draw:fill-color="{C['biru']}"/></style:style>
<style:style style:name="Mgr-emas" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="none" draw:fill="solid" draw:fill-color="{C['emas']}"/></style:style>
<style:style style:name="Mgr-jalur" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="none" draw:fill="solid" draw:fill-color="{C['jalur']}"/></style:style>
<style:style style:name="Mgr-footer" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="none" draw:fill="solid" draw:fill-color="{C['footer']}"/></style:style>
<style:style style:name="Mgr-garis-emas" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="solid" svg:stroke-color="{C['emas']}" svg:stroke-width="0.039cm"/></style:style>
<style:style style:name="Mgr-img" style:family="graphic" style:parent-style-name="standard"><style:graphic-properties
 draw:stroke="none" draw:fill="none"/></style:style>
<style:style style:name="Mgr-ft" style:family="presentation"><style:graphic-properties draw:stroke="none" draw:fill="none"
 draw:textarea-vertical-align="middle" draw:auto-grow-height="false" fo:padding-top="0cm" fo:padding-bottom="0cm"
 fo:padding-left="0cm" fo:padding-right="0cm"/>{txt(11.1, C['biru'])}</style:style>
<style:style style:name="MP-kanan" style:family="paragraph"><style:paragraph-properties fo:text-align="end"/></style:style>
"""

LAYOUTS = f"""
<style:presentation-page-layout style:name="AL1T0"><presentation:placeholder presentation:object="title"
 {geo(1.59, 2.4, 20.0, 1.3)}/><presentation:placeholder presentation:object="subtitle" {geo(1.59, 3.9, 20.0, 1.2)}/>
</style:presentation-page-layout>
<style:presentation-page-layout style:name="AL2T1"><presentation:placeholder presentation:object="title"
 {geo(0.55, 0, 22.4, TB)}/><presentation:placeholder presentation:object="outline" {geo(1.99, 2.4, 22.0, 10.6)}/>
</style:presentation-page-layout>
<style:presentation-page-layout style:name="AL3T19"><presentation:placeholder presentation:object="title"
 {geo(0.55, 0, 22.4, TB)}/></style:presentation-page-layout>
"""


def image(x, y, s, layer="backgroundobjects"):
    return (f'<draw:frame draw:style-name="Mgr-img" draw:layer="{layer}" {geo(x, y, s, s)}>'
            '<draw:image xlink:href="Pictures/itb-logo.png" xlink:type="simple" xlink:show="embed" '
            'xlink:actuate="onLoad"/></draw:frame>')


def mrect(style, x, y, w, h):
    return f'<draw:rect draw:style-name="{style}" draw:layer="backgroundobjects" {geo(x, y, w, h)}/>'


def mline(style, x1, y1, x2, y2):
    return (f'<draw:line draw:style-name="{style}" draw:layer="backgroundobjects" svg:x1="{cm(x1)}" '
            f'svg:y1="{cm(y1)}" svg:x2="{cm(x2)}" svg:y2="{cm(y2)}"/>')


def placeholder(master, cls, x, y, w, h):
    ps = "outline1" if cls == "outline" else cls
    return (f'<draw:frame presentation:style-name="{mname(master)}-{ps}" draw:layer="backgroundobjects" '
            f'{geo(x, y, w, h)} presentation:class="{cls}" presentation:placeholder="true"><draw:text-box/></draw:frame>')


BAND = 9.14


def masters():
    isi = (mrect("Mgr-biru", 0, 0, W, TB)
           + mrect("Mgr-jalur", 0, TB, W, 0.022)
           + image(24.03, 0.18, 1.19)
           + mrect("Mgr-footer", 0, FY, W, FT)
           + mline("Mgr-garis-emas", 0, FY - 0.02, W, FY - 0.02)
           + placeholder("Isi", "title", 0.55, 0, 22.4, TB)
           + placeholder("Isi", "outline", 1.99, 2.4, 22.0, 10.6)
           + f'<draw:frame presentation:style-name="Mgr-ft" draw:layer="backgroundobjects" {geo(0.32, FY - 0.07, 16, FT)} '
             'presentation:class="footer"><draw:text-box><text:p><presentation:footer/></text:p></draw:text-box></draw:frame>'
           + f'<draw:frame presentation:style-name="Mgr-ft" draw:layer="backgroundobjects" {geo(W - 4.32, FY - 0.07, 4, FT)} '
             'presentation:class="page-number"><draw:text-box><text:p text:style-name="MP-kanan">'
             '<text:page-number>&lt;number&gt;</text:page-number></text:p></draw:text-box></draw:frame>')
    bagian = (mrect("Mgr-biru", 0, 0, BAND, H)
              + mrect("Mgr-emas", BAND, 0, 0.13, H)
              + image(23.36, 12.24, 1.59)
              + placeholder("Bagian", "title", 10.61, 4.0, 14.2, 6.2)
              + placeholder("Bagian", "outline", 10.61, 10.4, 14.2, 1.5))
    judul = (image(21.39, 7.58, 2.7)
             + placeholder("Judul", "title", 1.59, 2.4, 20.0, 1.3)
             + placeholder("Judul", "outline", 1.59, 6.85, 19.0, 4.8)
             + mrect("Mgr-emas", 1.59, 5.72, 22.23, 0.02))

    def mp(name, body):
        return (f'<style:master-page style:name="{mname(name)}" style:display-name="ITB {name}" '
                f'style:page-layout-name="PM1" draw:style-name="Mdp1">{body}</style:master-page>')

    penutup = (mrect("Mgr-biru", 0, 0, W, H) + mrect("Mgr-footer", 0, FY, W, FT)
               + mline("Mgr-garis-emas", 0, FY - 0.02, W, FY - 0.02)
               + placeholder("Penutup", "title", 0, 5.5, W, 3.0)
               + f'<draw:frame presentation:style-name="Mgr-ft" draw:layer="backgroundobjects" {geo(0.32, FY - 0.07, 16, FT)} '
                 'presentation:class="footer"><draw:text-box><text:p><presentation:footer/></text:p></draw:text-box></draw:frame>'
               + f'<draw:frame presentation:style-name="Mgr-ft" draw:layer="backgroundobjects" {geo(W - 4.32, FY - 0.07, 4, FT)} '
                 'presentation:class="page-number"><draw:text-box><text:p text:style-name="MP-kanan">'
                 '<text:page-number>&lt;number&gt;</text:page-number></text:p></draw:text-box></draw:frame>')
    return mp("Judul", judul) + mp("Isi", isi) + mp("Bagian", bagian) + mp("Penutup", penutup)


def styles_xml():
    marker = '<draw:marker draw:name="Panah" svg:viewBox="0 0 20 30" svg:d="M10 0l-10 30h20z"/>'
    pres = (presentation_styles("Judul", 22.8, C["teks"], title_valign="top")
            + presentation_styles("Isi", 19, C["putih"])
            + presentation_styles("Bagian", 27.3, C["tua"])
            + presentation_styles("Penutup", 22.8, C["putih"], title_align="center"))
    return (f'<?xml version="1.0" encoding="UTF-8"?><office:document-styles {NS}>{font_decls()}'
            f'<office:styles>{marker}{named_graphic_styles()}{pres}{LAYOUTS}</office:styles>'
            f'<office:automatic-styles>{AUTO_STYLES}</office:automatic-styles>'
            '<office:master-styles><draw:layer-set><draw:layer draw:name="layout"/><draw:layer draw:name="background"/>'
            '<draw:layer draw:name="backgroundobjects"/><draw:layer draw:name="controls"/>'
            f'<draw:layer draw:name="measurelines"/></draw:layer-set>{masters()}</office:master-styles>'
            '</office:document-styles>')


# --------------------------------------------------------------------------- isi slide
CONTENT_AUTO = f"""
<style:style style:name="dp-isi" style:family="drawing-page"><style:drawing-page-properties presentation:display-footer="true"
 presentation:display-page-number="true" presentation:display-date-time="false" presentation:background-visible="true"
 presentation:background-objects-visible="true"/></style:style>
<style:style style:name="dp-isi-tetap" style:family="drawing-page"><style:drawing-page-properties presentation:display-footer="true"
 presentation:display-page-number="false" presentation:display-date-time="false" presentation:background-visible="true"
 presentation:background-objects-visible="true"/></style:style>
<style:style style:name="dp-polos" style:family="drawing-page"><style:drawing-page-properties presentation:display-footer="false"
 presentation:display-page-number="false" presentation:display-date-time="false" presentation:background-visible="true"
 presentation:background-objects-visible="true"/></style:style>
<style:style style:name="T-tebal" style:family="text"><style:text-properties fo:font-weight="bold"/></style:style>
<style:style style:name="T-miring" style:family="text"><style:text-properties fo:font-style="italic"/></style:style>
<style:style style:name="T-istilah" style:family="text"><style:text-properties fo:color="{C['biru']}" fo:font-weight="bold"/></style:style>
<style:style style:name="T-alert" style:family="text"><style:text-properties fo:color="{C['merah']}"/></style:style>
<style:style style:name="T-angka" style:family="text"><style:text-properties fo:font-size="34.8pt" fo:font-weight="bold"/></style:style>
<style:style style:name="T-angka-lebar" style:family="text"><style:text-properties fo:font-size="23.7pt" fo:font-weight="bold"/></style:style>
{bullet_list_style("L-isi")}
<style:style style:name="P-label" style:family="paragraph"><style:paragraph-properties fo:text-align="center" fo:line-height="0.77cm"/></style:style>
<style:style style:name="P-tengah" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/></style:style>
<style:style style:name="P-angka" style:family="paragraph"><style:paragraph-properties fo:text-align="center" fo:margin-bottom="0cm" fo:line-height="1.23cm"/></style:style>
<style:style style:name="P-angka-lebar" style:family="paragraph"><style:paragraph-properties fo:text-align="center" fo:margin-bottom="0.11cm" fo:line-height="0.84cm"/></style:style>
<style:style style:name="P-sub" style:family="paragraph"><style:paragraph-properties fo:margin-bottom="0.31cm"/>
 <style:text-properties fo:font-size="14.2pt"/></style:style>
"""

MARK = re.compile(r"(\*\*.+?\*\*|//.+?//|\[\[.+?\]\]|\{\{.+?\}\})")
TSTYLE = {"**": "T-tebal", "//": "T-miring", "[[": "T-alert", "{{": "T-istilah"}


OTOMATIS = {}  # gaya otomatis tambahan (spasi antar-kata, geser teks) untuk meniru tata letak TeX di slide contoh


def gaya_otomatis(kunci, xml):
    if kunci not in OTOMATIS:
        OTOMATIS[kunci] = xml.replace("@NAMA@", f"A{len(OTOMATIS)}")
    return re.search(r'style:name="([^"]+)"', OTOMATIS[kunci]).group(1)


def spasi_span(teks, spasi):
    """TeX meregangkan spasi antar-kata pada baris rata kiri; spasi + jarak huruf meniru lebar spasi itu."""
    if not spasi:
        return escape(teks)
    st = gaya_otomatis(("spasi", spasi), '<style:style style:name="@NAMA@" style:family="text">'
                       f'<style:text-properties fo:letter-spacing="{cm(spasi)}"/></style:style>')
    return escape(teks).replace(" ", f'<text:span text:style-name="{st}"> </text:span>')


def runs(s, spasi=0):
    """Penanda: **tebal**  //miring//  [[merah]]  {{istilah biru tebal}}"""
    out = []
    for part in MARK.split(s):
        if not part:
            continue
        st = TSTYLE.get(part[:2]) if len(part) > 4 else None
        out.append(f'<text:span text:style-name="{st}">{spasi_span(part[2:-2], spasi)}</text:span>' if st
                   else spasi_span(part, spasi))
    return "".join(out)


def paras(text, pstyle=None, spasi=0):
    ps = f' text:style-name="{pstyle}"' if pstyle else ""
    return "".join(f"<text:p{ps}>{runs(line, spasi)}</text:p>" for line in text.split("\n"))


def geser(style, dy):
    """Gaya turunan yang menggeser teks dy cm ke bawah (negatif = ke atas), meniru posisi TeX yang ikut
    bentuk huruf. Hanya untuk slide contoh; bentuk baru memakai gaya bernamanya langsung."""
    if not dy:
        return style
    (t, r, b, l), valign = GAYA_PAD[style]
    if valign == "middle":
        t, b = (t + 2 * dy, b) if dy > 0 else (t, b - 2 * dy)
    else:
        t += dy
    return gaya_otomatis(("geser", style, dy), f'<style:style style:name="@NAMA@" style:family="graphic" '
                         f'style:parent-style-name="{style}"><style:graphic-properties fo:padding-top="{cm(t)}" '
                         f'fo:padding-bottom="{cm(b)}"/></style:style>')


def custom(style, x, y, w, h, inner="", radius=None, kind="rect"):
    """Bentuk khusus (custom shape): teks di dalamnya membungkus, ikut terekspor ke .pptx."""
    if kind == "circle":
        g = 'draw:type="ellipse"'
    elif radius:
        g = f'draw:type="round-rectangle" draw:modifiers="{round(radius / min(w, h) * 21600)}"'
    else:
        g = 'draw:type="rectangle"'
    return (f'<draw:custom-shape draw:style-name="{style}" {geo(x, y, w, h)}>{inner}'
            f'<draw:enhanced-geometry svg:viewBox="0 0 21600 21600" {g}/></draw:custom-shape>')


def shape(style, x, y, w, h, text="", radius=None, kind="rect", pstyle=None, spasi=0, dy=0):
    return custom(geser(style, dy), x, y, w, h, paras(text, pstyle, spasi) if text else "", radius, kind)


def textbox(style, x, y, w, h, text, pstyle=None, spasi=0):
    return (f'<draw:frame draw:style-name="{style}" {geo(x, y, w, h)}><draw:text-box>{paras(text, pstyle, spasi)}'
            '</draw:text-box></draw:frame>')


def line(style, x1, y1, x2, y2):
    return (f'<draw:line draw:style-name="{style}" svg:x1="{cm(x1)}" svg:y1="{cm(y1)}" svg:x2="{cm(x2)}" '
            f'svg:y2="{cm(y2)}"/>')


def kartu(x, y, w, hk, hb, judul, isi="", warna="", spasi=0, spasi_judul=0):
    """Kartu: kepala berwarna (tinggi hk) di atas badan bergaris (tinggi hb). Dikelompokkan."""
    return ("<draw:g>" + shape(f"Kartu-isi{warna}", x + 0.01, y + hk - 0.02, w, hb, isi, radius=0.22, spasi=spasi)
            + shape(f"Kartu-kepala{warna}", x, y, w - 0.55, hk, judul, radius=0.17, spasi=spasi_judul) + "</draw:g>")


def intinya(x, y, w, judul, isi, hk=0.85, hb=0.92):
    return ("<draw:g>" + shape("Intinya-kepala", x, y, w, hk, judul)
            + shape("Intinya-isi", x, y + hk, w, hb, isi) + "</draw:g>")


def ubin(x, y, angka, label, warna="", lebar=False, w=4.76, h=4.21, dy=0, spasi=0):
    st = "T-angka-lebar" if lebar else "T-angka"
    body = (f'<text:p text:style-name="{"P-angka-lebar" if lebar else "P-angka"}"><text:span text:style-name="{st}">{escape(angka)}</text:span></text:p>'
            + "".join(f'<text:p text:style-name="P-label">{spasi_span(t, spasi)}</text:p>' for t in label.split("\n")))
    return custom(geser(f"Ubin{warna}", dy), x, y, w, h, body, radius=0.28)


TABEL_GAYA = []
# Impress menggambar garis sel 1,75x lebih tebal dari nilai di gaya; dikoreksi agar sama dengan booktabs.
GARIS_TEBAL, GARIS_TIPIS = "0.0257cm solid #212121", "0.016cm solid #212121"
SEP = 0.336  # \tabcolsep Beamer (6pt x 1,5875)
BARIS = 0.598  # tinggi satu baris teks 14,2pt di Impress


def tabel(x, y, lebar, batas, rows, kanan=()):
    r"""Tabel Impress bergaya booktabs (seperti \toprule, \midrule, \bottomrule): garis atas & bawah tebal,
    garis bawah kepala tipis, tanpa garis tegak; angka berlebar sama dan gaya lama seperti Metropolis.
    batas: posisi y tiap baris (atas, lalu bawah tiap baris); teks diletakkan pada batas + jarak atas.
    Impress menghitung tinggi baris dari isinya, jadi tinggi diatur lewat jarak atas/bawah sel.
    Salin tabel contoh untuk membuat tabel baru (gaya selnya ikut tersalin)."""
    teks_atas, tepi = batas
    for i, w in enumerate(lebar):
        TABEL_GAYA.append(f'<style:style style:name="TK{i}" style:family="table-column">'
                          f'<style:table-column-properties style:column-width="{cm(w)}" '
                          'style:use-optimal-column-width="false"/></style:style>')
    for r in range(len(rows)):
        TABEL_GAYA.append(f'<style:style style:name="TR{r}" style:family="table-row">'
                          f'<style:table-row-properties style:row-height="{cm(tepi[r + 1] - tepi[r])}" '
                          'style:use-optimal-row-height="false"/></style:style>')
        atas = GARIS_TEBAL if r == 0 else "none"
        bawah = GARIS_TIPIS if r == 0 else GARIS_TEBAL if r == len(rows) - 1 else "none"
        pt = teks_atas[r] - tepi[r]
        pb = tepi[r + 1] - tepi[r] - pt - BARIS
        for c in range(len(lebar)):
            pl = 0 if c == 0 else 0.1 if c in kanan else SEP
            # Kolom rata kiri tidak butuh jarak kanan penuh; jarak kecil mencegah Impress diam-diam membungkus teks
            # terpanjang (yang membuat baris lebih tinggi). Posisi teks tetap sama dengan LaTeX.
            pr = SEP if c in kanan else 0 if c == len(lebar) - 1 else 0.1
            TABEL_GAYA.append(
                f'<style:style style:name="TS{r}-{c}" style:family="table-cell">'
                f'<loext:graphic-properties draw:fill="none" draw:textarea-vertical-align="top" '
                f'fo:padding-top="{cm(pt)}" fo:padding-bottom="{cm(pb)}" fo:padding-left="{cm(pl)}" '
                f'fo:padding-right="{cm(pr)}"/>'
                f'<style:paragraph-properties fo:border-top="{atas}" fo:border-bottom="{bawah}" '
                'fo:border-left="none" fo:border-right="none"/>'
                f'{txt(14.2, angka=":onum&amp;tnum")}</style:style>')
    for k, rata in (("kr", "start"), ("kn", "end"), ("akhir", "start")):
        gaya = f'<style:style style:name="TP-{k}" style:family="paragraph">' \
               f'<style:paragraph-properties fo:text-align="{rata}" fo:line-height="100%"/>' \
               f'{txt(14.2, angka=":onum&amp;tnum")}</style:style>'
        if k == "akhir":  # kolom terakhir berakhir tepat di ujung garis: sedikit kelonggaran agar tidak terbungkus
            gaya = gaya.replace('style:letter-kerning="true"', 'style:letter-kerning="true" fo:letter-spacing="-0.003cm"')
        TABEL_GAYA.append(gaya)
    cols = "".join(f'<table:table-column table:style-name="TK{i}"/>' for i in range(len(lebar)))
    body = ""
    for r, row in enumerate(rows):
        sel = "".join(f'<table:table-cell table:style-name="TS{r}-{c}">'
                      f'<text:p text:style-name="TP-{"kn" if c in kanan else "akhir" if c == len(row) - 1 else "kr"}">'
                      f'{runs(t)}</text:p></table:table-cell>'
                      for c, t in enumerate(row))
        body += f'<table:table-row table:style-name="TR{r}">{sel}</table:table-row>'
    return (f'<draw:frame draw:style-name="standard" draw:layer="layout" '
            f'{geo(x, y, sum(lebar), tepi[-1] - tepi[0])}><table:table>{cols}{body}</table:table></draw:frame>')


def chip(x, y, n, d=0.98, style="Chip"):
    # Angka gaya lama 3, 5, 7 berekor ke bawah; TeX memusatkan menurut bentuk hurufnya, jadi naikkan sedikit.
    return shape(style, x, y, d, d, str(n), kind="circle", dy=-0.055 if str(n) in "357" else 0)


def ph_title(master, text, x, y, w, h, spasi=0):
    return (f'<draw:frame presentation:style-name="{mname(master)}-title" draw:layer="layout" {geo(x, y, w, h)} '
            f'presentation:class="title"><draw:text-box><text:p>{runs(text, spasi)}</text:p></draw:text-box></draw:frame>')


def ph_subtitle(text, x, y, w, h):
    return (f'<draw:frame presentation:style-name="{mname("Judul")}-subtitle" draw:layer="layout" {geo(x, y, w, h)} '
            f'presentation:class="subtitle"><draw:text-box>{paras(text)}</draw:text-box></draw:frame>')


def ph_outline(items, x=1.99, y=4.7, w=22.0, h=4.0):
    """items: daftar (tingkat, teks); tingkat 1 atau 2."""
    out, i = [], 0
    while i < len(items):
        out.append(f"<text:list-item><text:p>{runs(items[i][1])}</text:p>")
        i += 1
        subs = []
        while i < len(items) and items[i][0] == 2:
            subs.append(f'<text:list-item><text:p text:style-name="P-sub">{runs(items[i][1])}</text:p></text:list-item>')
            i += 1
        if subs:
            out.append(f"<text:list>{''.join(subs)}</text:list>")
        out.append("</text:list-item>")
    return (f'<draw:frame presentation:style-name="{mname("Isi")}-outline1" draw:layer="layout" {geo(x, y, w, h)} '
            f'presentation:class="outline"><draw:text-box><text:list text:style-name="L-isi">{"".join(out)}'
            '</text:list></draw:text-box></draw:frame>')


PAGES = []
N_ISI = 6     # jumlah slide berfooter (untuk garis progres, seperti Beamer)
ISI_KE = [0]


def nomor(teks):
    """Nomor halaman "k/N" seperti Beamer (yang hanya menghitung frame isi). Nomor otomatis Impress menghitung
    semua slide, jadi di slide contoh nomornya ditulis tetap; slide baru memakai nomor otomatis dari master."""
    return (f'<draw:frame draw:style-name="Nomor" {geo(W - 4.32, FY - 0.07, 4, FT)}><draw:text-box>'
            f'<text:p>{teks}</text:p></draw:text-box></draw:frame>')


def page(name, master, layout, body, dp="dp-isi"):
    footer = ' presentation:use-footer-name="ftr1"' if dp.startswith("dp-isi") else ""
    PAGES.append(f'<draw:page draw:name="{escape(name)}" draw:style-name="{dp}" draw:master-page-name="{mname(master)}" '
                 f'presentation:presentation-page-layout-name="{layout}"{footer}>{body}'
                 '<presentation:notes draw:style-name="dp-polos"/></draw:page>')


def isi(name, title, body, layout="AL3T19"):
    """Slide isi: judul + garis progres emas (lebar = urutan/N, seperti progressbar Metropolis)."""
    ISI_KE[0] += 1
    progres = custom("Progres", 0, TB, W * ISI_KE[0] / N_ISI, 0.022)
    page(name, "Isi", layout, ph_title("Isi", title, 0.55, 0, 22.4, TB) + progres + body
         + nomor(f"{ISI_KE[0]}/{N_ISI}"), dp="dp-isi-tetap")


def bagian(n, judul, dy=0.0, spasi=0):
    page(f"Bagian {n}", "Bagian", "AL3T19",
         textbox("Nomor-bagian", 0, 3.97, BAND, 4.6, str(n))
         + textbox("Label-bagian", 0, 8.53, BAND, 0.7, f"Bagian {n}")
         + ph_title("Bagian", judul, 10.61, 4.0 + dy, 14.2, 6.2, spasi), dp="dp-polos")


def build_pages():
    # 1. Judul
    page("Judul", "Judul", "AL1T0",
         ph_title("Judul", "Judul Presentasi Anda", 1.59, 2.55, 20.0, 1.2)
         + ph_subtitle("Subjudul, mis. tinjauan pustaka sistematis (Kitchenham), 2021–2026", 1.59, 3.98, 21.5, 1.0)
         + textbox("Judul-penulis", 1.59, 6.96, 18.0, 0.7, "Nama Anda · NIM")
         + textbox("Judul-pembimbing", 1.59, 7.90, 18.0, 0.6, "Promotor: Prof. Dr. Nama Promotor")
         + textbox("Judul-pembimbing", 1.59, 8.61, 18.0, 0.6, "Ko-promotor: Dr. Nama Ko-promotor")
         + textbox("Judul-penulis", 1.59, 9.37, 18.0, 0.7, "Oktober 2026")
         + textbox("Judul-institusi", 1.59, 10.46, 18.0, 1.1,
                   "Program Doktor Teknik Elektro dan Informatika\n"
                   "Sekolah Teknik Elektro dan Informatika, Institut Teknologi Bandung", spasi=-0.011),
         dp="dp-polos")

    # 2. Agenda
    # (teks, y, tinggi, spasi tambahan antar-kata, geser tegak): meniru TeX di contoh.pdf
    agenda = [("Latar belakang", 4.70, 1.35, 0, 0), ("Masalah dan pertanyaan\npenelitian", 6.24, 1.75, 0.04, 0),
              ("Metode", 8.19, 1.35, 0, 0), ("Hasil RQ1", 9.93, 1.35, 0, 0),
              ("Hasil RQ2", 4.70, 1.35, 0, 0), ("Hasil RQ3", 6.44, 1.35, 0, 0),
              ("Celah riset dan model", 8.19, 1.35, 0.04, 0.05),
              ("Validitas dan langkah berikutnya", 9.93, 1.35, 0.043, 0)]
    b = ""
    for i, (t, y, h, sp, dy) in enumerate(agenda):
        x = 3.39 if i < 4 else 14.82
        b += (shape("Kotak-pucat", x, y, 8.5, h, t, radius=0.22, spasi=sp, dy=dy)
              + chip(x - 1.32, y + h / 2 - 0.49, i + 1))
    isi("Agenda", "Agenda", b)

    bagian(1, "Latar belakang", spasi=0.11)

    # 4. Butir + intinya
    isi("Slide berisi butir", "Slide berisi butir",
        ph_outline([(1, "Butir pertama dengan {{istilah kunci}} dan //istilah asing//."),
                    (1, "Butir kedua dengan [[penekanan merah]]."),
                    (2, "Sub-butir memakai tanda emas."),
                    (1, "Butir ketiga, cukup satu gagasan per butir.")])
        + textbox("Catatan-kecil", 1.59, 8.94, 20, 0.6, "Sumber: Penulis, Tahun; Penulis lain, Tahun", spasi=-0.01)
        + intinya(1.59, 9.78, 22.23, "Intinya", "Satu kalimat yang merangkum pesan utama slide ini."),
        layout="AL2T1")

    # 5. Kartu dua kolom
    pert = ["pertama", "kedua", "ketiga"]
    isi("Kartu dua kolom", "Slide dua kolom dengan kartu",
        kartu(1.07, 4.85, 11.22, 0.80, 1.61, "Topik", "Isi kartu pertama. Pakai **tebal** untuk kata yang pen\u00adting.",
              spasi=0.034)
        + kartu(1.07, 7.50, 11.22, 0.71, 1.51, "Kondisi saat ini",
                "Kartu dengan kepala emas untuk konteks atau ca\u00adtatan.", "-emas", spasi=0.023, spasi_judul=0.04)
        + kartu(13.24, 4.85, 11.22, 0.80, 3.59, "Pertanyaan penelitian", "", "-tua")
        + "".join(chip(13.53, y, k + 1, 0.76, "Chip-kecil")
                  + textbox("Teks-kecil", 14.44, y + 0.07, 9.6, 0.6, f"Pertanyaan {pert[k]}.")
                  for k, y in enumerate((5.91, 7.04, 8.18)))
        + kartu(13.24, 9.49, 11.22, 0.68, 0.91, "Keterbatasan", "Kartu merah untuk risiko atau keterbatasan.",
                "-merah", spasi=0.024))

    # 6. Ubin angka
    # (angka, label, warna, geser tegak, spasi antar-kata label): meniru TeX di contoh.pdf
    tiles = [("104", "makalah primer terpilih", "", 0, 0.07), ("12", "label angka kedua", "-tua", 0, 0.075),
             ("6\u2009/\u200917", "rasio atau\nperbandingan", "", 0.13, 0.08), ("0", "temuan negatif", "-merah", 0, 0),
             ("27", "label angka", "-tua", 0, 0), ("3", "label angka", "", 0, 0),
             ("USD\u20097,3 jt", "nilai lebar, huruf\nlebih kecil", "-tua", 0.135, 0.075),
             ("8", "celah riset", "-emas", 0.08, 0.08)]
    b = ""
    for i, (a, l, wcol, dy, sp) in enumerate(tiles):
        r, c = divmod(i, 4)
        b += ubin(2.34 + c * 5.32, 3.58 + r * 4.61, a, l, wcol, lebar=len(a) > 6, dy=dy, spasi=sp)
    isi("Ubin angka", "Temuan utama sekilas", b)

    bagian(2, "Metode", dy=0.08)

    # 8. Diagram alur
    labels = ["Klarifikasi\nRiset", "Studi\nDeskriptif I", "Studi\nPreskriptif", "Studi\nDeskriptif II"]
    sem = ["Semester 1", "Semester 2", "Semester 3–4", "Semester 5–6"]
    xs = [1.88 + k * 5.715 for k in range(4)]
    b = ""
    for k in range(4):
        b += shape("Tahap" if k == 0 else "Tahap-muda", xs[k], 5.12, 5.08, 1.98, labels[k], radius=0.17,
                   dy=0 if k == 0 else -0.07)
        b += textbox("Catatan-kecil", xs[k], 7.38, 5.08, 0.5, sem[k], pstyle="P-tengah")
        if k < 3:
            b += line("Panah", xs[k] + 5.09, 6.11, xs[k + 1] - 0.12, 6.11)
    b += shape("Sorot", 1.64, 4.84, 5.56, 3.25, radius=0.22)
    b += shape("Label-emas", 3.45, 4.06, 1.94, 0.78, "tahap ini", radius=0.11)
    for k in range(3):
        b += kartu(1.03 + k * 8.125, 10.03, 7.22, 0.66, 1.0, f"Luaran {k + 1}",
                   f"Penjelasan luaran {pert[k]}.")
    isi("Diagram alur", "Diagram alur", b)

    # 9. Tabel (objek tabel Impress, gaya booktabs: garis atas, garis tengah tipis, garis bawah)
    rows = [("**Tahap**", "**Jumlah**", "**Sisa**", "**Catatan**"),
            ("Pencarian basis data", "1.250", "1.250", "Scopus, IEEE, ACM"),
            ("Saring judul/abstrak", "−\u2009980", "270", "kriteria inklusi"),
            ("Baca teks lengkap", "−\u2009166", "**104**", "penilaian kualitas")]
    # Posisi dari contoh.pdf: garis di 6,28 / 7,28 / 9,70; teks tiap baris di 6,49 / 7,48 / 8,19 / 8,90.
    isi("Tabel", "Tabel", tabel(5.94, 6.28, [5.02, 2.25, 1.90, 4.35],
                                ([6.49, 7.48, 8.19, 8.90], [6.28, 7.28, 8.14, 8.85, 9.70]), rows, kanan={1, 2}))

    # 10. Penutup
    page("Terima kasih", "Penutup", "AL3T19", ph_title("Penutup", "Terima kasih", 0, 5.5, W, 3.0)
         + nomor(f"{N_ISI}/{N_ISI}"), dp="dp-isi-tetap")


def content_xml():
    build_pages()
    return (f'<?xml version="1.0" encoding="UTF-8"?><office:document-content {NS}>{font_decls()}'
            f'<office:automatic-styles>{CONTENT_AUTO}{"".join(TABEL_GAYA)}{"".join(OTOMATIS.values())}'
            '</office:automatic-styles>'
            '<office:body><office:presentation>'
            f'<presentation:footer-decl presentation:name="ftr1">{escape(FOOTER_TEKS)}</presentation:footer-decl>'
            f'{"".join(PAGES)}</office:presentation></office:body></office:document-content>')


def meta_xml(title):
    return (f'<?xml version="1.0" encoding="UTF-8"?><office:document-meta {NS}><office:meta>'
            f'<dc:title>{escape(title)}</dc:title><meta:generator>build_odp.py</meta:generator>'
            '</office:meta></office:document-meta>')


SETTINGS = (f'<?xml version="1.0" encoding="UTF-8"?><office:document-settings {NS}><office:settings>'
            '<config:config-item-set config:name="ooo:configuration-settings">'
            '<config:config-item config:name="EmbedFonts" config:type="boolean">true</config:config-item>'
            '</config:config-item-set></office:settings></office:document-settings>')


def manifest(mime, fonts):
    entries = "".join(f'<manifest:file-entry manifest:full-path="Fonts/{f}" '
                      'manifest:media-type="application/x-font-otf"/>' for f in fonts)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3">'
            f'<manifest:file-entry manifest:full-path="/" manifest:media-type="{mime}"/>'
            '<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
            '<manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>'
            '<manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>'
            '<manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/>'
            '<manifest:file-entry manifest:full-path="Pictures/itb-logo.png" manifest:media-type="image/png"/>'
            f'{entries}</manifest:manifest>')


def write(path, mime, title, content, styles):
    fonts = [f for f in FONT_FILES if (FONT_DIR / f).exists()]
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), mime, compress_type=zipfile.ZIP_STORED)
        for name, data in (("content.xml", content), ("styles.xml", styles), ("meta.xml", meta_xml(title)),
                           ("settings.xml", SETTINGS), ("META-INF/manifest.xml", manifest(mime, fonts))):
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
        z.write(LOGO, "Pictures/itb-logo.png", compress_type=zipfile.ZIP_STORED)
        for f in fonts:
            z.write(FONT_DIR / f, f"Fonts/{f}", compress_type=zipfile.ZIP_DEFLATED)
    print("tulis", path.name)


RPR = re.compile(r"<a:(rPr|defRPr|endParaRPr)\b([^>]*?)(/>|>.*?</a:\1>)", re.S)


def font_pptx(xml):
    """Di Windows/PowerPoint, FiraSans-Book terdaftar sebagai keluarga 'Fira Sans Book', sedangkan Bold sebagai
    'Fira Sans' (tebal). Teks biasa -> 'Fira Sans Book', teks tebal -> 'Fira Sans'."""
    def ganti(m):
        tebal = 'b="1"' in m.group(2)
        nama = "@TEBAL@" if tebal else f"{FONT} Book"
        return re.sub(f'typeface="{FONT}(:[^"]*)?"', f'typeface="{nama}"', m.group(0))
    xml = RPR.sub(ganti, xml)
    xml = re.sub(f'typeface="{FONT}(:[^"]*)?"', f'typeface="{FONT} Book"', xml)
    return xml.replace('typeface="@TEBAL@"', f'typeface="{FONT}"')


def longgar_tabel(xml, tambah=54000):
    """PowerPoint tidak memakai kelonggaran jarak huruf di kolom terakhir tabel; lebarkan kolom itu 1,5 mm
    (54000 EMU) agar teksnya tidak terbungkus."""
    def kolom(m):
        cols = re.findall(r'<a:gridCol w="(\d+)"', m.group(0))
        akhir = int(cols[-1]) + tambah
        return re.sub(r'(<a:gridCol w=")\d+("[^>]*/?>)(?!.*<a:gridCol)', rf'\g<1>{akhir}\g<2>', m.group(0), flags=re.S)
    def bingkai(m):
        g = m.group(0)
        if "<a:tblGrid>" not in g:
            return g
        g = re.sub(r'(<a:ext cx=")(\d+)', lambda e: f"{e.group(1)}{int(e.group(2)) + tambah}", g, count=1)
        g = re.sub(r"<a:tblGrid>.*?</a:tblGrid>", kolom, g, flags=re.S)
        # Jarak sel 0 tidak ditulis LibreOffice; PowerPoint lalu memakai bawaan 0,25 cm. Tulis eksplisit.
        def sel(t):
            tag = t.group(0)
            for sisi in ("marL", "marR"):
                if f"{sisi}=" not in tag:
                    tag = tag.replace("<a:tcPr", f'<a:tcPr {sisi}="0"', 1)
            return tag
        return re.sub(r"<a:tcPr\b[^>]*>", sel, g)
    return re.sub(r"<p:graphicFrame>.*?</p:graphicFrame>", bingkai, xml, flags=re.S)


def pptx(odp):
    """Ekspor .pptx lewat LibreOffice, lalu betulkan nama font (PowerPoint tidak mengenal akhiran fitur OpenType
    ':onum', jadi di .pptx angkanya angka biasa)."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("lewati .pptx: LibreOffice (soffice) tidak ditemukan")
        return
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([soffice, "--headless", "--convert-to", "pptx", "--outdir", tmp, str(odp)],
                       check=True, capture_output=True)
        src = Path(tmp) / (odp.stem + ".pptx")
        dst = odp.with_suffix(".pptx")
        with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
            for item in zi.infolist():
                data = zi.read(item.filename)
                if item.filename.endswith(".xml"):
                    data = longgar_tabel(font_pptx(data.decode())).encode()
                zo.writestr(item, data)
    print("tulis", dst.name)


if __name__ == "__main__":
    styles = styles_xml()  # dulu: mengisi GAYA_PAD yang dipakai slide contoh
    content = content_xml()
    write(HERE / "contoh-itb.odp", "application/vnd.oasis.opendocument.presentation", "Contoh slide ITB",
          content, styles)
    write(HERE / "tema-itb.otp", "application/vnd.oasis.opendocument.presentation-template", "Tema slide ITB",
          content, styles)
    pptx(HERE / "contoh-itb.odp")
