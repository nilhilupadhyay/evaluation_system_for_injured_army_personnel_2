import pandas as pd
import numpy as np

# Define the data generation parameters
n = 1000

# Generate random data based on the patterns observed
data = {
    'Bullet Velocity (m/s)': np.round(np.random.uniform(300, 425, n), 1),
    'Human Body Mass (kg)': np.round(np.random.uniform(55, 87, n), 1),
    'Kinetic Energy (J)': np.round(np.random.uniform(348, 631, n), 1),
    'Temperature Rise (°C)': np.round(np.random.uniform(0.001, 0.0022, n), 4),
    'Blood Loss (ml)': np.random.randint(100, 1301, n),
    'ECG Readings': np.random.choice(['Normal', 'Abnormal'], n),
    'Health Status': np.random.choice(['Healthy', 'Injured', 'Critical'], n),
    'Latitude': np.random.choice([28.6139, 28.7041, 19.076, 12.9716, 13.0827, 22.5726, 19.2183, 26.9124, 22.7196, 11.0168, 23.0225, 25.3176, 28.4089, 28.6517, 28.5355, 28.4798], n),
    'Longitude': np.random.choice([77.209, 77.1025, 72.8777, 77.5946, 80.2707, 88.3639, 72.9781, 75.7873, 75.8577, 76.9558, 72.5714, 82.9739, 77.3178, 77.2219, 77.391, 77.226], n),
    'Diagnosis Result': np.random.choice(['Healthy', 'Injured', 'Critical'], n)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('generated_dataset.csv', index=False)
