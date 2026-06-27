import pandas as pd
from statsmodels.tsa.stattools import adfuller

df = pd.read_csv('thesis_data.csv', index_col='date', parse_dates=True)

long_vars = ['policy_rate', 'inflation', 'gdp_growth', 'credit_growth', 'shadow_rate']
print('=== ADF on LEVELS ===')
for col in long_vars:
    s = df[col].dropna()
    r = adfuller(s)
    print(f'{col}: p={r[1]:.3f} ({"stationary" if r[1]<0.05 else "non-stationary"})')

print()
print('=== ADF on FIRST DIFFERENCE ===')
for col in long_vars:
    s = df[col].diff().dropna()
    r = adfuller(s)
    print(f'd({col}): p={r[1]:.3f} ({"stationary" if r[1]<0.05 else "non-stationary"})')
