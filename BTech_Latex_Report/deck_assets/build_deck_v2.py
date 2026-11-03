"""Build Legal_RAG_Defense.pptx — run from BTech_Latex_Report/ with ../.venv/bin/python."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BG = 'FCFBF7'; INK = '1A1A1A'; GREEN = '146B3A'; GOLD = 'C9A227'
MUT = '6B7280'; HAIR = 'E5E1D8'; PAPER = 'F4F1EA'
F = 'Helvetica Neue'

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def slide():
    s = prs.slides.add_slide(BLANK)
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = RGBColor.from_string(BG)
    r.line.fill.background(); r.shadow.inherit = False
    return s

def txt(s, x, y, w, h, text, size=13, color=INK, bold=False, align=PP_ALIGN.LEFT,
        font=F, italic=False, spacing=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ln in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing: p.line_spacing = spacing
        r = p.add_run(); r.text = ln
        r.font.name = font; r.font.size = Pt(size); r.font.bold = bold
        r.font.italic = italic; r.font.color.rgb = RGBColor.from_string(color)
    return tb

def rect(s, x, y, w, h, fill, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    if line: sh.line.color.rgb = RGBColor.from_string(line); sh.line.width = Pt(lw)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    return sh

def pagenum(s, n):
    txt(s, 12.55, 7.05, 0.6, 0.3, str(n), size=9, color=MUT, align=PP_ALIGN.RIGHT)

def title(s, text, size=30):
    txt(s, 0.7, 0.55, 12.0, 0.75, text, size=size, bold=True)

def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w: kw['width'] = Inches(w)
    if h: kw['height'] = Inches(h)
    return s.shapes.add_picture(path, Inches(x), Inches(y), **kw)

def arrow(s, x, y, w=0.55, h=0.28):
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = RGBColor.from_string(MUT)
    a.line.fill.background(); a.shadow.inherit = False
    return a

def chip(s, x, y, w, h, text, fill=INK, tc='FFFFFF', size=13, bold=True,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    sh.line.fill.background(); sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.03); tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, ln in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = ln
        r.font.name = F; r.font.size = Pt(size); r.font.bold = bold
        r.font.color.rgb = RGBColor.from_string(tc)
    return sh

# ============ S1 TITLE ============
s = slide()
rect(s, 0.7, 2.05, 0.55, 0.055, GREEN)
txt(s, 0.7, 2.35, 11.9, 1.6, 'Agentic RAG Framework for Automated\nLegal Case Analysis & Decision Support',
    size=40, bold=True, spacing=1.02)
txt(s, 0.7, 4.35, 11.5, 0.8,
    'A staged retrieval ablation on IL-PCSR, external validation on BSARD and AILA,\nand a citation-verified agentic case-analysis assistant.',
    size=15, color=MUT, spacing=1.15)
rect(s, 0.7, 5.55, 11.9, 0.012, HAIR)
txt(s, 0.7, 5.8, 11.9, 0.4,
    'Samudraneel Sarker   Patil Sakshi   Manpreet Kaur   Nikhil Kumar        Mentor: Dr Vibhav Prakash Singh',
    size=13, color=INK)
txt(s, 0.7, 6.15, 11.9, 0.35, 'github.com/sakshi-patil-1111/legal-rag', size=11, color=MUT)

# ============ S2 PROBLEM ============
s = slide(); pagenum(s, 2); title(s, 'The problem')
txt(s, 0.7, 1.95, 11.9, 1.5,
    'Ask a chatbot the punishment for murder and it will produce a confident section number.',
    size=24, spacing=1.2)
txt(s, 0.7, 3.35, 11.9, 1.2,
    'Nothing in the output tells a reader whether that citation is real.',
    size=24, bold=True, spacing=1.2)
txt(s, 0.7, 4.95, 11.9, 1.4,
    'In legal work, where lawyers and judges may come to depend on AI, fabricated citations and hallucinations are a critical risk.',
    size=24, spacing=1.3)

# ============ S3 GAP ============
s = slide(); pagenum(s, 3); title(s, 'The gap')
txt(s, 0.7, 1.75, 5.6, 0.35, 'Published state of the art', size=14, color=MUT)
txt(s, 0.7, 2.25, 5.6, 2.4,
    'Best rows on every legal benchmark are trained on that benchmark.\n\nGraph nets on IL-PCSR labels.\nFine-tuned bi-encoders on BSARD pairs.',
    size=17, spacing=1.3)
rect(s, 6.62, 1.8, 0.012, 4.3, HAIR)
txt(s, 6.95, 1.75, 5.6, 0.35, 'The corpus', size=14, color=MUT)
txt(s, 6.95, 2.25, 5.6, 2.4,
    'New judgments arrive every day.\nNew acts replace old ones.\n\nA system that needs retraining\nis permanently behind.',
    size=17, spacing=1.3)
rect(s, 0.7, 5.15, 11.9, 1.15, GREEN)
txt(s, 1.0, 5.42, 11.4, 0.6, 'Goal: competitive with published systems, without benchmark-specific training.',
    size=18, color='FFFFFF', bold=True)

# ============ S4 OBJECTIVES ============
s = slide(); pagenum(s, 4); title(s, 'Research questions')
qs = ['Which retrieval legs suit statutes, and which suit precedents?',
      'Which pipeline stages earn their place: chunking, fusion, reranking?',
      'Do query interventions survive several-thousand-word inputs?',
      'What does an agentic controller add that a fixed pipeline cannot?']
for i, q in enumerate(qs):
    yy = 1.85 + i * 1.05
    txt(s, 0.7, yy, 1.0, 0.6, f'0{i+1}', size=26, color=GOLD, bold=True)
    txt(s, 1.75, yy + 0.08, 10.8, 0.55, q, size=17)
    if i < 3: rect(s, 1.75, yy + 0.82, 10.8, 0.012, HAIR)

# ============ S5 DATA ============
s = slide(); pagenum(s, 5); title(s, 'Evaluation corpora')
cols = [('IL-PCSR', 'PRIMARY', '936 statutes\n3,183 precedents\n627 dev queries', 'Indian, English'),
        ('AILA', 'TRANSFER', '197 statutes\n2,914 precedents\n50 queries', 'Indian, entity-masked'),
        ('BSARD', 'TRANSFER', '22,633 articles\n222 test questions', 'Belgian, French')]
for i, (nm, role, stats, note) in enumerate(cols):
    x = 0.7 + i * 4.12
    rect(s, x, 1.85, 3.7, 3.6, 'FFFFFF', HAIR)
    rect(s, x, 1.85, 3.7, 0.09, GREEN if i == 0 else MUT)
    txt(s, x + 0.3, 2.15, 3.1, 0.4, nm, size=20, bold=True)
    txt(s, x + 0.3, 2.62, 3.1, 0.3, role, size=10, color=GREEN if i == 0 else MUT, bold=True)
    txt(s, x + 0.3, 3.1, 3.1, 1.6, stats, size=15, spacing=1.35)
    txt(s, x + 0.3, 4.85, 3.1, 0.35, note, size=11, color=MUT)
txt(s, 0.7, 5.85, 11.9, 0.4, 'All three are evaluated with the same configuration and no retraining.',
    size=14, color=MUT)

# ============ S6 MACHINERY ============
s = slide(); pagenum(s, 6); title(s, 'Retrieval pipeline')
steps = ['Case text\n(~3,600 words)', 'Retriever', 'Reranker', 'Generator', 'Answer']
labels = ['long legal query', 'which leg?', 'does it help?', 'grounded output', 'cited dossier']
x = 0.7
for i, st in enumerate(steps):
    chip(s, x, 3.0, 1.9, 0.85, st, fill=INK if i in (0, 4) else PAPER,
         tc='FFFFFF' if i in (0, 4) else INK, size=12.5, bold=True)
    txt(s, x, 4.0, 1.9, 0.5, labels[i], size=10.5, color=MUT, align=PP_ALIGN.CENTER)
    x += 1.9
    if i < 4: arrow(s, x + 0.12, 3.3); x += 0.72
txt(s, 0.7, 4.9, 11.9, 0.5, 'Few of these choices have been measured on long legal queries.',
    size=15, color=MUT)

# ============ S7 METHOD ============
s = slide(); pagenum(s, 7); title(s, 'Experimental setup')
stages = [('A', 'lexical legs', 'BM25 n-grams,\nchunking'), ('B', 'dense legs', 'SAILER to\nQwen3-4B'),
          ('C', 'fusion', 'RRF over\nbest legs'), ('D', 'second stage', 'cross-encoder,\nLLM rerank'),
          ('E', 'query surgery', 'roles, PRF,\nsummary'), ('F', 'agent', 'route, reflect,\nsynthesise')]
x = 0.7
for i, (ltr, nm, sub) in enumerate(stages):
    chip(s, x, 2.9, 1.72, 1.0, f'{ltr}\n{nm}', fill=INK if i < 5 else GREEN, size=12, bold=True)
    txt(s, x, 4.05, 1.72, 0.65, sub, size=9.5, color=MUT, align=PP_ALIGN.CENTER)
    x += 1.72
    if i < 5: arrow(s, x + 0.03, 3.3, 0.32, 0.22); x += 0.36
txt(s, 0.7, 5.1, 11.9, 0.5, 'Each stage varies one component; every arm is evaluated on the same 627-query dev split.',
    size=15, color=MUT)

# ============ S8-S10: chart slides ============
def chart_slide(num, ttl, img, w, cx, line):
    s = slide(); pagenum(s, num); title(s, ttl)
    pic(s, f'deck_assets/{img}', cx, 1.55, w=w)
    txt(s, 0.7, 5.7, 11.9, 0.8, line, size=16)

chart_slide(8, 'Lexical retrieval', 'c_bm25_v2.png', 10.6, 1.35,
            'MAP on the dev split. 5-gram phrases are the strongest precedent retriever; they do not transfer to statutes.')
chart_slide(9, 'Dense encoders', 'c_dense_v2.png', 10.6, 1.35,
            'MAP on the dev split. Short-context encoders see only the first page of a 3,600-word query.')
chart_slide(10, 'Fusion and second-stage reranking', 'c_rerank.png', 10.4, 1.45,
            'LLM listwise rerank gains 7.3 MAP and 12.0 MRR on statutes; cross-encoder collapse is a context failure.')
chart_slide(11, 'Query interventions', 'c_query.png', 10.1, 1.6,
            'Precedent MAP against the unmodified query. All interventions reduce it.')

# ============ S11 VERDICT ============
s = slide(); pagenum(s, 12); title(s, 'The two tasks differ')
rect(s, 0.7, 1.9, 5.75, 3.1, 'FFFFFF', HAIR); rect(s, 0.7, 1.9, 0.09, 3.1, GREEN)
txt(s, 1.05, 2.2, 5.1, 0.4, 'STATUTE RETRIEVAL', size=12, color=GREEN, bold=True)
txt(s, 1.05, 2.7, 5.1, 0.5, 'is semantic', size=26, bold=True)
txt(s, 1.05, 3.4, 5.1, 1.4, 'Dense legs win.\nQwen3-4B doubles the BM25 unigram MAP\n(19.79 vs 9.57 on the dev split).',
    size=13.5, color=MUT, spacing=1.3)
rect(s, 6.85, 1.9, 5.75, 3.1, 'FFFFFF', HAIR); rect(s, 6.85, 1.9, 0.09, 3.1, GOLD)
txt(s, 7.2, 2.2, 5.1, 0.4, 'PRECEDENT RETRIEVAL', size=12, color=GOLD, bold=True)
txt(s, 7.2, 2.7, 5.1, 0.5, 'is lexical', size=26, bold=True)
txt(s, 7.2, 3.4, 5.1, 1.4, 'Citation phrases decide relevance.\nFive-gram BM25 doubles the best dense MAP.\nOn entity-masked AILA text, 4B dense overtakes it.',
    size=13.5, color=MUT, spacing=1.3)
txt(s, 0.7, 5.5, 11.9, 0.5, 'Fusion improves ranking only when the two legs are already competitive.',
    size=16, bold=True)

# ============ S12-S13: external validation ============
chart_slide(13, 'External validation', 'c_transfer.png', 10.6, 1.35,
            'R@100 on held-out corpora, zero-shot. Statute recall reaches 100 on AILA at 4B.')
chart_slide(14, 'Comparison with published systems', 'c_vs_v2.png', 10.6, 1.35,
            'Best training-free statute score on every corpus; the dotted tier alone sits higher, and it is benchmark-trained.')

# ============ S14 AGENT ============
s = slide(); pagenum(s, 15); title(s, 'Agent evaluation')
stages = ['Route', 'Retrieve', 'Reflect', 'Synthesise', 'Validate']
x = 0.7
for i, st in enumerate(stages):
    chip(s, x, 1.7, 1.95, 0.6, st, fill=INK if i != 4 else GREEN, size=13)
    x += 1.95
    if i < 4: arrow(s, x + 0.12, 1.86, 0.4, 0.24); x += 0.62
pic(s, 'deck_assets/c_agent.png', 0.7, 2.9, w=7.9)
for i, (v, l) in enumerate([('49/50', 'complete dossiers'), ('167', 'citations emitted'),
                            ('0', 'invalid after validation')]):
    yy = 3.0 + i * 1.15
    txt(s, 9.0, yy, 3.5, 0.55, v, size=30, bold=True, color=GREEN)
    txt(s, 9.0, yy + 0.55, 3.5, 0.4, l, size=12, color=MUT)
txt(s, 0.7, 6.35, 11.9, 0.5, 'LLM calls help synthesis and citation validation; LLM-written queries hurt retrieval.',
    size=15, bold=True)
txt(s, 9.0, 6.5, 3.6, 0.3, 'single-shot: 627 dev queries; agent arms: 50', size=10, color=MUT)

# ============ S15 DESIGN ============
def down_arrow(s, x, y, w=0.3, h=0.34):
    a = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = RGBColor.from_string(MUT)
    a.line.fill.background(); a.shadow.inherit = False
    return a

s = slide(); pagenum(s, 16); title(s, 'Derived retrieval design')
chip(s, 0.7, 2.75, 1.7, 1.1, 'case\ntext', fill=INK, size=13)
# splitter arrows from case text into both lanes
arrow(s, 2.5, 2.28, 0.5, 0.24)
arrow(s, 2.5, 4.0, 0.5, 0.24)
# statute lane
rect(s, 3.15, 1.8, 6.55, 1.45, 'FFFFFF', HAIR); rect(s, 3.15, 1.8, 0.09, 1.45, GREEN)
txt(s, 3.45, 1.95, 3.4, 0.32, 'STATUTE LEG', size=11, color=GREEN, bold=True)
chip(s, 3.45, 2.35, 1.8, 0.7, 'BM25\ncontext-prepend', fill=PAPER, tc=INK, size=10.5, bold=False)
txt(s, 5.33, 2.53, 0.3, 0.3, '+', size=16, color=MUT)
chip(s, 5.68, 2.35, 1.55, 0.7, 'Qwen3\n4B dense', fill=GREEN, size=10.5)
arrow(s, 7.32, 2.56, 0.4, 0.22)
chip(s, 7.82, 2.35, 1.7, 0.7, 'RRF then\nLLM rerank', fill=PAPER, tc=INK, size=10.5, bold=False)
# precedent lane
rect(s, 3.15, 3.52, 6.55, 1.45, 'FFFFFF', HAIR); rect(s, 3.15, 3.52, 0.09, 1.45, GOLD)
txt(s, 3.45, 3.67, 3.4, 0.32, 'PRECEDENT LEG', size=11, color=GOLD, bold=True)
chip(s, 3.45, 4.07, 2.3, 0.7, '5-gram BM25\nwhole document', fill=PAPER, tc=INK, size=10.5, bold=False)
txt(s, 5.95, 4.27, 3.6, 0.3, 'single leg, no fusion', size=11, color=MUT)
# convergence into synthesis column
arrow(s, 9.82, 2.6, 0.5, 0.24)
arrow(s, 9.82, 3.95, 0.5, 0.24)
chip(s, 10.45, 2.15, 2.2, 0.8, 'LLM\nsynthesis', fill=INK, size=12)
down_arrow(s, 11.4, 3.05)
chip(s, 10.45, 3.5, 2.2, 0.8, 'citation\nvalidation', fill=GREEN, size=12)
down_arrow(s, 11.4, 4.4)
chip(s, 10.45, 4.85, 2.2, 0.8, 'grounded\ndossier', fill=INK, size=12)
txt(s, 0.7, 5.95, 11.9, 0.5, 'Each leg uses the configuration that measured best for its task.',
    size=15, color=MUT)

# ============ S16 DEMO ============
s = slide(); pagenum(s, 17); title(s, 'Demo application')
pic(s, '../demo_app/screenshots/dossier_bns_actual.png', 6.9, 1.55, w=6.1)
txt(s, 6.9, 4.85, 6.1, 0.7, 'Dossier for a BNS murder query: issue statement,\ngrounded sections with relevance, verified citations.',
    size=11.5, color=MUT, spacing=1.2)
txt(s, 0.7, 1.8, 5.6, 0.4, 'What you can ask it', size=15, bold=True)
for i, q in enumerate(['Tenant stops paying rent and claims adverse possession. Remedies?',
                       'What statutes apply to murder under the BNS?',
                       'Anticipatory bail: which precedents control?',
                       'Cheque dishonour under section 138 NI Act?']):
    yy = 2.4 + i * 0.78
    rect(s, 0.7, yy, 0.06, 0.52, GOLD)
    txt(s, 0.95, yy + 0.05, 5.4, 0.6, q, size=13, spacing=1.1)
txt(s, 0.7, 5.9, 5.6, 0.9, 'Returns a dossier of applicable statutes,\nprecedents and verified citations.',
    size=13.5, color=MUT, spacing=1.25)

# ============ S17 EXAMPLE RUNS ============
s = slide(); pagenum(s, 18); title(s, 'Example runs')
runs = [
    ('"What statutes apply to murder under the BNS?"',
     'Retrieves IPC murder sections, flags that BNS is not in the corpus, links indiacode.nic.in. Cites Bachan Singh v. State of Punjab.', GREEN),
    ('"Landlord wants to evict a tenant claiming adverse possession."',
     'States no governing eviction statute was retrieved; returns adverse-possession precedents including P.T. Munichikkanna Reddy v. Revamma (2020).', GREEN),
    ('"Supplier delivered defective goods; buyer wants refund plus damages."',
     'Finds only a partial analogy (Indus Airways, Section 138 NI Act) and reports the evidence as insufficient rather than inventing support.', GOLD),
    ('"quantum entanglement pasta recipe for my bicycle"',
     'Refuses: "no discernible legal issue." Zero citations emitted rather than fabricated ones.', GOLD)]
for i, (q, a, c) in enumerate(runs):
    yy = 1.7 + i * 1.28
    rect(s, 0.7, yy, 11.9, 1.1, 'FFFFFF', HAIR)
    rect(s, 0.7, yy, 0.09, 1.1, c)
    txt(s, 1.05, yy + 0.14, 11.2, 0.42, q, size=14.5, bold=True)
    txt(s, 1.05, yy + 0.58, 11.2, 0.42, a, size=12.5, color=MUT)

# ============ S18 CLOSE ============
s = slide(); pagenum(s, 19)
rect(s, 0.7, 2.0, 0.55, 0.055, GREEN)
txt(s, 0.7, 2.3, 11.9, 0.8, 'Summary', size=34, bold=True)
pts = ['No component is trained on a benchmark.',
       'Statutes and precedents need different retrievers; fusion is conditional.',
       'The same configuration transfers to AILA and BSARD unchanged.',
       'The assembled system is running as a citation-verified web application.']
for i, pt in enumerate(pts):
    yy = 3.4 + i * 0.62
    txt(s, 0.7, yy, 0.4, 0.4, f'{i+1}.', size=15, color=GREEN, bold=True)
    txt(s, 1.2, yy + 0.02, 11.0, 0.4, pt, size=15)
rect(s, 0.7, 6.0, 11.9, 0.012, HAIR)
txt(s, 0.7, 6.25, 11.9, 0.4, 'Thank you.', size=17, bold=True)
txt(s, 0.7, 6.7, 11.9, 0.4, 'github.com/sakshi-patil-1111/legal-rag', size=11, color=MUT)

# ============ A1 APPENDIX: dev results ============
def table_slide(num, ttl, headers, rows, col_w, note=None):
    s = slide(); pagenum(s, num); title(s, ttl)
    n_r, n_c = len(rows) + 1, len(headers)
    tbl = s.shapes.add_table(n_r, n_c, Inches(0.9), Inches(1.7),
                             Inches(sum(col_w)), Inches(0.42 * n_r)).table
    tbl.first_row = True; tbl.horz_banding = False
    for j, wd in enumerate(col_w): tbl.columns[j].width = Inches(wd)
    for j, h in enumerate(headers):
        c = tbl.cell(0, j); c.text = h
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(PAPER)
        p = c.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(12); p.runs[0].font.bold = True
        p.runs[0].font.name = F; p.runs[0].font.color.rgb = RGBColor.from_string(INK)
        p.alignment = PP_ALIGN.RIGHT if j else PP_ALIGN.LEFT
        c.margin_left = c.margin_right = Inches(0.1)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = tbl.cell(i + 1, j); c.text = str(v)
            c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string('FFFFFF')
            p = c.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(13); p.runs[0].font.name = F
            p.runs[0].font.bold = (j == 0)
            p.runs[0].font.color.rgb = RGBColor.from_string(INK)
            p.alignment = PP_ALIGN.RIGHT if j else PP_ALIGN.LEFT
            c.margin_left = c.margin_right = Inches(0.1)
    if note:
        txt(s, 0.9, 1.85 + 0.42 * n_r, 11.5, 0.4, note, size=11.5, color=MUT)
    return s

table_slide(20, 'Backup: first-stage results, dev split',
    ['Configuration', 'LSR MAP', 'LSR MRR', 'PCR MAP', 'PCR MRR'],
    [['BM25 unigram, whole doc', '9.57', '20.55', '18.41', '30.78'],
     ['BM25, recursive-512', '12.87', '29.38', '19.75', '33.03'],
     ['BM25 2-gram, recursive-512', '12.59', '30.77', '27.11', '43.68'],
     ['BM25 5-gram, whole doc', 'n/a', 'n/a', '39.90', '57.28'],
     ['BGE-base, 512-token', '6.72', '14.73', '5.73', '10.00'],
     ['Legal-Embed', '9.01', '19.35', '6.74', '11.52'],
     ['SAILER', '0.12', '0.47', '0.04', '0.16'],
     ['Qwen3-Embedding-0.6B', '15.16', '30.93', '17.18', '27.18'],
     ['Qwen3-Embedding-4B', '19.79', '37.38', '19.65', '29.91'],
     ['RRF: 5-gram + Qwen3-4B', '19.12', '40.53', '31.60', '46.42']],
    [4.6, 1.6, 1.6, 1.6, 1.6],
    note='627 dev queries, micro-averaged. RRF row fuses the best leg of each family.')

table_slide(21, 'Backup: external validation',
    ['Corpus / config', 'R@100', 'MAP@100'],
    [['BSARD  ·  BM25 + context', '41.23', '17.31'],
     ['BSARD  ·  Qwen3-0.6B', '51.65', '26.71'],
     ['BSARD  ·  Qwen3-4B', '67.67', '36.91'],
     ['AILA statutes  ·  BM25', '50.23', '8.07'],
     ['AILA statutes  ·  Qwen3-0.6B', '96.77', '41.64'],
     ['AILA statutes  ·  Qwen3-4B', '100.0', '45.91'],
     ['AILA precedents  ·  BM25', '33.85', '10.46'],
     ['AILA precedents  ·  Qwen3-0.6B', '37.44', '7.69'],
     ['AILA precedents  ·  Qwen3-4B', '44.10', '12.82']],
    [7.6, 2.0, 2.0],
    note='Zero-shot on both corpora; published zero-shot BSARD rows: BM25 40.13, bi-encoder 49.41.')

prs.save('Legal_RAG_Defense_v2.pptx')
print('saved', len(prs.slides._sldIdLst), 'slides')
