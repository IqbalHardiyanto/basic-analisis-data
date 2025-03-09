# dashboard/dashboard.py
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
    # Baca data mentah
    raw_df = pd.read_csv('hour.csv')
    
    # Baca data gabungan untuk analisis lain
    combined_df = pd.read_csv('combined_data_bike.csv')
    
    return raw_df, combined_df

# Memuat data
raw_df, combined_df = load_data()

# Proses data untuk boxplot
def process_day_data(df):
    # Buat kolom kategori hari
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

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Pengaruh Cuaca", "Analisis Hari", "Tren Bulanan"])

with tab1:
    st.header("Pengaruh Kondisi Cuaca Terhadap Penyewaan")
    
    # Ambil data cuaca dari data gabungan
    weather_df = combined_df[combined_df['kategori'] == 'cuaca']
    
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
    
    # Insight
    st.markdown("""
    **🔍 Insight Cuaca:**
    - **Pengaruh Dominan:** Cuaca cerah (Clear) menyumbang **87.5%** dari total penyewaan 
      `(1.875.428 dari 2.147.662 sewa)`
    - **Penurunan Drastis:** Kondisi hujan/salju berat mengurangi penyewaan hingga **99.9%** 
      dibanding kondisi cerah `(215 vs 1.875.428 sewa)`
    - **Pola Jam Sibuk:** Pada cuaca cerah, penyewaan rata-rata/jam mencapai **164 sewa**, 
      3x lebih tinggi dari kondisi hujan ringan
    """)

with tab2:
    st.header("Perbandingan Penyewaan Hari Kerja vs Hari Libur")
    
    # Proses data mentah untuk boxplot
    processed_df = process_day_data(raw_df)
    
    # Membagi layout menjadi 2 kolom
    col1, col2 = st.columns(2)
    
    with col1:
        # Ambil data hari dari data gabungan
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
        # Gunakan data mentah untuk boxplot
        fig2b, ax2b = plt.subplots(figsize=(8, 4))
        sns.boxplot(
            data=processed_df,
            x='jenis_hari',
            y='registered',
            palette='viridis',
            showfliers=False,
            ax=ax2b,
            order=['Hari Kerja', 'Hari Libur', 'Weekend']
        )
        ax2b.set_title('Distribusi Sewa per Jam (Data Mentah)')
        ax2b.set_ylabel('Jumlah Sewa per Jam')
        ax2b.set_xlabel('Kategori Hari')
        st.pyplot(fig2b)
        
        # Insight
    st.markdown("""
    **🔍 Insight Hari:**
    - **Dominasi Hari Kerja:** Menyumbang **77.4%** total sewa `(1.989.125 sewa)` 
      dengan pola konsisten di jam 7-9 pagi dan 5-7 malam
    - **Variasi Weekend:** Distribusi sewa lebih merata di weekend dengan rentang 
      50-200 sewa/jam (lihat boxplot)
    - **Outlier Hari Libur:** Terdapat jam-jam tertentu di hari libur mencapai **600+ sewa**, 
      kemungkinan di lokasi wisata
    """)

with tab3:
    st.header("Tren Penyewaan Bulanan")
    
    # Ambil data bulanan dari data gabungan
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
    ax3.ticklabel_format(style='plain', axis='y')
    plt.xticks(rotation=45)
    st.pyplot(fig3)
    st.markdown("""
    **🔍 Insight Tren Bulanan:**
    - **Musim Puncak:** September menjadi bulan terbaik dengan **345.991 sewa** 
      (`+14.8%` dari Agustus)
    - **Dampak Musim Hujan:** Penurunan **39.2%** di Desember bertepatan dengan 
      peningkatan 144 hari hujan
    - **Pertumbuhan Signifikan:** 
      - April `(+51.3%)` - awal musim semi
      - Mei `(+23.3%)` - persiapan musim panas
    - **Korelasi Negatif:** 
      `r = -0.76` antara hari hujan dan jumlah sewa
    """)
