import pandas as pd

for c in ['de', 'es', 'it', 'fr', 'nl']:
    df = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)
    print(f"\n=== {c.upper()} ===")
    print(df.isnull().sum())
    print(f"Clean rows (no NaN): {df.dropna().shape[0]}")
