import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller

# Data yükle
df = pd.read_csv('thesis_data.csv', index_col='date', parse_dates=True)

# ── GRAFIK 1: Zaman Serisi ──
fig1, axes1 = plt.subplots(3, 2, figsize=(14, 12))
fig1.suptitle('Key Variables: Euro Area, Germany and Spain', fontsize=14, fontweight='bold')

axes1[0, 0].plot(df.index, df['policy_rate'], 'k-', linewidth=2)
axes1[0, 0].set_title('ECB Policy Rate (%)')
axes1[0, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
axes1[0, 0].set_xlabel('Date')

axes1[0, 1].plot(df.index, df['nim_ea'], 'k-',  linewidth=2, label='Euro Area')
axes1[0, 1].plot(df.index, df['nim_de'], 'b--', linewidth=2, label='Germany')
axes1[0, 1].plot(df.index, df['nim_es'], 'r-.', linewidth=2, label='Spain')
axes1[0, 1].set_title('Net Interest Margin (%)')
axes1[0, 1].legend()
axes1[0, 1].set_xlabel('Date')

axes1[1, 0].plot(df.index, df['cet1_ea'], 'k-',  linewidth=2, label='Euro Area')
axes1[1, 0].plot(df.index, df['cet1_de'], 'b--', linewidth=2, label='Germany')
axes1[1, 0].plot(df.index, df['cet1_es'], 'r-.', linewidth=2, label='Spain')
axes1[1, 0].set_title('CET1 Capital Ratio (%)')
axes1[1, 0].legend()
axes1[1, 0].set_xlabel('Date')

axes1[1, 1].plot(df.index, df['credit_growth'], 'k-', linewidth=2)
axes1[1, 1].set_title('Credit Growth (%)')
axes1[1, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
axes1[1, 1].set_xlabel('Date')

axes1[2, 0].plot(df.index, df['gdp_growth'], 'k-', linewidth=2)
axes1[2, 0].set_title('GDP Growth (%)')
axes1[2, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
axes1[2, 0].set_xlabel('Date')

axes1[2, 1].plot(df.index, df['inflation'], 'k-', linewidth=2)
axes1[2, 1].set_title('Inflation - HICP (%)')
axes1[2, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
axes1[2, 1].set_xlabel('Date')

plt.tight_layout()
plt.savefig('timeseries.png', dpi=300, bbox_inches='tight')
plt.show()
print("Zaman serisi grafiği kaydedildi!")

# ── GRAFIK 1b: Bond Yields ──
fig1b, ax1b = plt.subplots(figsize=(12, 5))
fig1b.suptitle('10-Year Government Bond Yields by Country', fontsize=14, fontweight='bold')
colors = {'yield_de': ('b-',  'Germany'),
          'yield_es': ('r--', 'Spain'),
          'yield_it': ('g-.', 'Italy'),
          'yield_fr': ('m:',  'France'),
          'yield_nl': ('c-',  'Netherlands')}
for col, (style, label) in colors.items():
    ax1b.plot(df.index, df[col], style, linewidth=2, label=label)
ax1b.axhline(y=0, color='k', linestyle=':', alpha=0.3)
ax1b.set_xlabel('Date')
ax1b.set_ylabel('Yield (%)')
ax1b.legend()
plt.tight_layout()
plt.savefig('bond_yields.png', dpi=300, bbox_inches='tight')
plt.show()
print("Bond yields grafiği kaydedildi!")

# ── Stationarity Transformations ──
# ADF sonuçlarına göre (consistent across all countries):
#
# LEVELS: policy_rate (trend-stationary), gdp_growth, nim_* (all countries)
# FIRST DIFFERENCE: inflation, credit_growth, cet1_*, shadow_rate, yield_*
#
# yield_* bond yields: levels likely non-stationary (persistent), first diff alınıyor

df_model = df.copy()

diff_vars = ['inflation', 'credit_growth',
             'cet1_ea', 'cet1_de', 'cet1_es', 'cet1_it', 'cet1_fr', 'cet1_nl',
             'shadow_rate',
             'yield_de', 'yield_es', 'yield_it', 'yield_fr', 'yield_nl']
for var in diff_vars:
    df_model[var] = df[var].diff()

df_model = df_model.dropna()

# ── Stationarity Check ──
print("=== ADF Test Results (post-transformation) ===")
check_vars = ['policy_rate', 'inflation', 'gdp_growth', 'credit_growth',
              'nim_ea', 'nim_de', 'nim_es', 'nim_it', 'nim_fr', 'nim_nl',
              'cet1_ea', 'cet1_de', 'cet1_es', 'cet1_it', 'cet1_fr', 'cet1_nl',
              'yield_de', 'yield_es', 'yield_it', 'yield_fr', 'yield_nl', 'shadow_rate']
for col in check_vars:
    result = adfuller(df_model[col].dropna())
    star = '✓' if result[1] < 0.05 else ('~ (10%)' if result[1] < 0.10 else '✗')
    print(f"{col}: ADF={result[0]:.3f}, p={result[1]:.3f} {star}")

# ── VAR function ──
def run_var(df_vars, label):
    model = VAR(df_vars)
    results = model.fit(maxlags=2, ic='aic')
    print(f"{label} - Optimal lag: {results.k_ar}")
    irf    = results.irf(20)
    stderr = results.irf(20).stderr(orth=False)
    return results, irf, stderr

# ── BASELINE VARs: 6 ülke ──
countries_all = ['ea', 'de', 'es', 'it', 'fr', 'nl']
country_labels = {'ea': 'Euro Area', 'de': 'Germany', 'es': 'Spain',
                  'it': 'Italy',     'fr': 'France',  'nl': 'Netherlands'}

baseline_results = {}
for c in countries_all:
    vars_c = ['policy_rate', f'nim_{c}', f'cet1_{c}', 'credit_growth', 'gdp_growth', 'inflation']
    df_c   = df_model[vars_c].dropna()
    res, irf, se = run_var(df_c, country_labels[c])
    baseline_results[c] = {'vars': vars_c, 'df': df_c, 'results': res, 'irf': irf, 'stderr': se}

# ── BASELINE + BOND YIELD VARs: DE, ES, IT, FR, NL ──
yield_map = {'de': 'yield_de', 'es': 'yield_es', 'it': 'yield_it',
             'fr': 'yield_fr', 'nl': 'yield_nl'}
yield_results = {}
for c in ['de', 'es', 'it', 'fr', 'nl']:
    vars_c = ['policy_rate', f'nim_{c}', f'cet1_{c}', yield_map[c], 'credit_growth', 'gdp_growth', 'inflation']
    df_c   = df_model[vars_c].dropna()
    res, irf, se = run_var(df_c, f"{country_labels[c]} [+yield]")
    yield_results[c] = {'vars': vars_c, 'df': df_c, 'results': res, 'irf': irf, 'stderr': se}

# ── GRAFIK 2: IRF baseline - 6 ülke (3x4) ──
for group, group_countries, fname, title in [
    ('baseline_12', ['ea','de','es'], 'irf_results.png',    'Impulse Response Functions: Policy Rate Shock\nEuro Area, Germany, Spain'),
    ('baseline_34', ['it','fr','nl'], 'irf_results_2.png',  'Impulse Response Functions: Policy Rate Shock\nItaly, France, Netherlands'),
]:
    fig2, axes2 = plt.subplots(3, 4, figsize=(20, 12))
    fig2.suptitle(title, fontsize=14, fontweight='bold')
    for i, c in enumerate(group_countries):
        r    = baseline_results[c]
        irf  = r['irf']
        se   = r['stderr']
        vl   = r['vars']
        periods = range(21)
        for j, (vname, color, vlabel) in enumerate([
            (f'nim_{c}',      'blue',   'NIM Response'),
            (f'cet1_{c}',     'red',    'CET1 Response'),
            ('credit_growth', 'purple', 'Credit Growth Response'),
            ('gdp_growth',    'green',  'GDP Response'),
        ]):
            ax  = axes2[i, j]
            idx = vl.index(vname)
            val = irf.irfs[:, idx, 0]
            err = se[:, idx, 0]
            ax.plot(periods, val, color=color, linewidth=2)
            ax.fill_between(periods, val-err, val+err, alpha=0.2, color=color)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            ax.set_title(f'{country_labels[c]} - {vlabel}')
            ax.set_xlabel('Quarters')
    plt.tight_layout()
    plt.savefig(fname, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"{fname} kaydedildi!")

# ── GRAFIK 3: Country Comparison NIM - tüm ülkeler ──
fig3, (ax3, ax5) = plt.subplots(1, 2, figsize=(18, 6))
fig3.suptitle('Country Comparison: Response to Policy Rate Shock', fontsize=14, fontweight='bold')
periods = range(21)
styles = {'ea': ('k-', 'Euro Area'), 'de': ('b--', 'Germany'), 'es': ('r-.', 'Spain'),
          'it': ('g:',  'Italy'),    'fr': ('m-',  'France'),  'nl': ('c--', 'Netherlands')}
for c, (style, label) in styles.items():
    r   = baseline_results[c]
    nim_irf = r['irf'].irfs[:, r['vars'].index(f'nim_{c}'), 0]
    ax3.plot(periods, nim_irf, style, linewidth=2, label=label)
ax3.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax3.set_title('Net Interest Margin Response', fontsize=12, fontweight='bold')
ax3.set_xlabel('Quarters')
ax3.set_ylabel('Response')
ax3.legend()

for c, (style, label) in styles.items():
    r   = baseline_results[c]
    cr_irf = r['irf'].irfs[:, r['vars'].index('credit_growth'), 0]
    ax5.plot(periods, cr_irf, style, linewidth=2, label=label)
ax5.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax5.set_title('Credit Growth Response', fontsize=12, fontweight='bold')
ax5.set_xlabel('Quarters')
ax5.set_ylabel('Response')
ax5.legend()
plt.tight_layout()
plt.savefig('country_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("Country comparison grafiği kaydedildi!")

# ── GRAFIK 4: Bond Yield etkisi - NIM karşılaştırma ──
fig4, axes4 = plt.subplots(2, 3, figsize=(18, 10))
fig4.suptitle('NIM Response: Baseline vs With Government Bond Yield\nResponse to Policy Rate Shock',
              fontsize=13, fontweight='bold')
for i, c in enumerate(['de', 'es', 'it', 'fr', 'nl']):
    ax = axes4[i // 3, i % 3]
    # Baseline
    rb  = baseline_results[c]
    b_nim = rb['irf'].irfs[:, rb['vars'].index(f'nim_{c}'), 0]
    b_se  = rb['stderr'][:, rb['vars'].index(f'nim_{c}'), 0]
    ax.plot(periods, b_nim, 'b-',  linewidth=2, label='Baseline')
    ax.fill_between(periods, b_nim-b_se, b_nim+b_se, alpha=0.15, color='blue')
    # With yield
    ry  = yield_results[c]
    y_nim = ry['irf'].irfs[:, ry['vars'].index(f'nim_{c}'), 0]
    y_se  = ry['stderr'][:, ry['vars'].index(f'nim_{c}'), 0]
    ax.plot(periods, y_nim, 'r--', linewidth=2, label='+Bond Yield')
    ax.fill_between(periods, y_nim-y_se, y_nim+y_se, alpha=0.15, color='red')
    ax.axhline(y=0, color='k', linestyle=':', alpha=0.5)
    ax.set_title(f'{country_labels[c]}')
    ax.set_xlabel('Quarters')
    ax.legend(fontsize=9)
# Son panel boş
axes4[1, 2].axis('off')
plt.tight_layout()
plt.savefig('nim_yield_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("NIM yield comparison grafiği kaydedildi!")

# ── GRAFIK 5: Robustness - Shadow Rate ──
rob_results = {}
for c in countries_all:
    vars_c = ['shadow_rate', f'nim_{c}', f'cet1_{c}', 'credit_growth', 'gdp_growth', 'inflation']
    df_c   = df_model[vars_c].dropna()
    res, irf, se = run_var(df_c, f"{country_labels[c]} [SSR]")
    rob_results[c] = {'vars': vars_c, 'irf': irf, 'stderr': se}

fig5, axes5 = plt.subplots(3, 2, figsize=(16, 14))
fig5.suptitle('Robustness Check: Baseline (DFR) vs Shadow Rate (SSR)\nNIM and CET1 Response',
              fontsize=13, fontweight='bold')
for i, c in enumerate(['ea', 'de', 'es']):
    for j, vname in enumerate([f'nim_{c}', f'cet1_{c}']):
        ax = axes5[i, j]
        rb = baseline_results[c]
        rr = rob_results[c]
        b_val = rb['irf'].irfs[:, rb['vars'].index(vname), 0]
        b_se  = rb['stderr'][:, rb['vars'].index(vname), 0]
        r_val = rr['irf'].irfs[:, rr['vars'].index(vname), 0]
        r_se  = rr['stderr'][:, rr['vars'].index(vname), 0]
        ax.plot(periods, b_val, 'b-',  linewidth=2, label='Baseline (DFR)')
        ax.fill_between(periods, b_val-b_se, b_val+b_se, alpha=0.15, color='blue')
        ax.plot(periods, r_val, 'r--', linewidth=2, label='Robustness (SSR)')
        ax.fill_between(periods, r_val-r_se, r_val+r_se, alpha=0.15, color='red')
        ax.axhline(y=0, color='k', linestyle=':', alpha=0.5)
        vlabel = 'NIM' if 'nim' in vname else 'CET1'
        ax.set_title(f'{country_labels[c]} - {vlabel} Response')
        ax.set_xlabel('Quarters')
        ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('robustness_shadow_rate.png', dpi=300, bbox_inches='tight')
plt.show()
print("Robustness grafiği kaydedildi!")

print("\nTüm grafikler tamamlandı:")
print("timeseries.png, bond_yields.png, irf_results.png, irf_results_2.png,")
print("country_comparison.png, nim_yield_comparison.png, robustness_shadow_rate.png")
