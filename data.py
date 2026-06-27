import pandas as pd
df = pd.read_csv('thesis_data.csv', index_col='date', parse_dates=True)
print("Her değişkenin son tarihi:")
for col in df.columns:
    last = df[col].dropna().index[-1]
    print(f"{col}: {last}")