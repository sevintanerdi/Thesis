import requests

ids = {
    'ES GDP v2': 'ESPGDPNQDSMEI',
    'ES GDP v3': 'CLVMESEA02ESQ',
    'ES GDP v4': 'NAEXKP01ESQ656S',
    'IT deflator v2': 'ITALGDPDEFQISMEI',
    'IT deflator v3': 'ITADPANUQ086NRUG',
    'IT deflator v4': 'NAGGDP01ITQ661S',
    'DE 1Y v2': 'IRLTST01DEQ156N',
    'ES 1Y v2': 'IRLTST01ESQ156N',
    'IT 1Y': 'IRLTST01ITQ156N',
    'FR 1Y': 'IRLTST01FRQ156N',
    'NL 1Y': 'IRLTST01NLQ156N',
}

for label, sid in ids.items():
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
    ok = 'DATE' in r.text[:80] or 'observation' in r.text[:80]
    print(f"{'✓' if ok else '✗'} {label} ({sid})")
