import pandas as pd

for c in ['de', 'es', 'it', 'fr', 'nl']:
    df = pd.read_csv(f'thesis_data_{c}.csv', index_col='date', parse_dates=True)
    print(f"\n{c.upper()}:")
    print(f"  Raw rows: {len(df)}")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"  Complete rows (no NaN): {df.dropna().shape[0]}")
