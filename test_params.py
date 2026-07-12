import pandas as pd
import numpy as np
import statsmodels.api as sm

df = pd.read_csv('thesis_data_de.csv', index_col='date', parse_dates=True)
df = df.replace([np.inf, -np.inf], np.nan)

endog = df[['nim_de','cet1_de','long_yield','short_yield','gdp_de','defl_de','credit_de']].dropna()
exog  = df[['d_dfr']].reindex(endog.index).dropna()
endog = endog.reindex(exog.index).dropna()

res = sm.tsa.VAR(endog=endog, exog=exog).fit(4)

print("params shape:", res.params.shape)
print("params index:", res.params.index.tolist()[-5:])
print()

# Try different attributes
for attr in ['params_ex', 'coefs_exog', 'exog_params']:
    try:
        val = getattr(res, attr)
        print(f"{attr}: shape={val.shape}, val={val}")
    except Exception as e:
        print(f"{attr}: FAILED — {e}")
