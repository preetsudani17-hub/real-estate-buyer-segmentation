import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Parcl Real Estate Intelligence", layout="wide")

st.title(" Real Estate Market Intelligence Dashboard")
st.subheader("AI-Driven Buyer Segmentation & Investment Profiling")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("real_estate_buyer_segments.csv")

try:
    df = load_data()
except Exception:
    st.error("Dataset 'real_estate_buyer_segments.csv' not found!")
    st.stop()

# Sidebar Filters
st.sidebar.header("User Controls & Filters")
country_filter = st.sidebar.multiselect("Select Country", options=sorted(df['country'].dropna().unique()), default=sorted(df['country'].dropna().unique()))
region_filter = st.sidebar.multiselect("Select Region", options=sorted(df['region'].dropna().unique()), default=sorted(df['region'].dropna().unique()))
purpose_filter = st.sidebar.multiselect("Acquisition Purpose", options=sorted(df['acquisition_purpose'].dropna().unique()), default=sorted(df['acquisition_purpose'].dropna().unique()))
client_filter = st.sidebar.multiselect("Client Type", options=sorted(df['client_type'].dropna().unique()), default=sorted(df['client_type'].dropna().unique()))

# Filter Data
filtered_df = df[
    (df['country'].isin(country_filter)) &
    (df['region'].isin(region_filter)) &
    (df['acquisition_purpose'].isin(purpose_filter)) &
    (df['client_type'].isin(client_filter))
]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Buyer Segmentation Overview", 
    "Investor Behavior Dashboard", 
    "Geographic Buyer Analysis", 
    "Segment Insights Panel"
])

# Tab 1: Buyer Segmentation Overview
with tab1:
    st.header("Buyer Segmentation Overview")
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(filtered_df, names='Buyer_Segment', title='Cluster Distribution', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_bar = px.bar(filtered_df, x='Buyer_Segment', color='client_type', barmode='group', title='Buyer Segment by Client Type')
        st.plotly_chart(fig_bar, use_container_width=True)

# Tab 2: Investor Behavior Dashboard
with tab2:
    st.header("Investor Behavior Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        fig_box = px.box(filtered_df, x='Buyer_Segment', y='age', color='loan_applied', title='Age Distribution & Loan Status')
        st.plotly_chart(fig_box, use_container_width=True)
    with col2:
        fig_scat = px.scatter(filtered_df, x='total_spent', y='satisfaction_score', color='Buyer_Segment', title='Total Spent vs Satisfaction')
        st.plotly_chart(fig_scat, use_container_width=True)

# Tab 3: Geographic Buyer Analysis
with tab3:
    st.header("Geographic Buyer Analysis")
    fig_geo = px.histogram(filtered_df, x='region', color='Buyer_Segment', barmode='group', title='Buyer Segments by Region')
    st.plotly_chart(fig_geo, use_container_width=True)

# Tab 4: Segment Insights Panel
with tab4:
    st.header("Segment Insights Panel")
    st.subheader("Cluster Average Metrics")
    st.dataframe(filtered_df.groupby('Buyer_Segment')[['age', 'satisfaction_score', 'total_spent', 'property_count']].mean())
