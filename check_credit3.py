import requests
import pandas as pd
import numpy as np
from io import StringIO

url = "https://data-api.ecb.europa.eu/service/data/BSI/M.ES.N.A.A20T.A.I.U2.2240.Z01.A?startPeriod=2015-01&endPeriod=2025-12&format=csvdata"
r = requests.get(url)
df = pd.read_csv(StringIO(r.text))
time_col = [c for c in df.columns if 'TIME' in c][0]
val_col  = [c for c in df.columns if 'OBS_VALUE' in c][0]
df = df[[time_col, val_col]].copy()
df.columns = ['date', 'value']
df['value'] = pd.to_numeric(df['value'], errors='coerce')

print("Raw date sample:", df['date'].head(3).tolist())
print("Raw value sample:", df['value'].head(3).tolist())

df['date'] = pd.to_datetime(df['date'].astype(str).str[:7], format='%Y-%m')
df = df.set_index('date').sort_index()
print("\nAfter parse index sample:", df.index[:3].tolist())

q = df.resample('QS').mean()
print("\nAfter resample index sample:", q.index[:3].tolist())
print("NaN after resample:", q['value'].isna().sum())

q['value'] = 100 * np.log(q['value'])
print("NaN after log:", q['value'].isna().sum())
print(q.head(5))
