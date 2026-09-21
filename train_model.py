import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib

print("Data cleaning & Model training starting...")

# 1. Load Data
df_clients = pd.read_csv('clients.csv')
df_properties = pd.read_csv('properties.csv')

# 2. Data Cleaning & Aggregation
df_properties['sale_price_clean'] = (
    df_properties['sale_price']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .astype(float)
)

prop_agg = df_properties.groupby('client_ref').agg(
    total_spent=('sale_price_clean', 'sum'),
    property_count=('listing_id', 'count')
).reset_index()

df = pd.merge(df_clients, prop_agg, left_on='client_id', right_on='client_ref', how='left')
df['total_spent'] = df['total_spent'].fillna(0)
df['property_count'] = df['property_count'].fillna(0)

# Calculate Age
df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], format='mixed')
df['age'] = 2026 - df['date_of_birth'].dt.year

# 3. Encoding & Scaling
cat_features = ['client_type', 'region', 'acquisition_purpose', 'referral_channel', 'country']
num_features = ['age', 'satisfaction_score', 'total_spent', 'property_count']

df_encoded = pd.get_dummies(df, columns=cat_features, drop_first=True)
scaler = StandardScaler()
scaled_num = scaler.fit_transform(df[num_features])
df_scaled_num = pd.DataFrame(scaled_num, columns=num_features)

drop_cols = ['client_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'loan_applied', 'client_ref']
model_df = pd.concat([df_scaled_num, df_encoded.drop(columns=drop_cols)], axis=1)

# 4. Clustering Model
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['Cluster_ID'] = kmeans.fit_predict(model_df)

segment_map = {
    0: 'Global Investors',
    1: 'First-Time Buyers',
    2: 'Corporate Buyers',
    3: 'Luxury Investors'
}
df['Buyer_Segment'] = df['Cluster_ID'].map(segment_map)

# 5. Save Processed Data
df.to_csv('real_estate_buyer_segments.csv', index=False)
print(" Step 1 Complete: Dataset cleaned and 'real_estate_buyer_segments.csv' saved successfully!")