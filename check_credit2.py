import requests
import pandas as pd
from io import StringIO

def get_ecb_raw(key):
    url = f"https://data-api.ecb.europa.eu/service/data/{key}?startPeriod=2015-01&endPeriod=2025-12&format=csvdata"
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text))
    val_col = [c for c in df.columns if 'OBS_VALUE' in c][0]
    time_col = [c for c in df.columns if 'TIME' in c][0]
    df = df[[time_col, val_col]].copy()
    df.columns = ['date', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

for c in ['ES', 'IT', 'NL']:
    df = get_ecb_raw(f"BSI/M.{c}.N.A.A20T.A.I.U2.2240.Z01.A")
    print(f"\n{c}: {len(df)} obs, NaN: {df['value'].isna().sum()}")
    print(df.head(3).to_string())
    print(df[df['value'].isna()].head(3).to_string())
