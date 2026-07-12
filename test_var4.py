import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv('thesis_data_de.csv', index_col='date', parse_dates=True)
df = df.replace([np.inf, -np.inf], np.nan)

cols = ['dfr', 'nim_de', 'cet1_de', 'long_yield', 'short_yield', 'gdp_de', 'defl_de', 'credit_de']

for drop in cols[1:]:
    test_cols = [c for c in cols if c != drop]
    endog = df[test_cols].dropna()
    exog  = df[['d_dfr']].reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    try:
        res = sm.tsa.VAR(endog=endog, exog=exog).fit(4)
        print(f"OK (dropped {drop}): obs={len(endog)}, AIC={res.aic:.1f}")
    except Exception as e:
        print(f"FAIL (dropped {drop}): {str(e)[:50]}")
