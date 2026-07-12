import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# Plot styling
import matplotlib
matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

COUNTRY_COLORS = {
    'de': '#1f4e79',   # dark navy
    'es': '#c00000',   # deep red
    'it': '#375623',   # dark green
    'fr': '#7030a0',   # purple
    'nl': '#0070c0',   # bright blue
}
COUNTRY_LINESTYLES = {
    'de': '-',
    'es': '--',
    'it': '-.',
    'fr': ':',
    'nl': '-',
}

COUNTRIES = ['de', 'es', 'it', 'fr', 'nl']
COUNTRY_LABELS = {'de': 'Germany', 'es': 'Spain', 'it': 'Italy',
                  'fr': 'France', 'nl': 'Netherlands'}

LAGS_BASELINE   = 4
LAGS_ROBUSTNESS = 8
HORIZON         = 12
ROB_SAMPLE_END  = '2019Q4'

raw = {}
for c in COUNTRIES:
    raw[c] = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)


def adf_pvalue(series):
    s = series.dropna()
    if len(s) < 15:
        return 1.0
    return adfuller(s)[1]


def prepare_data(df, c, full=True, exog_col='d_dfr'):
    """
    Endogenous: NIM, CET1, long yield, short yield, GDP, deflator, credit.
    Exogenous: change in EA DFR (d_dfr) or change in shadow rate (d_ssr).
    DFR kept out of endogenous to avoid singularity with 7-variable system.
    Stationarity: levels if I(1) at most; first diff only if clearly I(2).
    GDP, deflator, credit enter as 100*log levels.
    """
    end = None if full else ROB_SAMPLE_END
    df  = df[:end].copy() if end else df.copy()
    df  = df.replace([np.inf, -np.inf], np.nan)

    col_map = {
        'long_yield':  'long_yield',
        'nim':         f'nim_{c}',
        'cet1':        f'cet1_{c}',
        'gdp':         f'gdp_{c}',
        'defl':        f'defl_{c}',
        'credit':      f'credit_{c}',
    }

    result = {}
    print(f"\n{COUNTRY_LABELS[c]} — transformation (all first diff):")
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        result[name] = s.diff()
        print(f"  {name}: first diff")

    endog = pd.DataFrame(result).dropna()
    # short_yield (Euribor) added as exogenous — EA-wide, identical across countries
    # Adding as endog causes collinearity; as exog it captures short-rate transmission
    short_diff = df[['short_yield']].diff().rename(columns={'short_yield': 'd_short_yield'})
    exog_base  = df[[exog_col]].replace([np.inf, -np.inf], np.nan)
    exog = pd.concat([exog_base, short_diff], axis=1).reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    return endog, exog


def run_var(endog, exog, lags, label=''):
    model   = sm.tsa.VAR(endog=endog, exog=exog)
    results = model.fit(lags)
    roots   = results.roots
    stable  = all(abs(r) > 1.0 for r in roots)
    print(f"  [{label}] lags={lags}, obs={results.nobs}, AIC={results.aic:.1f}, stable={stable}")
    return results


def get_response(results_dict, varname, horizon=HORIZON):
    """
    Compute dynamic response of varname to a unit shock in the exogenous policy variable.
    res.coefs_exog shape: (k, n_exog_cols) where n_exog_cols = n_exog_vars + 1 (const).
    The policy variable (d_dfr or d_ssr) is the last column.
    Response propagated via MA representation of the VAR.
    """
    res  = results_dict['results']
    cols = list(results_dict['endog'].columns)
    if varname not in cols:
        return None
    try:
        ma        = res.ma_rep(maxn=horizon)   # (horizon+1, k, k)
        idx       = cols.index(varname)
        # coefs_exog: (k, n_exog_total) — last column is d_dfr/d_ssr
        impact    = res.coefs_exog[:, -1]      # impact of policy exog on each variable
        val       = np.array([float(ma[h, idx, :] @ impact) for h in range(horizon + 1)])
        # Clip extreme values from unstable VARs
        if np.any(np.abs(val) > 100):
            val = np.clip(val, -10, 10)
        return val
    except Exception as e:
        print(f"    Response failed ({varname}): {e}")
        return None


results_main     = {}
results_precovid = {}
results_lags8    = {}
results_ssr      = {}

for c in COUNTRIES:
    df = raw[c]
    endog, exog = prepare_data(df, c, full=True, exog_col='d_dfr')

    print(f"Baseline:")
    res = run_var(endog, exog, LAGS_BASELINE, 'baseline')
    results_main[c] = {'results': res, 'endog': endog}

    print(f"Robustness — pre-COVID (2015–2019):")
    endog_r, exog_r = prepare_data(df, c, full=False, exog_col='d_dfr')
    try:
        results_precovid[c] = {'results': run_var(endog_r, exog_r, LAGS_BASELINE, 'pre-COVID'),
                                'endog': endog_r}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_precovid[c] = None

    print(f"Robustness — 8 lags:")
    try:
        results_lags8[c] = {'results': run_var(endog, exog, LAGS_ROBUSTNESS, '8-lag'),
                             'endog': endog}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_lags8[c] = None

    print(f"Robustness — shadow rate:")
    try:
        endog_s, exog_s = prepare_data(df, c, full=True, exog_col='d_ssr')
        results_ssr[c] = {'results': run_var(endog_s, exog_s, LAGS_BASELINE, 'SSR'),
                           'endog': endog_s}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_ssr[c] = None


