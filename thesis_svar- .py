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

axes1[0, 1].plot(df.index, df['nim_ea'], 'k-', linewidth=2, label='Euro Area')
axes1[0, 1].plot(df.index, df['nim_de'], 'b--', linewidth=2, label='Germany')
axes1[0, 1].plot(df.index, df['nim_es'], 'r-.', linewidth=2, label='Spain')
axes1[0, 1].set_title('Net Interest Margin (%)')
axes1[0, 1].legend()
axes1[0, 1].set_xlabel('Date')

axes1[1, 0].plot(df.index, df['cet1_ea'], 'k-', linewidth=2, label='Euro Area')
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

# ── Stationarity Transformations ──
# ADF test sonuçlarına göre (consistent across countries):
#
# LEVELS (stationary in levels):
#   - policy_rate: stationary with trend (p=0.019)
#   - gdp_growth:  stationary (p=0.000)
#   - nim_ea/de/es: stationary (p<0.05)
#
# FIRST DIFFERENCE (I(1)):
#   - inflation:    borderline, accepted at 10% after differencing
#   - credit_growth: p=0.000 after diff
#   - cet1_ea/de/es: p<0.05 after diff (cet1_es borderline, accepted at 10%)
#   - shadow_rate:  p=0.002 after diff
#
# All transformations applied consistently across EA, DE, ES.

df_model = df.copy()

# First difference variables
diff_vars = ['inflation', 'credit_growth', 'cet1_ea', 'cet1_de', 'cet1_es',
             'shadow_rate']
for var in diff_vars:
    df_model[var] = df[var].diff()

# Levels variables (no transformation needed):
# policy_rate, gdp_growth, nim_ea, nim_de, nim_es

df_model = df_model.dropna()

# ── Stationarity Check (after transformations) ──
print("=== ADF Test Results (post-transformation) ===")
check_vars = ['policy_rate', 'inflation', 'gdp_growth', 'credit_growth',
              'nim_ea', 'nim_de', 'nim_es',
              'cet1_ea', 'cet1_de', 'cet1_es', 'shadow_rate']
for col in check_vars:
    result = adfuller(df_model[col].dropna())
    star = '✓' if result[1] < 0.05 else ('~ (10%)' if result[1] < 0.10 else '✗')
    print(f"{col}: ADF={result[0]:.3f}, p={result[1]:.3f} {star}")

# ── VAR ──
def run_var(df_vars, label):
    model = VAR(df_vars)
    results = model.fit(maxlags=2, ic='aic')
    print(f"{label} - Optimal lag: {results.k_ar}")
    irf    = results.irf(20)
    stderr = results.irf(20).stderr(orth=False)
    return results, irf, stderr

# ── BASELINE: ECB Deposit Facility Rate ──
ea_vars = ['policy_rate', 'nim_ea', 'cet1_ea', 'credit_growth', 'gdp_growth', 'inflation']
df_ea   = df_model[ea_vars].dropna()
results_ea, irf_ea, stderr_ea = run_var(df_ea, "Euro Area")

de_vars = ['policy_rate', 'nim_de', 'cet1_de', 'credit_growth', 'gdp_growth', 'inflation']
df_de   = df_model[de_vars].dropna()
results_de, irf_de, stderr_de = run_var(df_de, "Germany")

es_vars = ['policy_rate', 'nim_es', 'cet1_es', 'credit_growth', 'gdp_growth', 'inflation']
df_es   = df_model[es_vars].dropna()
results_es, irf_es, stderr_es = run_var(df_es, "Spain")

# ── GRAFIK 2: IRF 3x4 ──
fig2, axes2 = plt.subplots(3, 4, figsize=(20, 12))
fig2.suptitle('Impulse Response Functions: Policy Rate Shock', fontsize=14, fontweight='bold')

countries  = ['Euro Area', 'Germany', 'Spain']
irfs       = [irf_ea,    irf_de,    irf_es]
stderrs    = [stderr_ea, stderr_de, stderr_es]
var_lists  = [ea_vars,   de_vars,   es_vars]

for i, (country, irf, stderr, var_list) in enumerate(zip(countries, irfs, stderrs, var_lists)):
    periods  = range(21)
    irf_data = irf.irfs

    nim_idx   = var_list.index([v for v in var_list if 'nim'  in v][0])
    cet1_idx  = var_list.index([v for v in var_list if 'cet1' in v][0])
    credit_idx = var_list.index('credit_growth')
    gdp_idx   = var_list.index('gdp_growth')

    for j, (idx, color, label) in enumerate([
        (nim_idx,    'blue',   'NIM Response'),
        (cet1_idx,   'red',    'CET1 Response'),
        (credit_idx, 'purple', 'Credit Growth Response'),
        (gdp_idx,    'green',  'GDP Response'),
    ]):
        ax  = axes2[i, j]
        val = irf_data[:, idx, 0]
        se  = stderr[:, idx, 0]
        ax.plot(periods, val, color=color, linewidth=2)
        ax.fill_between(periods, val - se, val + se, alpha=0.2, color=color)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax.set_title(f'{country} - {label}')
        ax.set_xlabel('Quarters')

plt.tight_layout()
plt.savefig('irf_results.png', dpi=300, bbox_inches='tight')
plt.show()
print("IRF grafiği kaydedildi!")

