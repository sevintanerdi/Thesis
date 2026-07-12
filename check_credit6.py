import requests
import pandas as pd
from io import StringIO

for c, sid in [('DE','DDDI01DEA156NWDB'),('ES','DDDI01ESA156NWDB')]:
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
    df = pd.read_csv(StringIO(r.text))
    df.columns = ['date','value']
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= '2014-01-01']
    print(f"\n{c}: {len(df)} obs")
    print(df.head(5).to_string())
