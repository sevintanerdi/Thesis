import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv('thesis_data_fr.csv', index_col='date', parse_dates=True)
df = df.replace([np.inf, -np.inf], np.nan)

# France variables in levels (all)
cols_all = ['nim_fr', 'cet1_fr', 'long_yield', 'short_yield', 'gdp_fr', 'defl_fr', 'credit_fr']

for drop in cols_all:
    test_cols = [c for c in cols_all if c != drop]
    endog = df[test_cols].dropna()
    exog  = df[['d_dfr']].reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    try:
        res = sm.tsa.VAR(endog=endog, exog=exog).fit(4)
        print(f"OK (dropped {drop}): obs={len(endog)}")
    except Exception as e:
        print(f"FAIL (dropped {drop}): {str(e)[:40]}")
