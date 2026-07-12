with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

old = """for i, c in enumerate(COUNTRIES):
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

new = """for i, c in enumerate(COUNTRIES):
    color = COUNTRY_COLORS[c]
    ls    = COUNTRY_LINESTYLES[c]
    for j, vname in enumerate(target_vars):
        ax  = axes1[i, j]
        val = get_response(results_main[c], vname)
        if val is None:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.plot(periods, val, color=color, linestyle=ls, linewidth=2.5)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4, linewidth=0.8)
            ax.fill_between(periods, val, 0, alpha=0.08, color=color)
        ax.set_title(f'{COUNTRY_LABELS[c]} — {vname.upper()}', fontsize=10,
                     color=color, fontweight='bold')
        ax.set_xlabel('Quarters')"""

if old in content:
    content = content.replace(old, new)
    with open('thesis_svar_v2.py', 'w') as f:
        f.write(content)
    print("PATCHED")
else:
    print("NOT FOUND")
