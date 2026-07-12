import pandas as pd
import numpy as np
import requests
from io import StringIO
from openpyxl import load_workbook


def get_ecb(series_key, start, end, freq='M'):
    url = f"https://data-api.ecb.europa.eu/service/data/{series_key}?startPeriod={start}&endPeriod={end}&format=csvdata"
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text))
    time_col = [c for c in df.columns if 'TIME' in c][0]
    val_col  = [c for c in df.columns if 'OBS_VALUE' in c][0]
    df = df[[time_col, val_col]].copy()
    df.columns = ['date', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    if freq == 'M':
        # Parse YYYY-MM format explicitly
        df['date'] = pd.to_datetime(df['date'].astype(str).str[:7], format='%Y-%m')
        df = df.set_index('date').sort_index()
        df = df.resample('QS').mean()
    else:
        df['date'] = df['date'].apply(
            lambda x: pd.to_datetime(f"{x[:4]}-{int(x[6])*3-2:02d}-01")
            if isinstance(x, str) and 'Q' in x else pd.NaT)
        df = df.set_index('date').sort_index()
    return df


def get_fred(series_id, col_name, start='2014-01-01'):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text))
    df.columns = ['date', 'value']
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.set_index('date').sort_index()
    df = df[start:]
    df = df.resample('QS').mean()
    df.columns = [col_name]
    return df


# ECB Deposit Facility Rate — baseline exogenous variable
dfr = get_ecb("FM/B.U2.EUR.4F.KR.DFR.LEV", "2014-01", "2025-12", "M")
dfr.columns = ['dfr']
dfr.loc['2015-01-01', 'dfr'] = -0.20
dfr['dfr'] = dfr['dfr'].ffill().bfill()
dfr['d_dfr'] = dfr['dfr'].diff()

# Short yield: 3M Euribor, EA-wide
euribor = get_fred("IR3TIB01EZM156N", "short_yield")

# Long yields: 10Y government bonds, country-specific (FRED)
yield_de = get_fred("IRLTLT01DEM156N", "long_yield_de")
yield_es = get_fred("IRLTLT01ESM156N", "long_yield_es")
yield_it = get_fred("IRLTLT01ITM156N", "long_yield_it")
yield_fr = get_fred("IRLTLT01FRM156N", "long_yield_fr")
yield_nl = get_fred("IRLTLT01NLM156N", "long_yield_nl")

# 1Y EA spot rate (ECB yield curve) — used as additional short-term yield measure
ycm_1y = get_ecb("YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y", "2014-01", "2025-12", "M")
ycm_1y.columns = ['yield_1y']

# NIM and CET1 — ECB supervisory, country-specific
nim = {}
cet1 = {}
for c, code in [('de','DE'),('es','ES'),('it','IT'),('fr','FR'),('nl','NL')]:
    s = get_ecb(f"SUP/Q.{code}.W0._Z.I2120._T.SII._Z._Z._Z.PCT.C", "2014-Q4", "2025-Q4", "Q")
    s.columns = [f'nim_{c}']
    nim[c] = s
    s = get_ecb(f"SUP/Q.{code}.W0._Z.I4008._T.SII._Z._Z._Z.PCT.C", "2014-Q4", "2025-Q4", "Q")
    s.columns = [f'cet1_{c}']
    cet1[c] = s

# Real GDP — 100*log transformation; country-specific FRED series
# IT uses NAEXKP01ITQ189S (chain-linked volumes index, SA)
gdp_series = {
    'de': 'DEUGDPNQDSMEI',
    'es': 'ESPGDPNQDSMEI',
    'it': 'NAEXKP01ITQ189S',
    'fr': 'NAEXKP01FRQ189S',
    'nl': 'NAEXKP01NLQ189S',
}
gdp = {}
for c, sid in gdp_series.items():
    s = get_fred(sid, f'gdp_{c}')
    s[f'gdp_{c}'] = 100 * np.log(s[f'gdp_{c}'])
    gdp[c] = s
    print(f"GDP {c.upper()}: OK")

