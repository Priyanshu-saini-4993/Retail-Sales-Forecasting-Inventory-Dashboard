from sklearn.ensemble import RandomForestRegressor

def train_model(df):
    X = df[['day','month','weekday','price']]
    y = df['sales']

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)

    return model

def predict(model, df):
    X = df[['day','month','weekday','price']]
    df['predicted_sales'] = model.predict(X)
    return df