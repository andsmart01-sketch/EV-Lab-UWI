import pandas as pd
from pathlib import Path

xlsx = Path("data/raw/Fuel_Prices_Sorted_Fixed.xlsx")
df = pd.read_excel(xlsx)
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print("\nFirst 3 rows:")
print(df.head(3).to_string())
print("\nLast 3 rows:")
print(df.tail(3).to_string())
print("\nDtypes:")
print(df.dtypes)
