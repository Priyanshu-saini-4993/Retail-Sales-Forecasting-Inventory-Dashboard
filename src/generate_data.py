import pandas as pd
import numpy as np

np.random.seed(42)

products = [
    ("iPhone 14", "Electronics", 80000),
    ("Samsung TV", "Electronics", 50000),
    ("Nike Shoes", "Fashion", 5000),
    ("Levi Jeans", "Fashion", 3000),
    ("Milk 1L", "Grocery", 60),
    ("Bread", "Grocery", 40),
    ("Washing Machine", "Appliances", 25000),
    ("Laptop HP", "Electronics", 60000)
]

stores = ["Delhi Store", "Mumbai Store", "Chandigarh Store"]

dates = pd.date_range(start="2022-01-01", periods=365*2)

data = []

for date in dates:
    for name, category, price in products:
        for store in stores:

            base = np.random.randint(10, 50)
            seasonal = 20 if date.month in [10,11,12] else 0
            weekend = 10 if date.weekday() >= 5 else 0
            noise = np.random.randint(-5,5)

            sales = max(base + seasonal + weekend + noise, 0)
            revenue = sales * price

            data.append([date, name, category, store, price, sales, revenue])

df = pd.DataFrame(data, columns=[
    "date","product","category","store","price","sales","revenue"
])

df.to_csv("data/sales_data.csv", index=False)

print("Dataset created:", df.shape)