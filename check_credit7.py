import requests
from io import StringIO
import pandas as pd

def test_ecb(key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{key}?startPeriod=2015-01&endPeriod=2015-06&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        df = pd.read_csv(StringIO(r.text))
        val_col = [c for c in df.columns if 'OBS_VALUE' in c][0]
        val = pd.to_numeric(df[val_col], errors='coerce').dropna().iloc[0]
        print(f"✓ {label}: {val:.1f}")
    else:
        print(f"✗ {label} ({r.status_code})")

# Try outstanding amounts with different counterpart/sector codes
for c in ['DE','ES','IT','FR','NL']:
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.E.U2.2240.Z01.E", f"{c} v1")
    test_ecb(f"BSI/M.{c}.N.A.A20.A.E.U2.2240.Z01.E",  f"{c} v2")
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.E.A1.2240.Z01.E", f"{c} v3")
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.N.U2.2240.Z01.E", f"{c} v4")
