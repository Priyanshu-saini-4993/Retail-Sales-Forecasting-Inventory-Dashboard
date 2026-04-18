def calculate_inventory(df):
    results = []

    grouped = df.groupby(['product', 'store'])

    for (product, store), group in grouped:

        if 'predicted_sales' not in group.columns:
            continue

        avg = group['predicted_sales'].mean()

        lead_time = 7
        safety_stock = avg * 2
        reorder_point = avg * lead_time + safety_stock

        status = "OK"
        if avg < 20:
            status = "Low Demand"
        elif avg > 60:
            status = "High Demand"

        results.append({
            "product": product,
            "store": store,
            "avg_demand": round(avg, 2),
            "reorder_point": round(reorder_point, 2),
            "status": status
        })

    return results