import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi tampilan
st.set_page_config(page_title="Dashboard", page_icon="🚲", layout="wide")
sns.set_style('whitegrid')

st.title("Analisis Penyewaan Sepeda 🚵")
st.markdown("Menganalisis bagaimana cuaca, waktu, dan hari libur memengaruhi penyewaan sepeda.")

# Fungsi pembaca data
@st.cache_data
def load_data():
    raw_df = pd.read_csv('hour.csv')
    combined_df = pd.read_csv('combined_data_bike.csv')
    return raw_df, combined_df

raw_df, combined_df = load_data()

# Proses data untuk boxplot
def process_day_data(df):
    df['jenis_hari'] = df.apply(lambda x: 
        'Hari Kerja' if x['workingday'] == 1 else
        'Hari Libur' if x['holiday'] == 1 else 
        'Weekend', axis=1)
    return df

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485965120184-e220f721d03e")
    st.title("Tentang")
    st.markdown(""" 
                **Analisis Penyewaan Sepeda** 
                - Dataset: hour.csv dan combined_data_bike.csv
                - Penulis: Muh. Iqbal Hardiyanto """)
    
    # ================= FITUR INTERAKTIF =================
    st.header("🛠️ Filter Data")
    
    # Filter 1: Cuaca dan Total Sewa
    cuaca_data = combined_df[combined_df['kategori'] == 'cuaca']
    weather_labels = cuaca_data['weather_label'].unique()
    selected_weather = st.multiselect(
        "Pilih Kondisi Cuaca",
        options=weather_labels,
        default=weather_labels
    )
    
    total_range = st.slider(
        "Rentang Total Sewa (juta)",
        min_value=float(cuaca_data['total'].min()),
        max_value=float(cuaca_data['total'].max()),
        value=(float(cuaca_data['total'].min()), float(cuaca_data['total'].max()))
    )
    
    # Filter 2: Sewa per Jam
    cnt_range = st.slider(
        "Rentang Sewa per Jam",
        min_value=int(raw_df['cnt'].min()),
        max_value=int(raw_df['cnt'].max()),
        value=(int(raw_df['cnt'].min()), int(raw_df['cnt'].max()))
    )
    
    # Fitur Pencarian
    st.header("🔍 Pencarian")
    if st.button("Cari Sewa Tertinggi"):
        max_row = raw_df.loc[raw_df['cnt'].idxmax()]
        st.success(f"**Rekor Tertinggi:** {max_row['cnt']} sewa pada {max_row['dteday']} jam {max_row['hr']}")

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Pengaruh Cuaca", "Analisis Hari", "Tren Bulanan"])

with tab1:
    st.header("Pengaruh Kondisi Cuaca Terhadap Penyewaan")
    
    # Terapkan filter cuaca
    weather_df = combined_df[
        (combined_df['kategori'] == 'cuaca') &
        (combined_df['weather_label'].isin(selected_weather)) &
        (combined_df['total'].between(total_range[0], total_range[1]))
    ]
    
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=weather_df, 
        x='weather_label', 
        y='total',
        palette='coolwarm',
        ax=ax1
    )
    ax1.set_title('Total Penyewaan berdasarkan Kondisi Cuaca', fontsize=14)
    ax1.set_xlabel('Kondisi Cuaca')
    ax1.set_ylabel('Total Sewa (juta)')
    ax1.ticklabel_format(style='plain', axis='y')
    st.pyplot(fig1)
    
    # Insight (disesuaikan dengan filter)
    if not weather_df.empty:
        dominant_weather = weather_df['weather_label'].mode()[0]
        average_total = weather_df['total'].mean()
    else:
        dominant_weather = "Tidak ada data"
        average_total = 0
    
    st.markdown(f"""
    **🔍 Insight Cuaca:**
    - **Total Data Terseleksi:** {len(weather_df)} kondisi cuaca
    - **Rentang Sewa:** {total_range[0]:.1f} - {total_range[1]:.1f} juta sewa
    - **Pola Terfilter:** Cuaca {dominant_weather} dominan dengan rata-rata {average_total:.1f} juta sewa
    """)

with tab2:
    st.header("Perbandingan Penyewaan Hari Kerja vs Hari Libur")
    
    # Terapkan filter jam
    processed_df = process_day_data(raw_df)
    processed_df = processed_df[processed_df['cnt'].between(cnt_range[0], cnt_range[1])]
    
    col1, col2 = st.columns(2)
    
    with col1:
        day_df = combined_df[combined_df['kategori'] == 'hari']
        clean_day_df = day_df[~day_df['jenis_hari'].isna()]
        
        fig2a, ax2a = plt.subplots(figsize=(8, 4))
        sns.barplot(
            data=clean_day_df,
            x='jenis_hari',
            y='total',
            palette='viridis',
            ax=ax2a
        )
        ax2a.set_title('Total Penyewaan per Kategori Hari')
        ax2a.set_ylabel('Total Sewa (juta)')
        st.pyplot(fig2a)
    
    with col2:
        fig2b, ax2b = plt.subplots(figsize=(8, 4))
        sns.boxplot(
            data=processed_df,
            x='jenis_hari',
            y='cnt',
            palette='viridis',
            showfliers=False,
            ax=ax2b,
            order=['Hari Kerja', 'Hari Libur', 'Weekend']
        )
        ax2b.set_title(f'Distribusi Sewa per Jam ({cnt_range[0]}-{cnt_range[1]} sewa/jam)')
        ax2b.set_ylabel('Jumlah Sewa per Jam')
        ax2b.set_xlabel('Kategori Hari')
        st.pyplot(fig2b)

with tab3:
    # Tetap tampilkan tren bulanan tanpa filter
    st.header("Tren Penyewaan Bulanan")
    monthly_df = combined_df[combined_df['kategori'] == 'bulan']
    monthly_clean = monthly_df.sort_values('mnth').dropna(subset=['bulan'])
    
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=monthly_clean,
        x='bulan',
        y='total',
        marker='o',
        color='green',
        label='Total Sewa'
    )
    ax3.set_title('Tren Penyewaan Sepeda Sepanjang Tahun', fontsize=14)
    ax3.set_xlabel('Bulan')
    ax3.set_ylabel('Total Sewa (juta)')
    plt.xticks(rotation=45)
    st.pyplot(fig3)