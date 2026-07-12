with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

old = """            ax.plot(periods, val, color=color, linestyle=ls, linewidth=2.5)
            ax.fill_between(periods, val, 0, alpha=0.08, color=color)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4, linewidth=0.8)"""

new = """            ax.plot(periods, val, color=color, linestyle=ls, linewidth=2.5)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4, linewidth=0.8)"""

if old in content:
    content = content.replace(old, new)
    with open('thesis_svar_v2.py', 'w') as f:
        f.write(content)
    print("PATCHED")
else:
    print("NOT FOUND")
