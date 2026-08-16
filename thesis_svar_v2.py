import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm

# Clean academic plot style
matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
})

COUNTRIES = ['de', 'es', 'it', 'fr', 'nl']
COUNTRY_LABELS = {
    'de': 'Germany', 'es': 'Spain', 'it': 'Italy',
    'fr': 'France',  'nl': 'Netherlands'
}

# Country-specific colors and line styles for cross-country comparisons
COUNTRY_COLORS = {
    'de': '#1f4e79', 'es': '#c00000', 'it': '#375623',
    'fr': '#7030a0', 'nl': '#0070c0'
}
COUNTRY_LS = {
    'de': '-', 'es': '--', 'it': '-.', 'fr': ':', 'nl': '-'
}

LAGS_BASELINE   = 4    # baseline lag length (1 year of quarterly lags)
LAGS_ROBUSTNESS = 8    # robustness check: 2 years of lags
HORIZON         = 8   # IRF horizon in quarters
ROB_SAMPLE_END  = '2019Q4'  # pre-COVID robustness sample end

# Load per-country datasets produced by thesis_data_v2.py
raw = {}
for c in COUNTRIES:
    raw[c] = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)


def prepare_data(df, c, full=True, exog_col='d_dfr'):
    # long_yield, gdp, defl, credit: first-differenced (I(1))
    # nim, cet1: levels (I(1) at most)
    # short_yield: exog to avoid collinearity (EA-wide series)
    end = None if full else ROB_SAMPLE_END
    df  = df[:end].copy() if end else df.copy()
    df  = df.replace([np.inf, -np.inf], np.nan)

    diff_vars = {'long_yield', 'gdp', 'defl', 'credit'}
    col_map = {
        'long_yield': 'long_yield',
        'nim':        f'nim_{c}',
        'cet1':       f'cet1_{c}',
        'gdp':        f'gdp_{c}',
        'defl':       f'defl_{c}',
        'credit':     f'credit_{c}',
    }

    result = {}
    for name, col in col_map.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        result[name] = s.diff() if name in diff_vars else s

    endog = pd.DataFrame(result).dropna()

    # short_yield added as exog to preserve it without causing collinearity
    short_diff = df[['short_yield']].diff().rename(columns={'short_yield': 'd_short_yield'})
    exog_base  = df[[exog_col]].replace([np.inf, -np.inf], np.nan)
    exog = pd.concat([exog_base, short_diff], axis=1).reindex(endog.index).dropna()
    endog = endog.reindex(exog.index).dropna()
    return endog, exog


def run_var(endog, exog, lags, label=''):
    """Fit VAR with exogenous variables and report key diagnostics."""
    model   = sm.tsa.VAR(endog=endog, exog=exog)
    results = model.fit(lags)
    stable  = all(abs(r) > 1.0 for r in results.roots)
    print(f"  [{label}] lags={lags}, obs={results.nobs}, AIC={results.aic:.1f}, stable={stable}")
    return results


def get_response(results_dict, varname, horizon=HORIZON):
    # Response to unit shock in exog policy variable, propagated via MA representation
    res  = results_dict['results']
    cols = list(results_dict['endog'].columns)
    if varname not in cols:
        return None
    try:
        ma     = res.ma_rep(maxn=horizon)       # shape: (horizon+1, k, k)
        idx    = cols.index(varname)
        impact = res.coefs_exog[:, 1]          # policy exog: column order is [const, policy, d_short_yield]
        val    = np.array([float(ma[h, idx, :] @ impact) for h in range(horizon + 1)])
        return val
    except Exception as e:
        print(f"    Response failed ({varname}): {e}")
        return None


# 3-variable EA VAR to extract orthogonalized DFR shock (supervisor notebook variant 3)

def orthogonalized_shocks(var_results):

    u   = var_results.resid
    P   = np.linalg.cholesky(var_results.sigma_u)
    eps = np.linalg.solve(P, u.T).T
    return pd.DataFrame(eps, index=u.index,
                        columns=[f'shock_{c}' for c in u.columns])

df_ea3    = raw['de'].copy().replace([np.inf, -np.inf], np.nan)
ea3_endog = pd.DataFrame({
    'defl': df_ea3['defl_de'].diff(),
    'gdp':  df_ea3['gdp_de'].diff(),
    'dfr':  df_ea3['dfr'],
}).dropna()

try:
    results_ea3 = sm.tsa.VAR(ea3_endog).fit(4)
    shocks_ea3  = orthogonalized_shocks(results_ea3)
    shock_dfr   = shocks_ea3[['shock_dfr']].rename(columns={'shock_dfr': 'orth_shock'})
    print(f"EA 3-var VAR: obs={results_ea3.nobs} — orthogonalized DFR shock extracted")
    HAS_ORTH = True