# GDP deflator — 100*log; IT uses HICP as price level proxy (deflator unavailable on FRED)
defl_series = {
    'de': ('fred', 'DEUGDPDEFQISMEI'),
    'es': ('fred', 'ESPGDPDEFQISMEI'),
    'it': ('ecb',  'ICP/M.IT.N.000000.4.ANR'),
    'fr': ('fred', 'FRAGDPDEFQISMEI'),
    'nl': ('fred', 'NLDGDPDEFQISMEI'),
}
defl = {}
for c, (source, sid) in defl_series.items():
    if source == 'fred':
        s = get_fred(sid, f'defl_{c}')
        s[f'defl_{c}'] = 100 * np.log(s[f'defl_{c}'].replace(0, np.nan))
    else:
        s = get_ecb(sid, "2014-01", "2025-12", "M")
        s.columns = [f'defl_{c}']
        s[f'defl_{c}'] = 100 * np.log(s[f'defl_{c}'].replace(0, np.nan))
    defl[c] = s
    print(f"Deflator {c.upper()}: OK")

# Credit — total private sector loans outstanding (NFC + households), 100*log levels
# Sources: ECB BSI, adjusted outstanding amounts, EUR millions
credit = {}
for c in ['de','es','it','fr','nl']:
    C = c.upper()
    try:
        nfc = get_ecb(f"BSI/M.{C}.N.A.A20T.A.1.U2.2240.Z01.E", "2014-01", "2025-12", "M")
        hh  = get_ecb(f"BSI/M.{C}.N.A.A20T.A.1.U2.2250.Z01.E", "2014-01", "2025-12", "M")
        total = nfc.add(hh.values, fill_value=0)
        total.columns = [f'credit_{c}']
        total[f'credit_{c}'] = 100 * np.log(total[f'credit_{c}'].replace(0, np.nan))
        credit[c] = total
        print(f"Credit {C}: OK")
    except Exception as e:
        print(f"Credit {C}: FAILED — {e}")
        credit[c] = None

# Shadow Short Rate (Krippner) — robustness exogenous variable
wb = load_workbook('SSR_Estimates_20260602.xlsx', read_only=True, data_only=True)
ws = wb['D. Monthly average SSR series']
rows = list(ws.iter_rows(values_only=True))
ssr_data = [(row[1], row[3]) for row in rows[20:] if row[1] is not None and row[3] is not None]
df_ssr = pd.DataFrame(ssr_data, columns=['date', 'shadow_rate'])
df_ssr['date'] = pd.to_datetime(df_ssr['date'])
df_ssr = df_ssr.set_index('date').sort_index()
ssr_q = df_ssr['shadow_rate'].resample('QS').mean().to_frame()
ssr_q['d_ssr'] = ssr_q['shadow_rate'].diff()

# Build and save per-country datasets
long_yield_map = {
    'de': yield_de, 'es': yield_es, 'it': yield_it,
    'fr': yield_fr, 'nl': yield_nl,
}
countries = ['de', 'es', 'it', 'fr', 'nl']

for c in countries:
    parts = [
        dfr[['dfr', 'd_dfr']],
        euribor,
        ycm_1y,
        long_yield_map[c].rename(columns={f'long_yield_{c}': 'long_yield'}),
        nim[c],
        cet1[c],
        gdp.get(c),
        defl.get(c),
        credit.get(c),
        ssr_q,
    ]
    parts = [p for p in parts if p is not None]
    df_c = pd.concat(parts, axis=1, sort=True)
    df_c = df_c.sort_index()
    df_c = df_c['2015-01-01':]
    # Forward-fill small gaps in GDP and deflator (e.g. latest quarters not yet released)
    for col in [f'gdp_{c}', f'defl_{c}']:
        if col in df_c.columns:
            df_c[col] = df_c[col].ffill()
    df_c.to_csv(f'thesis_data_{c}.csv')
    print(f"thesis_data_{c}.csv saved — shape: {df_c.shape}, NaN: {df_c.isnull().sum().sum()}")

print("\nDone.")