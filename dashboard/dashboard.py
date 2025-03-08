import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set page config
st.set_page_config(
    page_title="Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Load the merged data
@st.cache_data
def load_data():
    df = pd.read_csv('bike_sharing_analysis_results.csv')
    return df

df = load_data()

# Title
st.title("Bike Sharing Demand Analysis 🚴♂️")
st.markdown("Analyzing how weather, time, and holidays impact bike rentals.")

# --------------------------
# Section 1: Weather Impact
# --------------------------
st.header("1. Weather Conditions & Rentals")
tab1, tab2, tab3 = st.tabs(["Weather Situation", "Temperature/Humidity", "Wind Speed"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='weathersit', y='registered', data=df, ax=ax, palette="Blues", showfliers=False)
    ax.set_title("Registered Rentals by Weather Condition")
    ax.set_xlabel("Weather")
    ax.set_ylabel("Registered Users")
    st.pyplot(fig)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots()
        sns.scatterplot(x='temp_actual', y='registered', data=df, ax=ax1, color='red')
        ax1.set_title("Temperature vs Rentals")
        st.pyplot(fig1)
    with col2:
        fig2, ax2 = plt.subplots()
        sns.scatterplot(x='hum_actual', y='registered', data=df, ax=ax2, color='green')
        ax2.set_title("Humidity vs Rentals")
        st.pyplot(fig2)

with tab3:
    fig, ax = plt.subplots()
    sns.scatterplot(x='windspeed_actual', y='registered', data=df, ax=ax, color='blue')
    ax.set_title("Wind Speed vs Rentals")
    st.pyplot(fig)

# --------------------------
# Section 2: Temporal Patterns
# --------------------------
st.header("2. Time-Based Patterns")
tab4, tab5 = st.tabs(["Seasonal Trends", "Hourly Clusters"])

with tab4:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        x='hr', 
        y='registered', 
        hue='season', 
        data=df, 
        ax=ax, 
        palette='viridis', 
        estimator='mean'
    )
    ax.set_title("Hourly Rentals by Season")
    st.pyplot(fig)

with tab5:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='time_cluster', 
        y='registered', 
        data=df, 
        ax=ax, 
        palette='Set2', 
        estimator='mean'
    )
    ax.set_title("Average Rentals by Time Cluster")
    st.pyplot(fig)

# --------------------------
# Section 3: Holiday/Weekend Analysis
# --------------------------
st.header("3. Holiday & Weekend Trends")
holiday_type = st.radio("Select Day Type:", ["Holiday", "Weekend"])

if holiday_type == "Holiday":
    filtered_df = df[df['holiday'] == 1]
else:
    filtered_df = df[df['workingday'] == 0]

fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(
    x='hr', 
    y='registered', 
    data=filtered_df, 
    ax=ax, 
    color='purple', 
    estimator='mean'
)
ax.set_title(f"Hourly Rentals on {holiday_type}s")
st.pyplot(fig)


# --------------------------
# Section 4: Advanced Analysis (NEW)
# --------------------------
st.header("4. Advanced Analysis")
tab6, tab7 = st.tabs(["Multivariate Correlation", "Weather-Time Clusters"])

with tab6:
    st.subheader("Multivariate Impact on Rentals")
    selected_vars = st.multiselect(
        "Select variables to correlate with rentals:",
        options=['temp_actual', 'hum_actual', 'windspeed_actual', 'hr'],
        default=['temp_actual', 'hr']
    )
    
    if selected_vars:
        corr_matrix = df[selected_vars + ['registered']].corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr_matrix, annot=True, cmap="icefire", ax=ax)
        ax.set_title("Correlation Matrix: Selected Variables vs Rentals")
        st.pyplot(fig)
    else:
        st.warning("Please select at least one variable.")

with tab7:
    st.subheader("Optimal Weather-Time Clusters")
    
    # Define optimal thresholds
    temp_threshold = st.slider("Temperature Threshold (°C)", 10, 30, 20)
    wind_threshold = st.slider("Wind Speed Threshold (km/h)", 10, 40, 25)
    
    # Create clusters
    df['optimal_cluster'] = np.where(
        (df['temp_actual'] >= temp_threshold) & 
        (df['windspeed_actual'] <= wind_threshold),
        "Optimal",
        "Suboptimal"
    )
    
    # Plot cluster comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='time_cluster',
        y='registered',
        hue='optimal_cluster',
        data=df,
        palette="viridis",
        estimator=np.mean,
        ax=ax
    )
    ax.set_title(f"Rentals in Optimal vs Suboptimal Conditions (Temp ≥{temp_threshold}°C, Wind ≤{wind_threshold}km/h)")
    st.pyplot(fig)

# --------------------------
# Raw Data Preview (Optional)
# --------------------------
with st.expander("View Raw Data"):
    st.dataframe(df)

# --------------------------
# Key Insights Summary
# --------------------------
st.header("Key Insights")
st.markdown("""
- Cuaca Optimal: 20-25°C, langit cerah, kelembapan <80%.
- Jam Puncak: Pukul 8 pagi dan 5 - 6 sore pada hari kerja.
- Hari Libur: Penyewaan 15% lebih rendah secara keseluruhan, tetapi wahana rekreasi mencapai puncaknya pada pukul 12-3 siang.
- Kondisi Terburuk: Hujan lebat/salju mengurangi penyewaan hingga 50%.
""")