except Exception as e:
    print(f"EA 3-var VAR FAILED: {e}")
    HAS_ORTH = False
    shock_dfr = None


# ── Main estimation loop ──
results_main     = {}   # baseline: d_dfr exog, 4 lags, full sample
results_precovid = {}   # robustness: pre-COVID sample (2015Q1–2019Q4)
results_lags8    = {}   # robustness: 8 lags
results_ssr      = {}   # robustness: shadow rate (d_ssr) as exog
results_orth     = {}   # robustness: orthogonalized EA shock as exog

for c in COUNTRIES:
    df = raw[c]
    print(f"\n{'='*40}\n{COUNTRY_LABELS[c]}\n{'='*40}")

    endog, exog = prepare_data(df, c, full=True, exog_col='d_dfr')

    print("Baseline (∆DFR, 4 lags, 2015Q1–present):")
    res = run_var(endog, exog, LAGS_BASELINE, 'baseline')
    results_main[c] = {'results': res, 'endog': endog}

    print("Robustness — pre-COVID sample (2015Q1–2019Q4):")
    endog_r, exog_r = prepare_data(df, c, full=False, exog_col='d_dfr')
    try:
        results_precovid[c] = {
            'results': run_var(endog_r, exog_r, LAGS_BASELINE, 'pre-COVID'),
            'endog': endog_r}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_precovid[c] = None

    print("Robustness — 8 lags:")
    try:
        results_lags8[c] = {
            'results': run_var(endog, exog, LAGS_ROBUSTNESS, '8-lag'),
            'endog': endog}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_lags8[c] = None

    print("Robustness — shadow rate (∆SSR, Krippner) as exog:")
    try:
        endog_s, exog_s = prepare_data(df, c, full=True, exog_col='d_ssr')
        results_ssr[c] = {
            'results': run_var(endog_s, exog_s, LAGS_BASELINE, 'SSR'),
            'endog': endog_s}
    except Exception as e:
        print(f"  FAILED: {e}")
        results_ssr[c] = None

    print("Robustness — orthogonalized EA DFR shock as exog:")
    if HAS_ORTH:
        try:
            endog_o, _ = prepare_data(df, c, full=True, exog_col='d_dfr')
            short_d    = df[['short_yield']].diff().rename(columns={'short_yield': 'd_short_yield'})
            exog_o     = pd.concat([shock_dfr, short_d], axis=1).reindex(endog_o.index).dropna()
            endog_o    = endog_o.reindex(exog_o.index).dropna()
            results_orth[c] = {
                'results': run_var(endog_o, exog_o, LAGS_BASELINE, 'orth-shock'),
                'endog': endog_o}
        except Exception as e:
            print(f"  FAILED: {e}")
            results_orth[c] = None
    else:
        results_orth[c] = None


# ── Figures ──
fig0, axes0 = plt.subplots(3, 2, figsize=(14, 14))
fig0.suptitle('Key Variables: All Countries (2015Q1-present)', fontsize=13, fontweight='bold')

ax_dfr = axes0[0, 0]
ax_dfr.plot(raw['de'].index, raw['de']['dfr'], color='black', linewidth=2)
ax_dfr.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax_dfr.set_title('ECB Deposit Facility Rate (%)')
ax_dfr.set_xlabel('Date')

panel_map = [
    (axes0[0, 1], 'nim', 'Net Interest Margin (%)'),
    (axes0[1, 0], 'cet1', 'CET1 Capital Ratio (%)'),
    (axes0[1, 1], 'long_yield', '10Y Government Bond Yield (%)'),
    (axes0[2, 0], 'credit', 'Credit (100 x log level, EUR mn)'),
    (axes0[2, 1], 'gdp', 'Real GDP (100 x log level)'),
]

for ax, varname, title in panel_map:
    for c in COUNTRIES:
        df_c = raw[c]
        col = varname if varname == 'long_yield' else f'{varname}_{c}'
        if col in df_c.columns:
            ax.plot(df_c.index, df_c[col], color=COUNTRY_COLORS[c], linestyle=COUNTRY_LS[c],
                    linewidth=1.8, label=COUNTRY_LABELS[c])
    ax.set_title(title)
    ax.set_xlabel('Date')
    if varname == 'nim':
        ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('timeseries.png', dpi=300, bbox_inches='tight')
plt.show()
print("timeseries.png saved")

periods = range(HORIZON + 1)

# Figure 1: Baseline IRF grid — all countries x key variables
target_vars = ['nim', 'cet1', 'long_yield', 'credit', 'gdp']
fig1, axes1 = plt.subplots(len(COUNTRIES), len(target_vars),
                            figsize=(4*len(target_vars), 4*len(COUNTRIES)))
fig1.suptitle('Response to ∆DFR Shock\n(Baseline: 4 lags, 2015Q1–present)',
              fontsize=13, fontweight='bold')

