import requests

ids = {
    'DE GDP': 'DEUGDPNQDSMEI',
    'DE GDP v3': 'NAEXKP01DEQ189S',
    'ES GDP': 'NAEXKP01ESQ189S',
    'IT GDP': 'NAEXKP01ITQ189S',
    'FR GDP': 'NAEXKP01FRQ189S',
    'NL GDP': 'NAEXKP01NLQ189S',
    'DE deflator': 'DEUGDPDEFQISMEI',
    'ES deflator': 'ESPGDPDEFQISMEI',
    'IT deflator': 'ITALGDPDEFQISMEI',
    'FR deflator': 'FRAGDPDEFQISMEI',
    'NL deflator': 'NLDGDPDEFQISMEI',
    'EA 3M Euribor': 'IR3TIB01EZM156N',
    'DE 1Y yield': 'IRLTST01DEM156N',
    'ES 1Y yield': 'IRLTST01ESM156N',
}

for label, sid in ids.items():
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
    first = r.text[:80]
    ok = 'DATE' in first or 'observation' in first
    print(f"{'✓' if ok else '✗'} {label} ({sid})")
