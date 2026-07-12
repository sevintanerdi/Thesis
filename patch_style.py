with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

# Add style config after imports
old = """COUNTRIES = ['de', 'es', 'it', 'fr', 'nl']"""

new = """# Plot styling
import matplotlib
matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

COUNTRY_COLORS = {
    'de': '#1f4e79',   # dark navy
    'es': '#c00000',   # deep red
    'it': '#375623',   # dark green
    'fr': '#7030a0',   # purple
    'nl': '#0070c0',   # bright blue
}
COUNTRY_LINESTYLES = {
    'de': '-',
    'es': '--',
    'it': '-.',
    'fr': ':',
    'nl': '-',
}

COUNTRIES = ['de', 'es', 'it', 'fr', 'nl']"""

content = content.replace(old, new)

# Update styles dict
old2 = """periods = range(HORIZON + 1)
styles  = {'de': ('b-','Germany'), 'es': ('r--','Spain'), 'it': ('g-.','Italy'),
           'fr': ('m:','France'),  'nl': ('c-', 'Netherlands')}"""

new2 = """periods = range(HORIZON + 1)
styles  = {
    'de': (COUNTRY_COLORS['de'], COUNTRY_LINESTYLES['de'], 'Germany'),
    'es': (COUNTRY_COLORS['es'], COUNTRY_LINESTYLES['es'], 'Spain'),
    'it': (COUNTRY_COLORS['it'], COUNTRY_LINESTYLES['it'], 'Italy'),
    'fr': (COUNTRY_COLORS['fr'], COUNTRY_LINESTYLES['fr'], 'France'),
    'nl': (COUNTRY_COLORS['nl'], COUNTRY_LINESTYLES['nl'], 'Netherlands'),
}"""

content = content.replace(old2, new2)

# Update Figure 1 - baseline IRF
old3 = """for i, c in enumerate(COUNTRIES):
    for j, vname in enumerate(target_vars):
        ax = axes1[i, j]
        val, err = get_irf_val(results_main[c], vname)
        if val is None:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        else:
            if err is not None:
                ax.fill_between(periods, val-err, val+err, alpha=0.2, color='steelblue')
            ax.plot(periods, val, 'b-', linewidth=2)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4)
        ax.set_title(f'{COUNTRY_LABELS[c]} — {vname.upper()}')
        ax.set_xlabel('Quarters')"""

new3 = """for i, c in enumerate(COUNTRIES):
    color = COUNTRY_COLORS[c]
    ls    = COUNTRY_LINESTYLES[c]
    for j, vname in enumerate(target_vars):
        ax  = axes1[i, j]
        val = get_response(results_main[c], vname)
        if val is None:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.plot(periods, val, color=color, linestyle=ls, linewidth=2)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4, linewidth=0.8)
        ax.set_title(f'{COUNTRY_LABELS[c]} — {vname.upper()}', fontsize=10)
        ax.set_xlabel('Quarters')"""

content = content.replace(old3, new3)

# Update Figure 2 - cross-country comparison
old4 = """for c, (style, label) in styles.items():
    val_nim  = get_response(results_main[c], 'nim')
    val_cet1 = get_response(results_main[c], 'cet1')
    if val_nim  is not None: ax_nim.plot(periods, val_nim,   style, linewidth=2, label=label)
    if val_cet1 is not None: ax_cet1.plot(periods, val_cet1, style, linewidth=2, label=label)"""

new4 = """for c, (color, ls, label) in styles.items():
    val_nim  = get_response(results_main[c], 'nim')
    val_cet1 = get_response(results_main[c], 'cet1')
    if val_nim  is not None: ax_nim.plot(periods, val_nim,   color=color, linestyle=ls, linewidth=2, label=label)
    if val_cet1 is not None: ax_cet1.plot(periods, val_cet1, color=color, linestyle=ls, linewidth=2, label=label)"""

content = content.replace(old4, new4)

# Update Figure 3 - robustness precovid
old5 = """for ax, c in zip(axes3, COUNTRIES):
    val_f = get_response(results_main[c], 'nim')
    if val_f is not None:
        ax.plot(periods, val_f, 'b-', linewidth=2, label='Full sample')
    if results_precovid[c]:
        val_r = get_response(results_precovid[c], 'nim')
        if val_r is not None:
            ax.plot(periods, val_r, 'r--', linewidth=2, label='Pre-COVID')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

new5 = """for ax, c in zip(axes3, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val_f = get_response(results_main[c], 'nim')
    if val_f is not None:
        ax.plot(periods, val_f, color=color, linestyle='-', linewidth=2, label='Full sample')
    if results_precovid[c]:
        val_r = get_response(results_precovid[c], 'nim')
        if val_r is not None:
            ax.plot(periods, val_r, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Pre-COVID')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

content = content.replace(old5, new5)

# Update Figure 4 - robustness SSR
old6 = """for ax, c in zip(axes4, COUNTRIES):
    val_d = get_response(results_main[c], 'nim')
    if val_d is not None:
        ax.plot(periods, val_d, 'b-', linewidth=2, label='∆DFR (baseline)')
    if results_ssr[c]:
        val_s = get_response(results_ssr[c], 'nim')
        if val_s is not None:
            ax.plot(periods, val_s, 'r--', linewidth=2, label='∆SSR (robustness)')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

new6 = """for ax, c in zip(axes4, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val_d = get_response(results_main[c], 'nim')
    if val_d is not None:
        ax.plot(periods, val_d, color=color, linestyle='-', linewidth=2, label='∆DFR (baseline)')
    if results_ssr[c]:
        val_s = get_response(results_ssr[c], 'nim')
        if val_s is not None:
            ax.plot(periods, val_s, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='∆SSR (robustness)')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

content = content.replace(old6, new6)

# Update Figure 5 - robustness lags
old7 = """for ax, c in zip(axes5, COUNTRIES):
    val4 = get_response(results_main[c], 'nim')
    if val4 is not None:
        ax.plot(periods, val4, 'b-', linewidth=2, label='4 lags')
    if results_lags8[c]:
        val8 = get_response(results_lags8[c], 'nim')
        if val8 is not None:
            ax.plot(periods, val8, 'r--', linewidth=2, label='8 lags')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

new7 = """for ax, c in zip(axes5, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val4 = get_response(results_main[c], 'nim')
    if val4 is not None:
        ax.plot(periods, val4, color=color, linestyle='-', linewidth=2, label='4 lags')
    if results_lags8[c]:
        val8 = get_response(results_lags8[c], 'nim')
        if val8 is not None:
            ax.plot(periods, val8, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='8 lags')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)"""

content = content.replace(old7, new7)

with open('thesis_svar_v2_styled.py', 'w') as f:
    f.write(content)

checks = [old2 in content, old3 in content, old4 in content]
print("Replacements done. Remaining old strings:", checks)