for i, c in enumerate(COUNTRIES):
    color = COUNTRY_COLORS[c]
    ls    = COUNTRY_LS[c]
    for j, vname in enumerate(target_vars):
        ax  = axes1[i, j]
        val = get_response(results_main[c], vname)
        if val is None:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.plot(periods, val, color=color, linestyle=ls, linewidth=2.5)
            ax.axhline(0, color='k', linestyle='--', alpha=0.4, linewidth=0.8)
        ax.set_title(f'{COUNTRY_LABELS[c]} — {vname.upper()}',
                     fontsize=10, color=color, fontweight='bold')
        ax.set_xlabel('Quarters')

plt.tight_layout()
plt.savefig('irf_baseline.png', dpi=300, bbox_inches='tight')
plt.show()
print("irf_baseline.png saved")

# Figure 2: Cross-country NIM and CET1 comparison
fig2, (ax_nim, ax_cet1, ax_credit) = plt.subplots(1, 3, figsize=(22, 6))
fig2.suptitle('Cross-Country Comparison: Response to ∆DFR Shock', fontsize=13, fontweight='bold')

for c in COUNTRIES:
    color = COUNTRY_COLORS[c]
    ls    = COUNTRY_LS[c]
    label = COUNTRY_LABELS[c]
    val_nim    = get_response(results_main[c], 'nim')
    val_cet1   = get_response(results_main[c], 'cet1')
    val_credit = get_response(results_main[c], 'credit')
    if val_nim    is not None: ax_nim.plot(periods,    val_nim,    color=color, linestyle=ls, linewidth=2, label=label)
    if val_cet1   is not None: ax_cet1.plot(periods,   val_cet1,   color=color, linestyle=ls, linewidth=2, label=label)
    if val_credit is not None: ax_credit.plot(periods, val_credit, color=color, linestyle=ls, linewidth=2, label=label)

for ax, title in [(ax_nim, 'NIM Response'), (ax_cet1, 'CET1 Response'), (ax_credit, 'Credit Growth Response')]:
    ax.axhline(0, color='k', linestyle=':', alpha=0.5)
    ax.set_title(title); ax.set_xlabel('Quarters'); ax.legend()

plt.tight_layout()
plt.savefig('irf_country_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("irf_country_comparison.png saved")

# Figure 3: Robustness — full sample vs pre-COVID
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

# Figure 4: Robustness — baseline DFR vs shadow rate
fig4, axes4 = plt.subplots(1, len(COUNTRIES), figsize=(4*len(COUNTRIES), 5))
fig4.suptitle('Robustness: ∆DFR vs ∆Shadow Rate (Krippner SSR) as Exogenous Variable\nNIM Response',
              fontsize=12, fontweight='bold')

for ax, c in zip(axes4, COUNTRIES):
    color = COUNTRY_COLORS[c]
    val_d = get_response(results_main[c], 'nim')
    if val_d is not None:
        ax.plot(periods, val_d, color=color, linestyle='-', linewidth=2, label='∆DFR (baseline)')
    if results_ssr[c]:
        val_s = get_response(results_ssr[c], 'nim')
        if val_s is not None:
            ax.plot(periods, val_s, color=color, linestyle='--', linewidth=1.5, alpha=0.7, label='∆SSR')
    ax.axhline(0, color='k', linestyle=':', alpha=0.4)
    ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('robustness_ssr.png', dpi=300, bbox_inches='tight')
plt.show()
print("robustness_ssr.png saved")

# Figure 5: Robustness — 4 lags vs 8 lags
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

# Figure 6: Robustness — baseline DFR vs orthogonalized EA shock
if HAS_ORTH:
    fig6, axes6 = plt.subplots(1, len(COUNTRIES), figsize=(4*len(COUNTRIES), 5))
    fig6.suptitle('Robustness: ∆DFR vs Orthogonalized EA DFR Shock\nNIM Response',
                  fontsize=12, fontweight='bold')

    for ax, c in zip(axes6, COUNTRIES):
        color = COUNTRY_COLORS[c]
        val_d = get_response(results_main[c], 'nim')
        if val_d is not None:
            ax.plot(periods, val_d, color=color, linestyle='-', linewidth=2, label='∆DFR (baseline)')
        if results_orth[c]:
            val_o = get_response(results_orth[c], 'nim')
            if val_o is not None:
                ax.plot(periods, val_o, color=color, linestyle='--', linewidth=1.5,
                        alpha=0.7, label='Orth. shock')
        ax.axhline(0, color='k', linestyle=':', alpha=0.4)
        ax.set_title(COUNTRY_LABELS[c]); ax.set_xlabel('Quarters'); ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig('robustness_orth_shock.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("robustness_orth_shock.png saved")

print("\nAll figures saved.")