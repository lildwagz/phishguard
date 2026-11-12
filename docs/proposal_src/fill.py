import copy, re, sys
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
sys.path.insert(0, '.')
from content import *

SRC = '/home/zam/projects/MyProject/PhishGuard/docs/Template_Proposal_Project_Kecerdasan_Buatan_UBSI_2026.docx'
OUT = '/home/zam/projects/MyProject/PhishGuard/docs/Proposal_PhishGuard.docx'
d = docx.Document(SRC)
P = d.paragraphs
BODY = next(p for p in P if p.text.startswith('Proposal project mata kuliah'))
BODY_PPR = copy.deepcopy(BODY._p.pPr) if BODY._p.pPr is not None else None


def new_para_before(anchor, text='', kind='p'):
    p = anchor.insert_paragraph_before()
    if kind == 'b':
        p.style = d.styles['List Bullet']
    elif BODY_PPR is not None:
        p._p.insert(0, copy.deepcopy(BODY_PPR))
    if kind == 'p':
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.0)
    if kind == 'b':
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if kind == 'ref':
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-1.27)
    if kind == 'cap':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if kind == 'code':
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
    if text:
        r = p.add_run(text)
        if kind == 'code':
            r.font.name = 'Courier New'; r.font.size = Pt(8.5)
            r._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:hAnsi'), 'Courier New')
        if kind == 'cap':
            r.italic = True; r.font.size = Pt(10)
    return p


def fill_section(heading_text, blocks):
    idx = next(i for i, p in enumerate(d.paragraphs) if p.text.strip() == heading_text and p.style.name.startswith('Heading'))
    h = d.paragraphs[idx]
    nxt = d.paragraphs[idx + 1] if idx + 1 < len(d.paragraphs) else None
    petunjuk = nxt if nxt is not None and nxt.text.strip().startswith('Petunjuk pengisian') else None
    if petunjuk is not None:
        anchor = petunjuk
    else:
        # insert right after the heading: anchor on the element that follows the heading
        anchor = docx.text.paragraph.Paragraph(h._p.getnext(), h._parent) if h._p.getnext() is not None and h._p.getnext().tag == qn('w:p') else None
        if anchor is None:  # heading followed by a table or nothing: put a temp paragraph after heading
            tmp = copy.deepcopy(h._p); h._p.addnext(tmp)
            anchor = docx.text.paragraph.Paragraph(tmp, h._parent)
            for r in list(anchor.runs): r._r.getparent().remove(r._r)
            anchor._p.getparent().remove(anchor._p) if False else None
            created_tmp = True
        else:
            created_tmp = False
    for b in blocks:
        kind = b[0]
        if kind == 'img':
            p = new_para_before(anchor, '', 'cap')
            p.add_run().add_picture(b[1], width=Cm(b[2]))
        elif kind == 'code':
            for line in b[1].split('\n'):
                new_para_before(anchor, line, 'code')
        else:
            new_para_before(anchor, b[1], kind)
    if petunjuk is not None:
        petunjuk._p.getparent().remove(petunjuk._p)
    elif created_tmp:
        anchor._p.getparent().remove(anchor._p)


def remove_petunjuk_after(heading_text):
    idx = next(i for i, p in enumerate(d.paragraphs) if p.text.strip() == heading_text and p.style.name.startswith('Heading'))
    nxt = d.paragraphs[idx + 1]
    if nxt.text.strip().startswith('Petunjuk pengisian'):
        nxt._p.getparent().remove(nxt._p)


def set_cell(cell, text):
    paras = cell.paragraphs
    p = paras[0]
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]: r._r.getparent().remove(r._r)
    else:
        p.add_run(text)
    for extra in paras[1:]:
        extra._p.getparent().remove(extra._p)


def fill_table(t, rows, start=1):
    need = start + len(rows)
    while len(t.rows) < need:
        t._tbl.append(copy.deepcopy(t.rows[-1]._tr))
    while len(t.rows) > need:
        t._tbl.remove(t.rows[-1]._tr)
    for i, vals in enumerate(rows):
        for j, v in enumerate(vals):
            set_cell(t.rows[start + i].cells[j], v)


# ---- cover & title placeholders
for p in d.paragraphs:
    for r in p.runs:
        if '[JUDUL PROJECT APLIKASI AI]' in r.text:
            r.text = r.text.replace('[JUDUL PROJECT APLIKASI AI]', JUDUL.upper() if p.alignment == WD_ALIGN_PARAGRAPH.CENTER else JUDUL)

# ---- pengusul (cover) + tanda tangan ketua
cover = [p for p in d.paragraphs if p.text.startswith('[NIM] [Nama Mahasiswa] (')]
people = [(KETUA, 'Ketua')] + [(a, f'Anggota {i+1}') for i, a in enumerate(ANGGOTA)]
while len(cover) < len(people):  # template has 4 slots; P01 allows 1 ketua + 4 anggota
    new = copy.deepcopy(cover[-1]._p); cover[-1]._p.addnext(new)
    cover.append(docx.text.paragraph.Paragraph(new, cover[-1]._parent))
for par, ((nim, nama), role) in zip(cover, people):
    par.runs[0].text = f'{nim} {nama} ({role})'
    for r in par.runs[1:]: r._r.getparent().remove(r._r)
for p in d.tables[2].rows[1].cells[0].paragraphs:
    for r in p.runs:
        r.text = r.text.replace('[Nama Mahasiswa]', KETUA[1]).replace('[NIM]', KETUA[0])

# ---- header text of the filled copy
for sec in d.sections:
    for hdr in (sec.header, sec.first_page_header, sec.even_page_header):
        for p in hdr.paragraphs:
            for r in p.runs:
                if 'Template Proposal Project' in r.text:
                    r.text = r.text.replace('Template Proposal Project', 'Proposal Project')

# ---- tables
T = d.tables
fill_table(T[0], [(k, v) for k, v in IDENTITAS], start=0)
set_cell(T[3].rows[0].cells[1], KATA_KUNCI); set_cell(T[3].rows[1].cells[1], LUARAN)
fill_table(T[4], FR)
fill_table(T[5], NFR)
for row in T[5].rows:
    row.cells[0].width = Cm(1.9); row.cells[1].width = Cm(2.9); row.cells[2].width = Cm(8.6)
grid = T[5]._tbl.tblGrid.findall(qn('w:gridCol'))
for gc, w in zip(grid, (1.9, 2.9, 8.6)):
    gc.set(qn('w:w'), str(int(w * 567)))
fill_table(T[6], ENDPOINTS)
fill_table(T[7], TESTS)
fill_table(T[8], PERAN)
fill_table(T[9], JADWAL)
fill_table(T[10], RISIKO)
for i, ok in enumerate(CHECKLIST):
    set_cell(T[11].rows[1 + i].cells[0], '[x]' if ok else '[ ]')

# ---- sections
remove_petunjuk_after('DAFTAR ISI')
remove_petunjuk_after('2.2 Analisis Kebutuhan Fungsional')
refs = sorted([b for b in SECTIONS['DAFTAR PUSTAKA']], key=lambda b: b[1].lower())
SECTIONS['DAFTAR PUSTAKA'] = refs
for heading, blocks in SECTIONS.items():
    fill_section(heading, blocks)

d.save(OUT)
left = [p.text[:60] for p in d.paragraphs if 'Petunjuk pengisian' in p.text]
print('saved', OUT, '| petunjuk left:', left)
