with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

old = '''    result = {}
    print(f"\\n{COUNTRY_LABELS[c]} — stationarity:")
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        p_lev  = adf_pvalue(s)
        p_diff = adf_pvalue(s.diff())
        if p_diff < 0.05:
            result[name] = s
            print(f"  {name}: levels — I(1) confirmed (p_diff={p_diff:.3f})")
        elif p_lev < 0.10:
            result[name] = s
            print(f"  {name}: levels — stationary (p_lev={p_lev:.3f})")
        else:
            result[name] = s
            print(f"  {name}: levels — borderline, kept per I(1) assumption (p_lev={p_lev:.3f})")'''

new = '''    log_level_vars = {'gdp', 'defl', 'credit'}
    result = {}
    print(f"\\n{COUNTRY_LABELS[c]} — transformation:")
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if name in log_level_vars:
            result[name] = s.diff()
            print(f"  {name}: first diff of log-level")
        else:
            result[name] = s
            print(f"  {name}: levels")'''

if old in content:
    content = content.replace(old, new)
    with open('thesis_svar_v2.py', 'w') as f:
        f.write(content)
    print("PATCHED")
else:
    print("NOT FOUND - printing actual block:")
    idx = content.find('result = {}')
    print(repr(content[idx:idx+500]))
