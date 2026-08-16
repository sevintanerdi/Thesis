import pandas as pd

df = pd.read_csv('thesis_data_de.csv', index_col='date', parse_dates=True)
complete = df.dropna()
print(f"First complete observation: {complete.index[0].date()}")
print(f"Last complete observation: {complete.index[-1].date()}")
