import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

countries = ['de', 'es', 'it', 'fr', 'nl']
country_names = {'de': 'Germany', 'es': 'Spain', 'it': 'Italy', 'fr': 'France', 'nl': 'Netherlands'}

var_map = {
    'long_yield': 'long_yield',
    'nim': None,      # will be nim_{c}
    'cet1': None,      # will be cet1_{c}
    'gdp': None,       # will be gdp_{c}
    'defl': None,      # will be defl_{c}
    'credit': None,    # will be credit_{c}
}

diff_vars = {'long_yield', 'gdp', 'defl', 'credit'}  # first-differenced in final spec
level_vars = {'nim', 'cet1'}                          # kept in levels

def adf_row(series):
    s = series.dropna()
    if len(s) < 8:
        return None, None
    stat, pval = adfuller(s)[0], adfuller(s)[1]
    return stat, pval

results = []

for c in countries:
    df = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)
    df = df.replace([np.inf, -np.inf], np.nan)

    col_map = {
        'long_yield': 'long_yield',
        'nim':        f'nim_{c}',
        'cet1':       f'cet1_{c}',
        'gdp':        f'gdp_{c}',
        'defl':       f'defl_{c}',
        'credit':     f'credit_{c}',
    }

    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()

        stat_lev, p_lev = adf_row(s)
        stat_diff, p_diff = adf_row(s.diff())

        transformation = 'First difference' if name in diff_vars else 'Levels'
        used_stat = stat_diff if name in diff_vars else stat_lev
        used_p = p_diff if name in diff_vars else p_lev
        stationary = 'Yes (5%)' if used_p is not None and used_p < 0.05 else ('Yes (10%)' if used_p is not None and used_p < 0.10 else 'No')

        results.append({
            'Country': country_names[c],
            'Variable': name.upper(),
            'Transformation': transformation,
            'ADF Stat': round(used_stat, 3) if used_stat is not None else None,
            'p-value': round(used_p, 3) if used_p is not None else None,
            'Stationary': stationary
        })

result_df = pd.DataFrame(results)
print(result_df.to_string(index=False))
result_df.to_csv('adf_results_table.csv', index=False)
print("\nSaved to adf_results_table.csv")
