import pandas as pd

# SSR verisini oku
df_ssr = pd.read_excel('SSR_Estimates_20260602.xlsx', 
                        sheet_name='D. Monthly average SSR series', 
                        header=None,
                        skiprows=19)

# İlk iki kolon: tarih ve Euro Area SSR
df_ssr = df_ssr.iloc[:, [0, 2]].copy()
df_ssr.columns = ['date', 'shadow_rate']
df_ssr = df_ssr.dropna()

# Tarihleri düzelt - Lehçe format
df_ssr['date'] = pd.to_datetime(df_ssr['date'], dayfirst=True, errors='coerce')
df_ssr = df_ssr.dropna()
df_ssr = df_ssr.set_index('date')

# Monthly to quarterly
df_ssr_q = df_ssr.resample('QS').mean()
df_ssr_q.columns = ['shadow_rate']

print(df_ssr_q.head(10))
print(df_ssr_q.tail(10))
print(df_ssr_q.shape)