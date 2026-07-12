import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv('thesis_data_de.csv', index_col='date', parse_dates=True)
df = df.replace([np.inf, -np.inf], np.nan)

endog = df[['dfr', 'nim_de', 'cet1_de', 'long_yield', 'short_yield',
            'gdp_de', 'defl_de', 'credit_de']].dropna()
exog  = df[['d_dfr']].reindex(endog.index).dropna()
endog = endog.reindex(exog.index).dropna()

print(f"obs: {len(endog)}, vars: {endog.shape[1]}")
print(f"params per equation: {4 * endog.shape[1]}")

try:
    model = sm.tsa.VAR(endog=endog, exog=exog)
    res   = model.fit(4)
    print(f"AIC: {res.aic:.1f}")
    irf = res.irf(16)
    val = irf.orth_irfs[:, 1, 0]
    print(f"NIM IRF q1: {val[1]:.4f}")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
