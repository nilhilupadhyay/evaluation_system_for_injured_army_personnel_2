import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os


db_path = os.path.join('instance', 'projectdata.db')
DATABASE_URI = f'sqlite:///{db_path}'


engine = create_engine(DATABASE_URI)

try:
    
    query = "SELECT * FROM impact_health"
    df = pd.read_sql(query, engine)
    
    
    if df.empty:
        raise ValueError("The query did not return any results. Please check the table name and data.")
    
    
    df['ecg_readings'] = df['ecg_readings'].apply(lambda x: 0 if x == 'Abnormal' else 1)
    df['diagnosis_result'] = df['diagnosis_result'].apply(lambda x: 0 if x == 'Healthy' else (1 if x == 'Injured' else 2))

    
    X = df.drop(columns=['health_status', 'id', 'latitude', 'longitude','diagnosis_result'])  
    y = df['diagnosis_result']

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    
    neigh = KNeighborsClassifier(n_neighbors=3)
    neigh.fit(X_train, y_train)

    
    joblib.dump(neigh, 'knn_model.joblib')
    print("Model trained and saved successfully.")
    
except Exception as e:
    print(f"An error occurred: {e}")
