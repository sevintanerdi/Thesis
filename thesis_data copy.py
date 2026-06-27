import pandas as pd
import requests
from io import StringIO

def get_ecb_monthly(series_key, start='2003-01', end='2024-12'):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod={start}&endPeriod={end}&format=csvdata"
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    time_col = [c for c in df.columns if 'TIME' in c][0]
    val_col = [c for c in df.columns if 'OBS_VALUE' in c][0]
    df = df[[time_col, val_col]].copy()
    df.columns = ['date', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df_q = df.resample('QE').mean()
    return df_q

def get_ecb_quarterly(series_key, start='2003-Q1', end='2024-Q4'):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod={start}&endPeriod={end}&format=csvdata"
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))
    time_col = [c for c in df.columns if 'TIME' in c][0]
    val_col = [c for c in df.columns if 'OBS_VALUE' in c][0]
    df = df[[time_col, val_col]].copy()
    df.columns = ['date', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['date'] = df['date'].apply(lambda x: pd.to_datetime(f"{x[:4]}-{int(x[6])*3-2:02d}-01") if isinstance(x, str) and 'Q' in x else pd.NaT)
    df = df.set_index('date')
    return df

# Policy rate
policy_rate = get_ecb_monthly("FM/B.U2.EUR.4F.KR.DFR.LEV")
policy_rate.columns = ['policy_rate']

# Inflation
inflation = get_ecb_monthly("ICP/M.U2.N.000000.4.ANR")
inflation.columns = ['inflation']

# GDP
gdp = get_ecb_quarterly("MNA/Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY")
gdp.columns = ['gdp_growth']

# Credit growth - loans to NFCs year on year
credit = get_ecb_monthly("BSI/M.U2.N.A.A20T.A.I.U2.2240.Z01.A")
credit.columns = ['credit_growth']

# Hepsini birleştir
df = pd.concat([policy_rate, inflation, credit], axis=1)
df.index = pd.PeriodIndex(df.index, freq='Q')
gdp.index = pd.PeriodIndex(gdp.index, freq='Q')
df = df.join(gdp, how='left')

# 2003-2024 filtrele
df = df['2003Q1':'2024Q4']

print(df.shape)
print(df.tail(10))
print("\nEksik değerler:")
print(df.isnull().sum())

# CSV'ye kaydet
df.to_csv('thesis_data.csv')
print("\nData kaydedildi: thesis_data.csv")