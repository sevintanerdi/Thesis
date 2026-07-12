import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv('thesis_data_de.csv', index_col='date', parse_dates=True)
df = df.replace([np.inf, -np.inf], np.nan)

endog = df[['long_yield','nim_de','cet1_de','gdp_de','defl_de','credit_de']].dropna()
short_diff = df[['short_yield']].diff().rename(columns={'short_yield': 'd_short_yield'})
exog_base  = df[['d_dfr']]
exog = pd.concat([exog_base, short_diff], axis=1).reindex(endog.index).dropna()
endog = endog.reindex(exog.index).dropna()

res = sm.tsa.VAR(endog=endog, exog=exog).fit(4)

# Try bootstrap errband
try:
    irf = res.irf(12)
    lower, upper = irf.errband_mc(orth=False, repl=200, signif=0.32)
    print(f"Bootstrap CI OK: lower shape={lower.shape}")
except Exception as e:
    print(f"Bootstrap failed: {e}")