periods = range(HORIZON + 1)
styles  = {
    'de': (COUNTRY_COLORS['de'], COUNTRY_LINESTYLES['de'], 'Germany'),
    'es': (COUNTRY_COLORS['es'], COUNTRY_LINESTYLES['es'], 'Spain'),
    'it': (COUNTRY_COLORS['it'], COUNTRY_LINESTYLES['it'], 'Italy'),
    'fr': (COUNTRY_COLORS['fr'], COUNTRY_LINESTYLES['fr'], 'France'),
    'nl': (COUNTRY_COLORS['nl'], COUNTRY_LINESTYLES['nl'], 'Netherlands'),
}

# Figure 1: Baseline response — all countries, key variables
target_vars = ['nim', 'cet1', 'long_yield', 'gdp']
fig1, axes1 = plt.subplots(len(COUNTRIES), len(target_vars),
                            figsize=(4*len(target_vars), 4*len(COUNTRIES)))
fig1.suptitle('Response to ∆DFR Shock\n(Baseline: 4 lags, 2015Q1–present)',
              fontsize=13, fontweight='bold')

for i, c in enumerate(COUNTRIES):
    for j, vname in enumerate(target_vars):
        ax  = axes1[i, j]
        val = get_response(results_main[c], vname)
        if val is None:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.plot(periods, val, 'b-', linewidth=2)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4)
        ax.set_title(f'{COUNTRY_LABELS[c]} — {vname.upper()}')
        ax.set_xlabel('Quarters')

plt.tight_layout()
plt.savefig('irf_baseline.png', dpi=300, bbox_inches='tight')
plt.show()
print("irf_baseline.png saved")

# Figure 2: Cross-country NIM and CET1
fig2, (ax_nim, ax_cet1) = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Cross-Country Comparison: Response to ∆DFR Shock', fontsize=13, fontweight='bold')

for c, (color, ls, label) in styles.items():
    val_nim  = get_response(results_main[c], 'nim')
    val_cet1 = get_response(results_main[c], 'cet1')
    if val_nim  is not None: ax_nim.plot(periods, val_nim,   color=color, linestyle=ls, linewidth=2, label=label)
    if val_cet1 is not None: ax_cet1.plot(periods, val_cet1, color=color, linestyle=ls, linewidth=2, label=label)

for ax, title in [(ax_nim, 'NIM Response'), (ax_cet1, 'CET1 Response')]:
    ax.axhline(0, color='k', linestyle=':', alpha=0.5)
    ax.set_title(title); ax.set_xlabel('Quarters'); ax.legend()

plt.tight_layout()
plt.savefig('irf_country_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("irf_country_comparison.png saved")

# Figure 3: Robustness — full vs pre-COVID
fig3, axes3 = plt.subplots(1, len(COUNTRIES), figsize=(4*len(COUNTRIES), 5))
fig3.suptitle('Robustness: Full Sample vs Pre-COVID (2015–2019)\nNIM Response',
              fontsize=12, fontweight='bold')

for ax, c in zip(axes3, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val_f = get_response(results_main[c], 'nim')
    if val_f is not None:
        ax.plot(periods, val_f, color=color, linestyle='-', linewidth=2, label='Full sample')
    if results_precovid[c]:
        val_r = get_response(results_precovid[c], 'nim')
        if val_r is not None:
            ax.plot(periods, val_r, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='Pre-COVID')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('robustness_precovid.png', dpi=300, bbox_inches='tight')
plt.show()
print("robustness_precovid.png saved")

# Figure 4: Robustness — DFR vs shadow rate
fig4, axes4 = plt.subplots(1, len(COUNTRIES), figsize=(4*len(COUNTRIES), 5))
fig4.suptitle('Robustness: ∆DFR vs ∆Shadow Rate as Exogenous Variable\nNIM Response',
              fontsize=12, fontweight='bold')

for ax, c in zip(axes4, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val_d = get_response(results_main[c], 'nim')
    if val_d is not None:
        ax.plot(periods, val_d, color=color, linestyle='-', linewidth=2, label='∆DFR (baseline)')
    if results_ssr[c]:
        val_s = get_response(results_ssr[c], 'nim')
        if val_s is not None:
            ax.plot(periods, val_s, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='∆SSR (robustness)')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('robustness_ssr.png', dpi=300, bbox_inches='tight')
plt.show()
print("robustness_ssr.png saved")

# Figure 5: Robustness — 4 vs 8 lags
fig5, axes5 = plt.subplots(1, len(COUNTRIES), figsize=(4*len(COUNTRIES), 5))
fig5.suptitle('Robustness: 4 Lags vs 8 Lags\nNIM Response',
              fontsize=12, fontweight='bold')

for ax, c in zip(axes5, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val4 = get_response(results_main[c], 'nim')
    if val4 is not None:
        ax.plot(periods, val4, color=color, linestyle='-', linewidth=2, label='4 lags')
    if results_lags8[c]:
        val8 = get_response(results_lags8[c], 'nim')
        if val8 is not None:
            ax.plot(periods, val8, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='8 lags')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('robustness_lags.png', dpi=300, bbox_inches='tight')
plt.show()
print("robustness_lags.png saved")

print("\nAll figures saved.")