# ── GRAFIK 3: Country Comparison ──
fig3, (ax3, ax5) = plt.subplots(1, 2, figsize=(18, 6))
fig3.suptitle('Country Comparison: Response to Policy Rate Shock', fontsize=14, fontweight='bold')

periods = range(21)

nim_ea_irf = irf_ea.irfs[:, ea_vars.index('nim_ea'), 0]
nim_de_irf = irf_de.irfs[:, de_vars.index('nim_de'), 0]
nim_es_irf = irf_es.irfs[:, es_vars.index('nim_es'), 0]

ax3.plot(periods, nim_ea_irf, 'k-',  linewidth=2, label='Euro Area')
ax3.plot(periods, nim_de_irf, 'b--', linewidth=2, label='Germany')
ax3.plot(periods, nim_es_irf, 'r-.', linewidth=2, label='Spain')
ax3.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax3.set_title('Net Interest Margin Response', fontsize=12, fontweight='bold')
ax3.set_xlabel('Quarters')
ax3.set_ylabel('Response')
ax3.legend()

credit_ea_irf = irf_ea.irfs[:, ea_vars.index('credit_growth'), 0]
credit_de_irf = irf_de.irfs[:, de_vars.index('credit_growth'), 0]
credit_es_irf = irf_es.irfs[:, es_vars.index('credit_growth'), 0]

ax5.plot(periods, credit_ea_irf, 'k-',  linewidth=2, label='Euro Area')
ax5.plot(periods, credit_de_irf, 'b--', linewidth=2, label='Germany')
ax5.plot(periods, credit_es_irf, 'r-.', linewidth=2, label='Spain')
ax5.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax5.set_title('Credit Growth Response', fontsize=12, fontweight='bold')
ax5.set_xlabel('Quarters')
ax5.set_ylabel('Response')
ax5.legend()

plt.tight_layout()
plt.savefig('country_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("Country comparison grafiği kaydedildi!")

# ── ROBUSTNESS: Shadow Short Rate (Krippner SSR) ──
ea_vars_rob = ['shadow_rate', 'nim_ea', 'cet1_ea', 'credit_growth', 'gdp_growth', 'inflation']
df_ea_rob   = df_model[ea_vars_rob].dropna()
results_ea_rob, irf_ea_rob, stderr_ea_rob = run_var(df_ea_rob, "Euro Area [SSR]")

de_vars_rob = ['shadow_rate', 'nim_de', 'cet1_de', 'credit_growth', 'gdp_growth', 'inflation']
df_de_rob   = df_model[de_vars_rob].dropna()
results_de_rob, irf_de_rob, stderr_de_rob = run_var(df_de_rob, "Germany [SSR]")

es_vars_rob = ['shadow_rate', 'nim_es', 'cet1_es', 'credit_growth', 'gdp_growth', 'inflation']
df_es_rob   = df_model[es_vars_rob].dropna()
results_es_rob, irf_es_rob, stderr_es_rob = run_var(df_es_rob, "Spain [SSR]")

# ── GRAFIK 4: Robustness ──
fig4, axes4 = plt.subplots(3, 2, figsize=(16, 14))
fig4.suptitle('Robustness Check: Baseline (DFR) vs Shadow Rate (SSR)\nNIM and CET1 Response to Policy Rate Shock',
              fontsize=13, fontweight='bold')

nim_names  = ['nim_ea',  'nim_de',  'nim_es']
cet1_names = ['cet1_ea', 'cet1_de', 'cet1_es']
baseline_irfs = [irf_ea,        irf_de,        irf_es]
baseline_se   = [stderr_ea,     stderr_de,     stderr_es]
baseline_vars = [ea_vars,       de_vars,       es_vars]
rob_irfs      = [irf_ea_rob,    irf_de_rob,    irf_es_rob]
rob_se        = [stderr_ea_rob, stderr_de_rob, stderr_es_rob]
rob_vars      = [ea_vars_rob,   de_vars_rob,   es_vars_rob]

for i, country in enumerate(countries):
    nim_name  = nim_names[i]
    cet1_name = cet1_names[i]

    for j, (name, ax) in enumerate([(nim_name, axes4[i,0]), (cet1_name, axes4[i,1])]):
        b_val = baseline_irfs[i].irfs[:, baseline_vars[i].index(name), 0]
        b_se  = baseline_se[i][:,   baseline_vars[i].index(name), 0]
        r_val = rob_irfs[i].irfs[:,  rob_vars[i].index(name), 0]
        r_se  = rob_se[i][:,         rob_vars[i].index(name), 0]

        ax.plot(periods, b_val, 'b-',  linewidth=2, label='Baseline (DFR)')
        ax.fill_between(periods, b_val - b_se, b_val + b_se, alpha=0.15, color='blue')
        ax.plot(periods, r_val, 'r--', linewidth=2, label='Robustness (SSR)')
        ax.fill_between(periods, r_val - r_se, r_val + r_se, alpha=0.15, color='red')
        ax.axhline(y=0, color='k', linestyle=':', alpha=0.5)
        label_str = 'NIM' if 'nim' in name else 'CET1'
        ax.set_title(f'{country} - {label_str} Response')
        ax.set_xlabel('Quarters')
        ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig('robustness_shadow_rate.png', dpi=300, bbox_inches='tight')
plt.show()
print("Robustness grafiği kaydedildi!")
print("\nTüm grafikler tamamlandı: timeseries.png, irf_results.png, country_comparison.png, robustness_shadow_rate.png")
