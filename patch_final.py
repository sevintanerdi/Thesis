with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

changes_made = []

# 1. Add credit to irf_baseline target_vars
old1 = "target_vars = ['nim', 'cet1', 'long_yield', 'gdp']"
new1 = "target_vars = ['nim', 'cet1', 'long_yield', 'credit', 'gdp']"
if old1 in content:
    content = content.replace(old1, new1)
    changes_made.append("Added credit to irf_baseline.png panels")
else:
    print("WARNING: could not find target_vars line - check manually")

# 2. Insert timeseries figure code right before "periods = range(HORIZON + 1)"
timeseries_code = '''
fig0, axes0 = plt.subplots(3, 2, figsize=(14, 14))
fig0.suptitle('Key Variables: All Countries (2015Q1-present)', fontsize=13, fontweight='bold')

ax_dfr = axes0[0, 0]
ax_dfr.plot(raw['de'].index, raw['de']['dfr'], color='black', linewidth=2)
ax_dfr.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax_dfr.set_title('ECB Deposit Facility Rate (%)')
ax_dfr.set_xlabel('Date')

panel_map = [
    (axes0[0, 1], 'nim', 'Net Interest Margin (%)'),
    (axes0[1, 0], 'cet1', 'CET1 Capital Ratio (%)'),
    (axes0[1, 1], 'long_yield', '10Y Government Bond Yield (%)'),
    (axes0[2, 0], 'credit', 'Credit (100 x log level, EUR mn)'),
    (axes0[2, 1], 'gdp', 'Real GDP (100 x log level)'),
]

for ax, varname, title in panel_map:
    for c in COUNTRIES:
        df_c = raw[c]
        col = varname if varname == 'long_yield' else f'{varname}_{c}'
        if col in df_c.columns:
            ax.plot(df_c.index, df_c[col], color=COUNTRY_COLORS[c], linestyle=COUNTRY_LS[c],
                    linewidth=1.8, label=COUNTRY_LABELS[c])
    ax.set_title(title)
    ax.set_xlabel('Date')
    if varname == 'nim':
        ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('timeseries.png', dpi=300, bbox_inches='tight')
plt.show()
print("timeseries.png saved")

'''

marker = "periods = range(HORIZON + 1)"
if marker in content:
    content = content.replace(marker, timeseries_code.strip('\n') + "\n\n" + marker, 1)
    changes_made.append("Inserted timeseries.png figure code")
else:
    print("WARNING: could not find 'periods = range(HORIZON + 1)' marker - check manually")

with open('thesis_svar_v2.py', 'w') as f:
    f.write(content)

print("\nChanges applied:")
for c in changes_made:
    print(f"  - {c}")
