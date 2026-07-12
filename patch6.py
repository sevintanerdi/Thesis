with open('thesis_svar_v2.py', 'r') as f:
    content = f.read()

# Remove short_yield from endog col_map
old1 = """    col_map = {
        'long_yield':  'long_yield',
        'short_yield': 'short_yield',
        'nim':         f'nim_{c}',
        'cet1':        f'cet1_{c}',
        'gdp':         f'gdp_{c}',
        'defl':        f'defl_{c}',
        'credit':      f'credit_{c}',
    }"""

new1 = """    col_map = {
        'long_yield':  'long_yield',
        'nim':         f'nim_{c}',
        'cet1':        f'cet1_{c}',
        'gdp':         f'gdp_{c}',
        'defl':        f'defl_{c}',
        'credit':      f'credit_{c}',
    }"""

# Add short_yield as second exog alongside d_dfr or d_ssr
old2 = """    endog = pd.DataFrame(result).dropna()
    exog  = df[[exog_col]].replace([np.inf, -np.inf], np.nan).reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    return endog, exog"""

new2 = """    endog = pd.DataFrame(result).dropna()
    # short_yield (Euribor) added as exogenous — EA-wide, identical across countries
    # Adding as endog causes collinearity; as exog it captures short-rate transmission
    short_diff = df[['short_yield']].diff().rename(columns={'short_yield': 'd_short_yield'})
    exog_base  = df[[exog_col]].replace([np.inf, -np.inf], np.nan)
    exog = pd.concat([exog_base, short_diff], axis=1).reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    return endog, exog"""

found1 = old1 in content
found2 = old2 in content
print(f"col_map found: {found1}, exog found: {found2}")

if found1:
    content = content.replace(old1, new1)
if found2:
    content = content.replace(old2, new2)

with open('thesis_svar_v2.py', 'w') as f:
    f.write(content)
print("Done")
