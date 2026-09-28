import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Real Estate Buyer Segmentation Dashboard",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Real Estate Buyer Segmentation & Investment Profiling")
st.markdown("Interactive dashboard for analyzing buyer demographics, total spend, and investment clusters.")

# -------------------------------------------------------------
# 2. DATA LOADING FUNCTION
# -------------------------------------------------------------
@st.cache_data
def load_data():
    # Dataset File Path (તમારી જરૂરિયાત મુજબ ફાઈલનું નામ બદલી શકો છો)
    try:
        df = pd.read_csv("real_estate_buyers.csv")
    except FileNotFoundError:
        # ફાઈલ ના મળે તો સેમ્પલ ડેમો ડેટા સેટ કરશે
        df = pd.DataFrame({
            'Age': [25, 34, 45, 52, 29, 41, 38, 60],
            'Total Spend': [150000, 320000, 450000, 800000, 210000, 500000, 380000, 950000],
            'region': ['North', 'South', 'East', 'West', 'North', 'East', 'South', 'West'],
            'client_type': ['Individual', 'Corporate', 'Individual', 'Investor', 'Individual', 'Corporate', 'Investor', 'Corporate']
        })
    
    # જો Age કોલમ ના હોય અને Date of Birth હોય તો Age ગણી લેવું
    if 'Age' not in df.columns and 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        df['Age'] = (pd.to_datetime('today') - df['date_of_birth']).dt.days // 365
        
    return df

try:
    df = load_data()

    # -------------------------------------------------------------
    # 3. SIDEBAR FILTERS (AGE & TOTAL SPEND INCLUDED)
    # -------------------------------------------------------------
    st.sidebar.header("🔍 User Filters")

    # A. Age Range Slider Filter
    min_age = int(df['Age'].min()) if 'Age' in df.columns else 18
    max_age = int(df['Age'].max()) if 'Age' in df.columns else 80
    selected_age = st.sidebar.slider(
        "🎂 Select Age Range",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )

    # B. Total Spend Range Slider Filter
    min_spend = float(df['Total Spend'].min()) if 'Total Spend' in df.columns else 10000.0
    max_spend = float(df['Total Spend'].max()) if 'Total Spend' in df.columns else 1000000.0
    selected_spend = st.sidebar.slider(
        "💰 Select Total Spend Range ($)",
        min_value=min_spend,
        max_value=max_spend,
        value=(min_spend, max_spend)
    )

    # C. Additional Region & Client Type Filters
    selected_regions = st.sidebar.multiselect(
        "📍 Select Region",
        options=df['region'].unique() if 'region' in df.columns else [],
        default=df['region'].unique() if 'region' in df.columns else []
    )

    selected_client_types = st.sidebar.multiselect(
        "👤 Select Client Type",
        options=df['client_type'].unique() if 'client_type' in df.columns else [],
        default=df['client_type'].unique() if 'client_type' in df.columns else []
    )

    # -------------------------------------------------------------
    # 4. FILTERING LOGIC
    # -------------------------------------------------------------
    filtered_df = df[
        (df['Age'] >= selected_age[0]) & (df['Age'] <= selected_age[1]) &
        (df['Total Spend'] >= selected_spend[0]) & (df['Total Spend'] <= selected_spend[1])
    ]

    if 'region' in df.columns and selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    if 'client_type' in df.columns and selected_client_types:
        filtered_df = filtered_df[filtered_df['client_type'].isin(selected_client_types)]

    # -------------------------------------------------------------
    # 5. DASHBOARD METRICS (KPIs)
    # -------------------------------------------------------------
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("👥 Total Buyers", f"{len(filtered_df):,}")
    col2.metric("🎂 Avg Age", f"{filtered_df['Age'].mean():.1f} Yrs" if 'Age' in filtered_df and len(filtered_df) > 0 else "N/A")
    col3.metric("💳 Avg Spend", f"${filtered_df['Total Spend'].mean():,.2f}" if 'Total Spend' in filtered_df and len(filtered_df) > 0 else "N/A")
    col4.metric("💵 Total Sales Volume", f"${filtered_df['Total Spend'].sum():,.2f}" if 'Total Spend' in filtered_df and len(filtered_df) > 0 else "N/A")

    st.markdown("---")

    # -------------------------------------------------------------
    # 6. VISUALIZATION TABS
    # -------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Buyer Analysis", "🗺️ Regional Insights", "📋 Data Inspector"])

    with tab1:
        st.subheader("Age vs. Total Spend Analysis")
        if 'Age' in filtered_df.columns and 'Total Spend' in filtered_df.columns and len(filtered_df) > 0:
            fig_scatter = px.scatter(
                filtered_df, 
                x='Age', 
                y='Total Spend', 
                color='client_type' if 'client_type' in filtered_df.columns else None,
                hover_data=['region'] if 'region' in filtered_df.columns else None,
                title="Buyer Segmentation: Age vs. Total Spend"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No data available for current selection.")

    with tab2:
        st.subheader("Regional Investment Breakdown")
        if 'region' in filtered_df.columns and 'Total Spend' in filtered_df.columns and len(filtered_df) > 0:
            region_summary = filtered_df.groupby('region')['Total Spend'].sum().reset_index()
            fig_region = px.bar(
                region_summary,
                x='region',
                y='Total Spend',
                color='region',
                title="Total Investment Volume per Region"
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.warning("No data available for current selection.")

    with tab3:
        st.subheader("Filtered Raw Dataset")
        st.dataframe(filtered_df)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
