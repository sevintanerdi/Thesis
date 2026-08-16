import pandas as pd
import numpy as np
import statsmodels.api as sm

countries = ['de', 'es', 'it', 'fr', 'nl']
names = {'de':'Germany','es':'Spain','it':'Italy','fr':'France','nl':'Netherlands'}

diff_vars = {'long_yield', 'gdp', 'defl', 'credit'}

for c in countries:
    df = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    col_map = {'long_yield':'long_yield','nim':f'nim_{c}','cet1':f'cet1_{c}',
               'gdp':f'gdp_{c}','defl':f'defl_{c}','credit':f'credit_{c}'}
    result = {}
    for name, col in col_map.items():
        s = df[col].dropna()
        result[name] = s.diff() if name in diff_vars else s
    endog = pd.DataFrame(result).dropna()
    short_diff = df[['short_yield']].diff().rename(columns={'short_yield':'d_short_yield'})
    exog = pd.concat([df[['d_dfr']], short_diff], axis=1).reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    res = sm.tsa.VAR(endog=endog, exog=exog).fit(4)
    print(f"{names[c]}: {res.nobs} observations used in estimation")
