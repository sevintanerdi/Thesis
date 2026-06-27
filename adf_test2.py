import pandas as pd
from statsmodels.tsa.stattools import adfuller

df = pd.read_csv('thesis_data.csv', index_col='date', parse_dates=True)

sup_vars = ['nim_ea', 'nim_de', 'nim_es', 'cet1_ea', 'cet1_de', 'cet1_es']
print('=== ADF on LEVELS (2015+) ===')
for col in sup_vars:
    s = df[col].dropna()
    r = adfuller(s)
    print(f'{col}: p={r[1]:.3f} ({"stationary" if r[1]<0.05 else "non-stationary"})')

print()
print('=== ADF on FIRST DIFFERENCE ===')
for col in sup_vars:
    s = df[col].diff().dropna()
    r = adfuller(s)
    print(f'd({col}): p={r[1]:.3f} ({"stationary" if r[1]<0.05 else "non-stationary"})')

print()
print('=== ADF with trend (levels) - policy_rate & inflation ===')
for col in ['policy_rate', 'inflation']:
    s = df[col].dropna()
    r = adfuller(s, regression='ct')
    print(f'{col} (trend): p={r[1]:.3f} ({"stationary" if r[1]<0.05 else "non-stationary"})')
    r2 = adfuller(s.diff().dropna(), regression='ct')
    print(f'd({col}) (trend): p={r2[1]:.3f} ({"stationary" if r2[1]<0.05 else "non-stationary"})')
