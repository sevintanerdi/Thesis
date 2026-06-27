import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

df = pd.read_csv('thesis_data.csv', index_col='date', parse_dates=True)

df_diff = df.copy()
diff_vars = ['policy_rate', 'inflation', 'credit_growth', 'cet1_ea', 'cet1_de', 'cet1_es', 'nim_de']
for var in diff_vars:
    df_diff[var] = df[var].diff()
df_diff['inflation'] = df_diff['inflation'].diff()
df_diff['cet1_es'] = df_diff['cet1_es'].diff()
df_diff = df_diff.dropna()

variables = {
    'ECB Policy Rate': ('policy_rate', 'First difference'),
    'Inflation (HICP)': ('inflation', 'Second difference'),
    'Credit Growth': ('credit_growth', 'First difference'),
    'GDP Growth': ('gdp_growth', 'Levels'),
    'NIM - Euro Area': ('nim_ea', 'Levels'),
    'NIM - Germany': ('nim_de', 'First difference'),
    'NIM - Spain': ('nim_es', 'Levels'),
    'CET1 - Euro Area': ('cet1_ea', 'First difference'),
    'CET1 - Germany': ('cet1_de', 'First difference'),
    'CET1 - Spain': ('cet1_es', 'Second difference'),
}

print(f"{'Variable':<22} {'Transformation':<22} {'ADF Stat':>10} {'p-value':>10} {'Stationary':>15}")
print("-" * 82)

for name, (col, transformation) in variables.items():
    result = adfuller(df_diff[col].dropna())
    if result[1] < 0.05:
        stationary = 'Yes (5%)'
    elif result[1] < 0.10:
        stationary = 'Yes (10%)'
    else:
        stationary = 'No'
    print(f"{name:<22} {transformation:<22} {result[0]:>10.3f} {result[1]:>10.3f} {stationary:>15}")