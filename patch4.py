with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

old = '''    diff_vars = {'gdp', 'defl', 'credit', 'long_yield', 'short_yield'}
    result = {}
    print(f"\\n{COUNTRY_LABELS[c]} — transformation:")
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if name in diff_vars:
            result[name] = s.diff()
            print(f"  {name}: first diff")
        else:
            result[name] = s
            print(f"  {name}: levels")'''

new = '''    result = {}
    print(f"\\n{COUNTRY_LABELS[c]} — transformation (all first diff):")
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        result[name] = s.diff()
        print(f"  {name}: first diff")'''

if old in content:
    content = content.replace(old, new)
    with open('thesis_svar_v2.py', 'w') as f:
        f.write(content)
    print("PATCHED")
else:
    print("NOT FOUND")
