"""Generate c_vs_v2.png — training-free comparison across all three corpora.
Run from BTech_Latex_Report/: ../.venv/bin/python deck_assets/gen_vs_v2.py"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BG = '#FCFBF7'; INK = '#1A1A1A'; GREEN = '#146B3A'; GOLD = '#C9A227'
MUT = '#6B7280'; PUB = '#8B8FA3'; FT_FC = '#EDEAE2'; FT_EC = '#8A8578'; HAIR = '#E5E1D8'
plt.rcParams.update({'font.family': 'Helvetica Neue', 'text.color': INK,
                     'axes.edgecolor': HAIR, 'xtick.color': MUT, 'ytick.color': INK,
                     'figure.facecolor': BG, 'axes.facecolor': BG})

fig, axes = plt.subplots(1, 3, figsize=(10.6, 4.5), dpi=300,
                         gridspec_kw={'width_ratios': [1.15, 1.0, 1.0]})
fig.subplots_adjust(left=0.175, right=0.985, top=0.86, bottom=0.13, wspace=0.52)

def bar_panel(ax, rows, xlim, panel_title):
    """rows: list of (label, value, color, hatch) top->bottom."""
    y = list(range(len(rows) - 1, -1, -1))
    for yi, (label, val, color, hatch) in zip(y, rows):
        ax.barh(yi, val, height=0.62, color=color,
                edgecolor=FT_EC if hatch else 'none', hatch=hatch, linewidth=0.8,
                zorder=3)
        if val > xlim * 0.92:
            ax.text(val - xlim * 0.015, yi, f'{val:.1f}', va='center', ha='right',
                    fontsize=8.6, color='white', fontweight='bold')
        else:
            ax.text(val + xlim * 0.015, yi, f'{val:.1f}', va='center', ha='left',
                    fontsize=8.6, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.2)
    ax.set_xlim(0, xlim)
    ax.set_title(panel_title, fontsize=10.5, color=MUT, pad=10, loc='left')
    ax.grid(axis='x', color=HAIR, linewidth=0.6, zorder=0)
    ax.tick_params(axis='x', labelsize=7.5, length=0)
    ax.tick_params(axis='y', length=0)
    for sp in ['top', 'right', 'left']:
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(HAIR)

# --- Panel 1: IL-PCSR (MAP) ---
bar_panel(axes[0], [
    ('statutes\npublished best',      21.82, PUB,  None),
    ('statutes\nthis work',           25.20, GREEN, None),
    ('precedents\npublished best',    43.98, PUB,  None),
    ('precedents\nthis work',         39.90, GOLD,  None),
    ('statutes\nfine-tuned',          61.06, FT_FC, '....'),
    ('precedents\nfine-tuned',        54.43, FT_FC, '....'),
], 72, 'IL-PCSR  ·  MAP')

# --- Panel 2: BSARD (R@100) ---
bar_panel(axes[1], [
    ('published\nBM25, zero-shot',    40.13, PUB,  None),
    ('published\nbi-encoder',         49.41, PUB,  None),
    ('this work\nQwen3-4B',           67.67, GREEN, None),
    ('fine-tuned',                    74.78, FT_FC, '....'),
], 100, 'BSARD  ·  R@100')

# --- Panel 3: AILA (MAP) ---
ax = bar_panel(axes[2], [
    ('statutes\npublished best',      15.66, PUB,  None),
    ('statutes\nthis work',           45.91, GREEN, None),
    ('precedents\npublished best',    14.92, PUB,  None),
    ('precedents\nthis work',         12.82, GOLD,  None),
], 55, 'AILA  ·  MAP')

fig.legend(handles=[
    Patch(facecolor=PUB, label='training-free reference'),
    Patch(facecolor=GREEN, label='this work — statutes'),
    Patch(facecolor=GOLD, label='this work — precedents'),
    Patch(facecolor=FT_FC, edgecolor=FT_EC, hatch='....',
          label='fine-tuned on benchmark'),
], loc='upper center', ncol=4, frameon=False, fontsize=8.6,
   bbox_to_anchor=(0.5, 1.0), handlelength=1.4, handleheight=0.9, columnspacing=1.5)

fig.text(0.02, 0.015,
    'IL-PCSR: published rows are test split, this work dev split.   '
    'BSARD: published macro R@100, this work micro.   '
    'AILA: published rows are FIRE 2019 track bests (macro MAP); this work micro MAP@100.',
    fontsize=7.2, color=MUT)

fig.savefig('deck_assets/c_vs_v2.png', facecolor=BG)
print('saved deck_assets/c_vs_v2.png')
