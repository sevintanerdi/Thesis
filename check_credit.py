import requests

def test_ecb(key, label):
    url = f"https://data-api.ecb.europa.eu/service/data/{key}?startPeriod=2015-01&endPeriod=2015-06&format=csvdata"
    r = requests.get(url)
    if r.status_code == 200 and 'OBS_VALUE' in r.text:
        from io import StringIO
        import pandas as pd
        df = pd.read_csv(StringIO(r.text))
        val_col = [c for c in df.columns if 'OBS_VALUE' in c][0]
        print(f"✓ {label} — sample val: {df[val_col].dropna().iloc[0]:.1f}")
    else:
        print(f"✗ {label} ({r.status_code})")

# Loans to private sector - different area codes
for c in ['DE','ES','IT','FR','NL']:
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.I.U2.2240.Z01.A", f"{c} credit U2")
    test_ecb(f"BSI/M.{c}.N.A.A20T.A.I.U6.2240.Z01.A", f"{c} credit U6")
    test_ecb(f"BSI/M.{c}.N.A.F.A.I.MFI.2240.Z01.E",   f"{c} credit v3")
