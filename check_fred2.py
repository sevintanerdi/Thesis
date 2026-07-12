import requests

ids = {
    'DE GDP': 'CLVMDEEA02DEQ',
    'DE GDP v2': 'DEUGDPNQDSMEI',
    'DE GDP v3': 'NAEXKP01DEQ189S',
    'ES GDP': 'CLVMESEA02ESQ',
    'ES GDP v2': 'NAEXKP01ESQ189S',
}

for label, sid in ids.items():
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
    first = r.text[:80]
    ok = 'DATE' in first or 'observation' in first
    print(f"{'✓' if ok else '✗'} {label} ({sid}): {first[:60]}")
