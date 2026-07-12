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

# Outstanding amounts (levels, not growth rates) - E = EUR millions
for c in ['DE','ES','IT','FR','NL']:
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.E.U2.2240.Z01.A", f"{c} credit E (amounts)")
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.E.U6.2240.Z01.A", f"{c} credit E U6")
